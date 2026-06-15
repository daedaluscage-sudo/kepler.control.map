# Ukraine Control Map — Kepler.gl Viewer

A self-hosted, interactive geospatial visualization of [Project Owl's Ukraine Control Map](https://github.com/owlmaps/UAControlMapBackups) built with [Kepler.gl](https://kepler.gl), deployed to GitHub Pages.

The map displays 9 data layers covering approximately 30,000 geolocated features:

| Layer | Features | Description |
|-------|----------|-------------|
| Frontline | 2 | Current estimated front line (LineString) |
| Important Areas | 21 | Key regions such as Crimea, occupied oblasts (Polygon) |
| Ukrainian Unit Positions | 538 | Last-known positions of Ukrainian military units |
| Russian Unit Positions | 996 | Last-known positions of Russian military units |
| UA Geolocations (30 days) | ~450 | Recent geolocated events, Ukrainian side |
| RU Geolocations (30 days) | ~740 | Recent geolocated events, Russian side |
| Archive Jan–Jun 2025 | 9,525 | Historical geolocated events |
| Archive Jul–Dec 2025 | 8,726 | Historical geolocated events |
| Archive Jan–Jun 2026 | 8,820 | Historical geolocated events |

Data is sourced from Project Owl's KMZ file, which is converted to GeoJSON and loaded into Kepler.gl for visualization.

---

## What is Kepler.gl?

Kepler.gl is an open-source geospatial analysis tool created by Uber's visualization team (now maintained by the Linux Foundation). It renders large datasets on interactive maps using WebGL (via deck.gl), providing capabilities that are difficult to achieve in traditional GIS tools.

**Why it matters for IR research:**

- **Scale.** Kepler.gl can render tens of thousands of points in the browser with smooth pan/zoom, making it practical for conflict datasets that overwhelm Google Maps or basic Leaflet maps.

- **Layer controls.** Each data layer (units, geolocations, frontline) can be toggled, filtered by attribute (date, side, unit type), and styled independently.

- **Time animation.** Geolocation data includes dates; Kepler.gl's time playback slider lets you animate the conflict's evolution over weeks or months.

- **Filtering and aggregation.** You can filter by any data attribute, aggregate points into heatmaps or hexbins to see density patterns, and cross-filter multiple layers simultaneously.

- **Export.** Maps can be exported as images, standalone HTML files, or JSON configurations for reproducibility.

- **No server required.** Everything runs in the browser. GitHub Pages hosts the static files; no backend, no database, no API keys needed.

### How the data pipeline works

```
Project Owl KMZ (Google Maps format)
        │
        ▼
  convert_kmz.py          ← Python script (standard library only)
        │
        ▼
  9 × GeoJSON files       ← One per map layer
        │
        ▼
  Kepler.gl (React app)   ← Loads GeoJSON, renders with deck.gl/WebGL
        │
        ▼
  GitHub Pages             ← Static hosting, updated daily via Actions
```

Kepler.gl uses **CARTO basemap tiles** (Positron, Dark Matter, Voyager) which are free and require no API token. The renderer is **MapLibre GL** (open-source fork of Mapbox GL).

---

## Quick Start

### Option A: Deploy via GitHub (no local setup)

This is the recommended approach. You don't need Node.js or Python on your computer.

1. **Fork this repository** on GitHub.

2. **Enable GitHub Pages:**
   - Go to your fork's **Settings → Pages**
   - Under "Source", select **GitHub Actions**

3. **Update the base path** (important):
   - Open `vite.config.js`
   - Change the `base` value to match your repository name:
     ```js
     base: '/your-repo-name/',
     ```

4. **Push the change.** The GitHub Actions workflow will automatically:
   - Download the latest KMZ from Project Owl
   - Convert it to GeoJSON
   - Build the Kepler.gl app
   - Deploy to GitHub Pages

5. **Visit your map** at `https://<your-username>.github.io/<your-repo-name>/`

The workflow runs daily at 06:00 UTC to pull fresh data automatically.

### Option B: Run locally

Prerequisites: Python 3.8+, Node.js 18+

```bash
# Clone the repository
git clone https://github.com/<your-username>/kepler-ua-map.git
cd kepler-ua-map

# Install JavaScript dependencies
npm install --legacy-peer-deps

# Download and convert the KMZ data
python3 convert_kmz.py

# Copy data to the public directory
mkdir -p public/data
cp -r data/* public/data/

# Start the development server
npm run dev
```

Open `http://localhost:5173/kepler-ua-map/` in your browser.

To build for production:

```bash
npm run build        # Output in dist/
npx vite preview     # Preview the production build locally
```

### Option C: One-command update

After initial setup, use the update script to pull fresh data and rebuild:

```bash
chmod +x update.sh
./update.sh
```

---

## Using Kepler.gl: A Guide for Researchers

When the map loads, you'll see the Kepler.gl interface with the Ukraine control map data. Here's how to work with it:

### The sidebar (left panel)

- **Layers tab:** Shows all loaded data layers. Click the eye icon to toggle visibility. Click a layer name to expand its style controls (color, radius, opacity, stroke).

- **Filters tab:** Add filters to narrow data. For example, filter geolocations by date range or by side (UA/RU). Click "Add Filter", choose a dataset, then select the field to filter on.

- **Interactions tab:** Configure tooltips (what information shows when you hover/click a point) and brushing behavior.

### Map controls (top-right)

- **Toggle 3D** — Switch between flat and perspective views
- **Map style** — Switch between Positron (light), Dark Matter (dark), and Voyager (detailed)
- **Split map** — Compare two map views side-by-side

### Working with the data

**Tooltips:** Click any point or polygon to see its metadata — unit name, description, source links, date, side.

**Time animation:** If you have geolocation layers loaded, Kepler.gl may show a time slider at the bottom. Drag it to filter events by date, or press play to animate.

**Export:** Click the export icon (top-right) to save:
- The map as a PNG image
- The map configuration as JSON (for reproducibility)
- The data as CSV or GeoJSON

### Loading archive data

The three archive layers (27,000+ points total) are not loaded by default to keep the initial load fast. Click the **"Load Archives"** button in the top-right corner to add them. This may take a few seconds.

---

## Project Structure

```
kepler-ua-map/
├── index.html              # Vite entry point
├── vite.config.js          # Build configuration
├── package.json            # Node.js dependencies
├── convert_kmz.py          # KMZ → GeoJSON conversion script
├── update.sh               # One-command data refresh + build
│
├── src/
│   ├── main.jsx            # React entry point
│   ├── App.jsx             # Main component (loads data, renders map)
│   ├── store.js            # Redux store for Kepler.gl
│   └── config.js           # Layer styling configuration
│
├── data/                   # Generated GeoJSON files (git-tracked)
│   ├── manifest.json       # Layer metadata
│   ├── frontline.geojson
│   ├── important_areas.geojson
│   ├── ukrainian_units.geojson
│   ├── russian_units.geojson
│   ├── geolocations_ua_recent.geojson
│   ├── geolocations_ru_recent.geojson
│   ├── archive_2025_h1.geojson
│   ├── archive_2025_h2.geojson
│   └── archive_2026_h1.geojson
│
├── public/data/            # Copy of data/ served by Vite
│
├── .github/workflows/
│   └── deploy.yml          # GitHub Pages CI/CD pipeline
│
└── _work/                  # Temporary (KMZ download, KML extraction)
```

---

## The Conversion Script

`convert_kmz.py` is a standalone Python script that uses only the standard library. It:

1. Downloads the latest KMZ from `github.com/owlmaps/UAControlMapBackups`
2. Extracts the KML (KMZ is a ZIP file containing KML + icon images)
3. Parses each `<Folder>` as a separate map layer
4. Converts KML `<Placemark>` elements to GeoJSON features:
   - `<Point>` → GeoJSON Point
   - `<LineString>` → GeoJSON LineString
   - `<Polygon>` → GeoJSON Polygon
5. Extracts metadata (name, description, unit number, date, side, source links)
6. Writes one `.geojson` file per layer, plus a `manifest.json`

To convert a local KMZ file instead of downloading:

```bash
python3 convert_kmz.py --local /path/to/file.kmz
```

---

## Customization

### Changing the base map style

Edit `src/store.js`, change the `styleType` value:

```js
mapStyle: {
  styleType: 'dark-matter',  // 'positron', 'dark-matter', or 'voyager'
}
```

### Adjusting default map view

Edit `src/config.js`, change the `mapState` values:

```js
mapState: {
  latitude: 48.5,   // center latitude
  longitude: 36.5,  // center longitude
  zoom: 6,          // zoom level (1 = world, 18 = street)
}
```

### Adding your own data layers

1. Place a GeoJSON file in `data/` and `public/data/`
2. Add an entry to `LAYER_STYLES` in `src/config.js`
3. Add the filename (without `.geojson`) to `CORE_LAYERS` or `ARCHIVE_LAYERS`
4. Rebuild: `npm run build`

### Using a Mapbox basemap

If you want Mapbox satellite or other Mapbox styles:

1. Create a free account at [mapbox.com](https://www.mapbox.com)
2. Copy your access token
3. In `src/App.jsx`, change the `mapboxApiAccessToken` prop:

```jsx
<KeplerGl
  id={MAP_ID}
  width={width}
  height={height}
  mapboxApiAccessToken="pk.your_token_here"
/>
```

This is optional — the default CARTO basemaps work without any token.

---

## Data Attribution

Map data is produced by [Project Owl](https://twitter.com/UAControlMap) and archived at [github.com/owlmaps/UAControlMapBackups](https://github.com/owlmaps/UAControlMapBackups). This project consumes their data but is not affiliated with Project Owl.

Kepler.gl is an open-source project by the [kepler.gl contributors](https://github.com/keplergl/kepler.gl) under the MIT license.

Basemap tiles by [CARTO](https://carto.com/basemaps/) under CC BY 3.0.

---

## Troubleshooting

**"Error loading map data"** — The `data/` folder may be empty. Run `python3 convert_kmz.py` to generate the GeoJSON files, then copy them to `public/data/`.

**Map loads but no data appears** — Open browser DevTools (F12) → Console tab. Look for fetch errors. The data URL path must match the `base` setting in `vite.config.js`.

**GitHub Pages shows 404** — Make sure Pages is configured to use "GitHub Actions" as the source (not "Deploy from a branch"). Also verify the `base` path in `vite.config.js` matches your repository name exactly.

**Build fails with peer dependency errors** — Use `npm install --legacy-peer-deps`. Kepler.gl has complex dependency chains that sometimes conflict.

**The map is slow with archives loaded** — 30,000 points is near the practical limit for smooth interaction. Consider filtering by date or side to reduce the visible point count.
