#!/usr/bin/env bash
# Builds the "already clean history" Starlight Planner fixture repo.
# Usage: ./build_repo.sh [target-dir]   (default: ./starlight-planner)
set -euo pipefail
TARGET="${1:-starlight-planner}"
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"
git init -q -b main
git config user.email "agent@example.invalid"
git config user.name "Fixture Agent"

mkdir -p docs src/skymap src/observatories src/export
cat > docs/index.md <<'EOF'
# Docs Index

EOF
git add -A
git commit -q -m "chore: seed docs index" --date="2026-02-01T09:00:00"

git checkout -q -b feature/moon-search-export

cat > src/skymap/moon_phase.py <<'EOF'
def moon_phase(date):
    """Return the moon phase (0=new, 0.5=full) for the given date."""
    raise NotImplementedError
EOF
git add -A
git commit -q -m "feat: add moon-phase overlay to sky map" --date="2026-02-02T09:00:00"

cat > src/observatories/search.py <<'EOF'
def search(observatories, min_aperture_mm=None, near=None):
    results = observatories
    if min_aperture_mm:
        results = [o for o in results if o.aperture_mm >= min_aperture_mm]
    if near:
        results = [o for o in results if o.distance_km(near) < 200]
    return results
EOF
git add -A
git commit -q -m "feat: add observatory search filters (location + aperture)" --date="2026-02-02T13:00:00"

# One commit: the feature and the doc that specifically documents it,
# bundled together, with the index row updated in the same commit.
cat > src/export/pdf.py <<'EOF'
def export_trip_pdf(trip, path):
    """Render the trip itinerary to a PDF at the given path."""
    raise NotImplementedError
EOF
cat > docs/trip-export.md <<'EOF'
# Trip Export

Export a planned observation trip to a shareable PDF itinerary.
EOF
cat >> docs/index.md <<'EOF'
- [Trip Export](trip-export.md)
EOF
git add -A
git commit -q -m "feat: add PDF trip export" --date="2026-02-03T09:00:00"

echo "--- log ---"
git log --oneline
