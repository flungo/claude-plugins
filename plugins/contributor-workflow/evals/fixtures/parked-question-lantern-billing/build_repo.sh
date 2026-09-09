#!/usr/bin/env bash
# Builds the Lantern Billing parked-question fixture repo.
# Usage: ./build_repo.sh [target-dir]   (default: ./lantern-billing)
set -euo pipefail
TARGET="${1:-lantern-billing}"
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"
git init -q -b main
git config user.email "agent@example.invalid"
git config user.name "Fixture Agent"

mkdir -p src/billing
cat > src/billing/invoice.py <<'EOF'
def line_total(qty: int, unit_price: int) -> int:
    """Total for a line, in minor units."""
    return qty * unit_price
EOF
git add -A
git commit -q -m "chore: seed billing module" --date="2026-04-01T09:00:00"

git checkout -q -b feature/late-fees

# The reviewer's ask on thread-a — rename amt to amount_cents so the unit is
# explicit — is ALREADY applied here. `fee` deliberately keeps no unit suffix:
# that is the subject of the optional offer the agent parked on the same
# thread, and it is correct for this PR to leave it alone.
cat > src/billing/late_fee.py <<'EOF'
def late_fee(amount_cents: int, days_overdue: int) -> int:
    """Late fee in minor units, capped at 25% of the amount."""
    fee = (amount_cents * days_overdue) // 1000
    cap = amount_cents // 4
    return min(fee, cap)
EOF
git add -A
git commit -q -m "feat: charge a capped late fee on overdue invoices" --date="2026-04-02T10:00:00"

echo "--- log ---"
git log --oneline
