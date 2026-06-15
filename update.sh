#!/usr/bin/env bash
# update.sh — Fetch the latest Ukraine Control Map and rebuild.
#
# Usage:
#   ./update.sh              # Download latest KMZ, convert, rebuild
#   ./update.sh --convert    # Convert only (skip download, use existing KMZ)
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Ukraine Control Map Updater ==="

# Step 1: Convert KMZ → GeoJSON
if [[ "${1:-}" == "--convert" ]]; then
    echo "Skipping download, converting existing KMZ..."
    python3 convert_kmz.py --local _work/latest.kmz
else
    echo "Downloading latest KMZ and converting..."
    python3 convert_kmz.py
fi

# Step 2: Copy data to public directory for Vite
echo ""
echo "Copying data to public/data/ ..."
mkdir -p public/data
cp -r data/* public/data/

# Step 3: Build (if npm is available)
if command -v npm &> /dev/null; then
    echo ""
    echo "Building with Vite..."
    npm run build
    echo ""
    echo "Build complete. Output is in dist/"
    echo "To preview locally: npx vite preview"
else
    echo ""
    echo "npm not found — skipping build."
    echo "Install Node.js 18+ and run: npm install && npm run build"
fi

echo ""
echo "Done."
