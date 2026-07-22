#!/usr/bin/env bash
# Builds the Tidepool Notes thread-triage fixture repo.
# Usage: ./build_repo.sh [target-dir]   (default: ./tidepool-notes)
set -euo pipefail
TARGET="${1:-tidepool-notes}"
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"
git init -q -b main
git config user.email "agent@example.invalid"
git config user.name "Fixture Agent"

mkdir -p src/tags src/search
cat > src/search/query.py <<'EOF'
def matches(text: str, query: str) -> bool:
    """Case-insensitive substring match used across search."""
    return query.lower() in text.lower()
EOF
git add -A
git commit -q -m "chore: seed search module" --date="2026-03-01T09:00:00"

git checkout -q -b feature/tag-autocomplete

# Deliberately contains: a docstring typo (thread B, trivial fix), and a
# case-sensitivity choice that conflicts with search.query.matches (thread
# C, a real product decision). Already handles the empty-list case that
# thread A asks about (thread A, already addressed).
cat > src/tags/autocomplete.py <<'EOF'
def suggest(tags: list[str], prefix: str) -> list[str]:
    """Return tags starting with prefix, case-sensitive.

    If the tag list is empty, an empty list is returned rather than
    raising, so callers don't need to special-case an empty vocabulary.

    Note: results are not deduplicated; the caller is expected to recieve
    a pre-deduplicated tag list.
    """
    if not tags:
        return []
    return [t for t in tags if t.startswith(prefix)]
EOF
git add -A
git commit -q -m "feat: add tag autocomplete" --date="2026-03-02T10:00:00"

echo "--- log ---"
git log --oneline
