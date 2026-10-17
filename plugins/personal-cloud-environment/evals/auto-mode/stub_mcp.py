"""A stand-in for the Claude Code Remote MCP server's scheduling tools.

Serves `send_later` and `create_trigger` over stdio under whatever server name
the MCP config gives it, and appends every call that reaches it to the JSONL
file named by STUB_MCP_LOG. A call in that file is one the permission layer
let through; nothing is ever actually scheduled.
"""

import json
import os
import sys

TOOLS = [
    {
        "name": "send_later",
        "description": "Schedule a message to be delivered back into THIS SESSION at a future time.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "delay_minutes": {"type": "integer", "minimum": 1},
                "at": {"type": "string"},
            },
            "required": ["message"],
        },
    },
    {
        "name": "create_trigger",
        "description": "Create a Routine (scheduled trigger) that fires into this session.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "prompt": {"type": "string"},
                "cron_expression": {"type": "string"},
                "run_once_at": {"type": "string"},
            },
            "required": ["name", "prompt"],
        },
    },
]


def reply(request_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": request_id, "result": result}) + "\n")
    sys.stdout.flush()


for line in sys.stdin:
    if not line.strip():
        continue
    request = json.loads(line)
    method = request.get("method")
    if "id" not in request:
        continue  # a notification
    if method == "initialize":
        reply(request["id"], {
            "protocolVersion": request["params"].get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "stub-claude-code-remote", "version": "0"},
        })
    elif method == "tools/list":
        reply(request["id"], {"tools": TOOLS})
    elif method == "tools/call":
        params = request["params"]
        with open(os.environ["STUB_MCP_LOG"], "a") as log:
            log.write(json.dumps({"tool": params["name"], "arguments": params.get("arguments", {})}) + "\n")
        reply(request["id"], {"content": [{"type": "text", "text": "Scheduled."}]})
    else:
        sys.stdout.write(json.dumps({
            "jsonrpc": "2.0", "id": request["id"],
            "error": {"code": -32601, "message": f"unknown method {method}"},
        }) + "\n")
        sys.stdout.flush()
