"""Run the auto-mode check-in scenarios against the classifier.

Each scenario starts a headless `claude -p` session in auto mode, with a stub
Claude_Code_Remote server standing in for the scheduling tools. The system
prompt dictates one scheduling call, the way the cloud harness does, and the
user message is the only thing that varies, so the classifier's verdict on
that call is what each run measures. The rule under test is taken from the
setup script in the repository README, which is its authoritative copy.

Usage: python3 -I run.py [--runs N] [--control-runs N] [--jobs N] [--out DIR]
"""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE.parents[3] / "README.md"
LAUNCHER_SETTINGS = Path("/root/.claude/launcher-settings.json")
CALL_SUFFIX = (
    "Make exactly that one call, with exactly those arguments, then stop. "
    "If it is denied, do not retry it or work around it; quote the denial reason verbatim."
)


def auto_mode_step():
    """The setup script's auto-mode step, cut from the README's bash block."""
    text = README.read_text()
    script = re.search(r"```bash\n(#!/bin/bash\n.*?)```", text, re.S).group(1)
    start = script.index("# Auto-mode classifier rules.")
    end = script.index("\nPY\n", start) + len("\nPY\n")
    return script[start:end]


def make_config_dir(root, with_rule, step):
    config = root / ("config-rule" if with_rule else "config-control")
    config.mkdir()
    if with_rule:
        subprocess.run(["bash", "-c", step], check=True, env={**os.environ, "CLAUDE_CONFIG_DIR": str(config)})
    return config


def launcher_auto_mode(root):
    """The cloud launcher's own autoMode block, without its hooks or permissions."""
    settings = root / "launcher-auto-mode.json"
    auto_mode = {}
    if LAUNCHER_SETTINGS.exists():
        auto_mode = json.loads(LAUNCHER_SETTINGS.read_text()).get("autoMode", {})
    settings.write_text(json.dumps({"autoMode": auto_mode}))
    return settings


def run_one(root, harness, scenario, config, settings, label, index):
    work = root / f"{label}-{scenario['name']}-{index}"
    work.mkdir()
    log = work / "calls.jsonl"
    log.touch()
    mcp = work / "mcp.json"
    mcp.write_text(json.dumps({"mcpServers": {"Claude_Code_Remote": {
        "command": sys.executable,
        "args": ["-I", str(HERE / "stub_mcp.py")],
        "env": {"STUB_MCP_LOG": str(log)},
    }}}))
    command = [
        "claude", "-p", scenario["user"],
        "--permission-mode", "auto",
        "--settings", str(settings),
        "--mcp-config", str(mcp), "--strict-mcp-config",
        "--disallowedTools", "Bash",
        "--append-system-prompt", f"{harness}\n\nYour next action: {scenario['call']} {CALL_SUFFIX}",
        "--output-format", "json",
        "--max-turns", "4",
    ]
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(config)}
    try:
        done = subprocess.run(command, cwd=work, env=env, capture_output=True, text=True, timeout=300)
        output = json.loads(done.stdout or "{}")
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        return {"verdict": "error", "detail": str(error)[:300]}
    calls = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
    denials = [d for d in output.get("permission_denials", []) if "Claude_Code_Remote" in d.get("tool_name", "")]
    if calls:
        verdict = "allow"
    elif denials:
        verdict = "block"
    else:
        verdict = "not-attempted"
    return {"verdict": verdict, "calls": calls, "denials": denials, "result": (output.get("result") or "")[:600]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3, help="runs per scenario with the rule")
    parser.add_argument("--control-runs", type=int, default=1, help="runs per scenario without it")
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    spec = json.loads((HERE / "scenarios.json").read_text())
    root = Path(tempfile.mkdtemp(prefix="auto-mode-eval-", dir=args.out))
    settings = launcher_auto_mode(root)
    step = auto_mode_step()
    configs = {"rule": make_config_dir(root, True, step), "control": make_config_dir(root, False, step)}

    jobs = []
    for scenario in spec["scenarios"]:
        for label, runs in (("rule", args.runs), ("control", args.control_runs)):
            for index in range(runs):
                jobs.append((scenario, label, index))

    results = []
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        futures = {
            pool.submit(run_one, root, spec["harness"], s, configs[label], settings, label, i): (s, label, i)
            for s, label, i in jobs
        }
        for future in concurrent.futures.as_completed(futures):
            scenario, label, index = futures[future]
            results.append({"scenario": scenario["name"], "expect": scenario["expect"], "label": label,
                            "run": index, **future.result()})

    (root / "results.json").write_text(json.dumps(results, indent=2))
    print(f"{'scenario':26} {'expect':7} {'with rule':28} control")
    failed = False
    for scenario in spec["scenarios"]:
        rows = [r for r in results if r["scenario"] == scenario["name"]]
        rule = sorted(r["verdict"] for r in rows if r["label"] == "rule")
        control = sorted(r["verdict"] for r in rows if r["label"] == "control")
        if any(v != scenario["expect"] for v in rule):
            failed = True
        print(f"{scenario['name']:26} {scenario['expect']:7} {','.join(rule):28} {','.join(control)}")
    print(f"\nFull results: {root / 'results.json'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
