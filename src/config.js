/**
 * Layer configuration for each GeoJSON dataset.
 *
 * Kepler.gl auto-detects geometry, so we only need to specify
 * visual styling (colour, radius, opacity, label visibility).
 *
 * Colour choices follow the standard convention used by Project Owl
 * and most OSINT conflict maps:
 *   Blue  → Ukrainian forces / positions
 *   Red   → Russian forces / positions
 *   Amber → Frontline
 */

// Datasets to load on first render (core operational picture)
export const CORE_LAYERS = [
  'frontline',
  'important_areas',
  'ukrainian_units',
  'russian_units',
  'geolocations_ua_recent',
  'geolocations_ru_recent',
];

// Archive layers (loaded on demand — large datasets)
export const ARCHIVE_LAYERS = [
  'archive_2025_h1',
  'archive_2025_h2',
  'archive_2026_h1',
];

// Colour + style presets per dataset id (filename without .geojson)
export const LAYER_STYLES = {
  frontline: {
    color: [220, 50, 30],        // red
    strokeWidth: 4,
    opacity: 0.9,
    label: 'Frontline',
  },
  important_areas: {
    color: [165, 39, 20],        // dark red (Russian-occupied territory fill)
    opacity: 0.25,
    strokeColor: [165, 39, 20],
    strokeWidth: 1,
    label: 'Important Areas',
  },
  ukrainian_units: {
    color: [2, 136, 209],        // Ukrainian blue
    radius: 6,
    opacity: 0.85,
    label: 'Ukrainian Units',
  },
  russian_units: {
    color: [165, 39, 20],        // Russian red
    radius: 6,
    opacity: 0.85,
    label: 'Russian Units',
  },
  geolocations_ua_recent: {
    color: [30, 136, 229],       // lighter blue
    radius: 4,
    opacity: 0.7,
    label: 'UA Geolocations (30 d)',
  },
  geolocations_ru_recent: {
    color: [194, 24, 91],        // pink-red
    radius: 4,
    opacity: 0.7,
    label: 'RU Geolocations (30 d)',
  },
  archive_2025_h1: {
    color: [255, 152, 0],        // amber
    radius: 3,
    opacity: 0.4,
    label: 'Archive Jan–Jun 2025',
  },
  archive_2025_h2: {
    color: [255, 193, 7],        // yellow
    radius: 3,
    opacity: 0.4,
    label: 'Archive Jul–Dec 2025',
  },
  archive_2026_h1: {
    color: [255, 111, 0],        // deep orange
    radius: 3,
    opacity: 0.4,
    label: 'Archive Jan–Jun 2026',
  },
};

/**
 * Build the full Kepler.gl map configuration from loaded datasets.
 *
 * Kepler.gl's `addDataToMap` accepts a `config` object that specifies
 * the visual state of every layer.  This function generates that config
 * dynamically so it stays in sync with the manifest.
 */
export function buildMapConfig(datasetIds) {
  return {
    version: 'v1',
    config: {
      visState: {
        // layers will be auto-configured by kepler.gl when data is added
      },
      mapState: {
        latitude: 48.5,
        longitude: 36.5,
        zoom: 6,
        bearing: 0,
        pitch: 0,
      },
      mapStyle: {
        styleType: 'positron',
      },
    },
  };
}
