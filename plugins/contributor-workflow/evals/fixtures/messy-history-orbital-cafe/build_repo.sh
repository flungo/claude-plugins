#!/usr/bin/env bash
# Builds the "messy history" Orbital Café fixture repo.
# Usage: ./build_repo.sh [target-dir]   (default: ./orbital-cafe)
set -euo pipefail
TARGET="${1:-orbital-cafe}"
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"
git init -q -b main
git config user.email "agent@example.invalid"
git config user.name "Fixture Agent"

mkdir -p docs
cat > docs/index.md <<'EOF'
# Docs Index

EOF
git add -A
git commit -q -m "chore: seed docs index" --date="2026-01-01T09:00:00"

git checkout -q -b feature/loyalty-and-offline

mkdir -p src/loyalty src/kiosk src/receipts ci

cat > src/loyalty/points.py <<'EOF'
def award_points(order_total_cents: int) -> int:
    """Award 1 point per $1 spent, rounded down."""
    return order_total_cents // 100


def redeem_points(balance: int, points: int) -> int:
    if points > balance:
        raise ValueError("insufficient points")
    return balance - points
EOF

cat > src/kiosk/offline_queue.py <<'EOF'
import json
from pathlib import Path

QUEUE_FILE = Path("offline_queue.jsonl")


def enqueue(order: dict) -> None:
    with QUEUE_FILE.open("a") as f:
        f.write(json.dumps(order) + "\n")


def flush(send_fn) -> int:
    if not QUEUE_FILE.exists():
        return 0
    sent = 0
    for line in QUEUE_FILE.read_text().splitlines():
        send_fn(json.loads(line))
        sent += 1
    QUEUE_FILE.unlink()
    return sent
EOF

cat > docs/loyalty-points.md <<'EOF'
# Loyalty Points

Customers earn 1 point per dollar spent (rounded down) and can redeem
points at checkout.
EOF

cat > docs/offline-queue.md <<'EOF'
# Offline Order Queue

Orders are buffered to disk when the kiosk loses network connectivity and
flushed once connectivity returns.
EOF

cat >> docs/index.md <<'EOF'
- [Loyalty Points](loyalty-points.md)
- [Offline Order Queue](offline-queue.md)
EOF

git add -A
git commit -q -m "feat: add loyalty points and offline queue" --date="2026-01-02T10:00:00"

# Anti-pattern: deferring the docs-index update for a doc added later
# instead of updating it in the commit that adds the doc.
cat >> docs/index.md <<'EOF'
- [Receipt Templates](receipt-templates.md)
EOF
cat > docs/receipt-templates.md <<'EOF'
# Receipt Templates

Receipts now render via Jinja2 templates instead of string concatenation.
EOF
git add -A
git commit -q -m "docs: add remaining docs and index" --date="2026-01-02T14:00:00"

# Anti-pattern: bundling an unrelated refactor with an unrelated CI change.
cat > src/receipts/template.py <<'EOF'
from jinja2 import Template

RECEIPT_TEMPLATE = Template(
    "{{ store_name }}\n{% for item in items %}{{ item.name }} - {{ item.price }}\n{% endfor %}Total: {{ total }}"
)


def render_receipt(store_name: str, items: list, total: str) -> str:
    return RECEIPT_TEMPLATE.render(store_name=store_name, items=items, total=total)
EOF

cat > ci/workflow.yml <<'EOF'
name: lint-and-test
on: [pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest
EOF

git add -A
git commit -q -m "chore: refactor receipts and tweak CI" --date="2026-01-03T09:00:00"

# Anti-pattern: a stray fixup commit that should have been folded into the
# commit it corrects (the loyalty points work introduced the rounding rule).
cat > CONTRIBUTING.md <<'EOF'
# Contributing

## Currency rounding
Loyalty point calculations always round down to the nearest whole point.
EOF
git add -A
git commit -q -m "fix: update CONTRIBUTING rounding note" --date="2026-01-03T11:00:00"

echo "--- log ---"
git log --oneline
