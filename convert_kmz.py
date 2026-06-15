#!/usr/bin/env python3
"""
convert_kmz.py — Convert Project Owl's Ukraine Control Map KMZ to GeoJSON layers.

Downloads the latest KMZ from the owlmaps GitHub repository, extracts the KML,
and converts each map folder into a separate GeoJSON file suitable for Kepler.gl.

Usage:
    python3 convert_kmz.py                   # Download latest + convert
    python3 convert_kmz.py --local file.kmz   # Convert a local KMZ file

Output:
    data/frontline.geojson
    data/important_areas.geojson
    data/ukrainian_units.geojson
    data/russian_units.geojson
    data/geolocations_ua_recent.geojson
    data/geolocations_ru_recent.geojson
    data/archive_2025_h1.geojson
    data/archive_2025_h2.geojson
    data/archive_2026_h1.geojson

Requirements:
    Python 3.8+  (standard library only — no pip installs needed)
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

KMZ_URL = (
    "https://github.com/owlmaps/UAControlMapBackups/raw/latest/latest.kmz"
)

KML_NS = {"kml": "http://www.opengis.net/kml/2.2"}

# Map KML folder names → output filenames and display labels
FOLDER_MAP = {
    "Frontline": ("frontline", "Frontline"),
    "Important Areas": ("important_areas", "Important Areas"),
    "Ukrainian Unit Positions": ("ukrainian_units", "Ukrainian Unit Positions"),
    "Russian Unit Positions": ("russian_units", "Russian Unit Positions"),
    "Ukraine Geolocations (~30 Days)": (
        "geolocations_ua_recent",
        "Ukraine Geolocations (Recent)",
    ),
    "Russian Geolocations (~30 Days)": (
        "geolocations_ru_recent",
        "Russia Geolocations (Recent)",
    ),
    "Archives Geos (Jan 2025 - Jun 2025)": (
        "archive_2025_h1",
        "Archive Jan–Jun 2025",
    ),
    "Archives Geos (Jul 2025 - Dec 2025)": (
        "archive_2025_h2",
        "Archive Jul–Dec 2025",
    ),
    "Archive Geos (Jan 2026-Jun 2026)": (
        "archive_2026_h1",
        "Archive Jan–Jun 2026",
    ),
}

# Colour hints extracted from KML style IDs (hex without #)
STYLE_COLOURS = {
    "A52714": "#A52714",  # Russian red
    "0288D1": "#0288D1",  # Ukrainian blue
    "C2185B": "#C2185B",  # Russian geolocation pink
    "01579B": "#01579B",  # Dark blue
    "1A237E": "#1A237E",  # Navy
    "F9A825": "#F9A825",  # Amber/yellow
    "0F9D58": "#0F9D58",  # Green
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def download_kmz(url: str, dest: str) -> str:
    """Download KMZ file. Returns path to downloaded file."""
    print(f"Downloading KMZ from:\n  {url}")
    urllib.request.urlretrieve(url, dest)
    size_mb = os.path.getsize(dest) / (1024 * 1024)
    print(f"  Downloaded {size_mb:.1f} MB → {dest}")
    return dest


def extract_kml(kmz_path: str, work_dir: str) -> str:
    """Extract doc.kml from a KMZ (ZIP) archive. Returns path to KML."""
    with zipfile.ZipFile(kmz_path, "r") as zf:
        zf.extractall(work_dir)
    kml_path = os.path.join(work_dir, "doc.kml")
    if not os.path.exists(kml_path):
        # Some KMZ files use a different name
        kml_files = [f for f in os.listdir(work_dir) if f.endswith(".kml")]
        if kml_files:
            kml_path = os.path.join(work_dir, kml_files[0])
        else:
            raise FileNotFoundError("No KML file found inside KMZ archive")
    size_mb = os.path.getsize(kml_path) / (1024 * 1024)
    print(f"  Extracted KML: {size_mb:.1f} MB")
    return kml_path


def parse_coordinates(coord_text: str):
    """
    Parse KML coordinate string → list of [lng, lat] or [lng, lat, alt].
    KML format: "lng,lat,alt lng,lat,alt ..."
    GeoJSON expects: [[lng, lat], ...]
    """
    coords = []
    for token in coord_text.strip().split():
        parts = token.split(",")
        if len(parts) >= 2:
            lng, lat = float(parts[0]), float(parts[1])
            coords.append([lng, lat])
    return coords


def extract_style_colour(placemark) -> str:
    """Try to extract a hex colour from the placemark's styleUrl."""
    style_el = placemark.find("kml:styleUrl", KML_NS)
    if style_el is not None and style_el.text:
        for hex_code, colour in STYLE_COLOURS.items():
            if hex_code in style_el.text:
                return colour
    return "#888888"


def parse_date_from_name(name: str) -> str:
    """Extract date string like '25/01/01' from placemark name '[25/01/01] ...'."""
    match = re.match(r"\[(\d{2}/\d{2}/\d{2})\]", name)
    if match:
        raw = match.group(1)
        parts = raw.split("/")
        return f"20{parts[0]}-{parts[1]}-{parts[2]}"
    return ""


def parse_side_from_name(name: str) -> str:
    """Extract 'UA' or 'RU' from placemark name like '[25/01/01] Ru Position'."""
    lower = name.lower()
    if "ua " in lower or "ua position" in lower:
        return "UA"
    if "ru " in lower or "ru position" in lower:
        return "RU"
    return ""


def placemark_to_feature(placemark) -> dict | None:
    """Convert a single KML Placemark to a GeoJSON Feature."""
    # --- Name ---
    name_el = placemark.find("kml:name", KML_NS)
    name = name_el.text.strip() if name_el is not None and name_el.text else ""

    # --- Description ---
    desc_el = placemark.find("kml:description", KML_NS)
    description = ""
    if desc_el is not None and desc_el.text:
        # Strip HTML tags for clean text properties
        description = re.sub(r"<[^>]+>", " ", desc_el.text).strip()
        description = re.sub(r"\s+", " ", description)

    # --- Extended Data ---
    properties = {"name": name, "description": description}

    ext_data = placemark.find("kml:ExtendedData", KML_NS)
    if ext_data is not None:
        for data_el in ext_data.findall("kml:Data", KML_NS):
            key = data_el.get("name", "")
            val_el = data_el.find("kml:value", KML_NS)
            if key and val_el is not None and val_el.text:
                properties[key] = val_el.text.strip()

    # --- Style / colour hint ---
    properties["_colour"] = extract_style_colour(placemark)

    # --- Date and side for geolocation points ---
    date_str = parse_date_from_name(name)
    if date_str:
        properties["date"] = date_str

    side = properties.get("code", "") or parse_side_from_name(name)
    if side:
        properties["side"] = side.upper()

    # --- Geometry ---
    geometry = None

    # Point
    point_el = placemark.find("kml:Point", KML_NS)
    if point_el is not None:
        coord_el = point_el.find("kml:coordinates", KML_NS)
        if coord_el is not None and coord_el.text:
            coords = parse_coordinates(coord_el.text)
            if coords:
                geometry = {"type": "Point", "coordinates": coords[0]}

    # LineString
    line_el = placemark.find("kml:LineString", KML_NS)
    if line_el is not None:
        coord_el = line_el.find("kml:coordinates", KML_NS)
        if coord_el is not None and coord_el.text:
            coords = parse_coordinates(coord_el.text)
            if len(coords) >= 2:
                geometry = {"type": "LineString", "coordinates": coords}

    # Polygon
    poly_el = placemark.find("kml:Polygon", KML_NS)
    if poly_el is not None:
        outer = poly_el.find(
            "kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", KML_NS
        )
        if outer is not None and outer.text:
            coords = parse_coordinates(outer.text)
            if len(coords) >= 3:
                # Close the ring if needed
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                geometry = {"type": "Polygon", "coordinates": [coords]}

    if geometry is None:
        return None

    return {"type": "Feature", "properties": properties, "geometry": geometry}


def convert_folder(folder, folder_name: str, output_dir: str) -> dict:
    """Convert a KML Folder to a GeoJSON FeatureCollection and write to disk."""
    if folder_name not in FOLDER_MAP:
        slug = re.sub(r"[^a-z0-9]+", "_", folder_name.lower()).strip("_")
        filename = slug
        label = folder_name
    else:
        filename, label = FOLDER_MAP[folder_name]

    placemarks = folder.findall("kml:Placemark", KML_NS)
    features = []
    skipped = 0

    for pm in placemarks:
        feat = placemark_to_feature(pm)
        if feat:
            features.append(feat)
        else:
            skipped += 1

    collection = {
        "type": "FeatureCollection",
        "metadata": {"layer_name": label, "source": "Project Owl / owlmaps"},
        "features": features,
    }

    out_path = os.path.join(output_dir, f"{filename}.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"  {label:42s}  {len(features):>6,} features  ({size_kb:,.0f} KB)")
    if skipped:
        print(f"    ⚠ {skipped} placemarks skipped (no parseable geometry)")

    return {
        "filename": f"{filename}.geojson",
        "label": label,
        "feature_count": len(features),
        "geometry_type": _dominant_geometry(features),
    }


def _dominant_geometry(features: list) -> str:
    types = set()
    for f in features[:50]:
        types.add(f["geometry"]["type"])
    if len(types) == 1:
        return types.pop()
    return "Mixed"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    script_dir = Path(__file__).parent.resolve()
    data_dir = script_dir / "data"
    work_dir = script_dir / "_work"

    data_dir.mkdir(exist_ok=True)
    work_dir.mkdir(exist_ok=True)

    # --- Acquire KMZ ---
    if "--local" in sys.argv:
        idx = sys.argv.index("--local")
        kmz_path = sys.argv[idx + 1]
        print(f"Using local KMZ: {kmz_path}")
    else:
        kmz_path = str(work_dir / "latest.kmz")
        download_kmz(KMZ_URL, kmz_path)

    # --- Extract KML ---
    kml_path = extract_kml(kmz_path, str(work_dir))

    # --- Parse ---
    print("\nParsing KML …")
    tree = ET.parse(kml_path)
    root = tree.getroot()
    doc = root.find("kml:Document", KML_NS)
    if doc is None:
        print("ERROR: No <Document> element found in KML.")
        sys.exit(1)

    map_name = ""
    name_el = doc.find("kml:name", KML_NS)
    if name_el is not None:
        map_name = name_el.text
        print(f"  Map: {map_name}")

    # --- Convert each folder ---
    folders = doc.findall("kml:Folder", KML_NS)
    print(f"  Found {len(folders)} layer folders\n")
    print(f"  {'Layer':<42s}  {'Features':>8s}  Size")
    print(f"  {'─' * 42}  {'─' * 8}  {'─' * 10}")

    manifest = []
    for folder in folders:
        fname_el = folder.find("kml:name", KML_NS)
        if fname_el is None:
            continue
        folder_name = fname_el.text.strip()
        info = convert_folder(folder, folder_name, str(data_dir))
        manifest.append(info)

    # --- Write manifest ---
    manifest_path = data_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(
            {"map_name": map_name, "layers": manifest},
            f,
            indent=2,
        )

    total_features = sum(m["feature_count"] for m in manifest)
    print(f"\n  Total: {total_features:,} features across {len(manifest)} layers")
    print(f"  Manifest written to {manifest_path}")
    print("\nDone. GeoJSON files are in the data/ directory.")
    print("Open index.html to view the map in Kepler.gl.")


if __name__ == "__main__":
    main()
