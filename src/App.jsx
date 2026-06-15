import React, {useEffect, useState} from 'react';
import {useDispatch} from 'react-redux';
import {addDataToMap} from '@kepler.gl/actions';
import {processGeojson} from '@kepler.gl/processors';
import AutoSizer from 'react-virtualized-auto-sizer';
import {KeplerGl} from '@kepler.gl/components';
import {CORE_LAYERS, ARCHIVE_LAYERS, LAYER_STYLES, buildMapConfig} from './config';

const MAP_ID = 'ua_control_map';
const BASE_URL = import.meta.env.BASE_URL || '/';

function App() {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(true);
  const [loadedLayers, setLoadedLayers] = useState([]);
  const [archivesLoaded, setArchivesLoaded] = useState(false);
  const [error, setError] = useState(null);

  // -------------------------------------------------------------------
  // Load a single GeoJSON file and dispatch it to the Kepler.gl store
  // -------------------------------------------------------------------
  async function loadLayer(layerId, isFirstLayer = false) {
    const url = `${BASE_URL}data/${layerId}.geojson`;
    const response = await fetch(url);
    if (!response.ok) {
      console.warn(`Failed to load ${layerId}: ${response.status}`);
      return;
    }
    const geojson = await response.json();
    const label = LAYER_STYLES[layerId]?.label || layerId;
    const processed = processGeojson(geojson);

    const payload = {
      datasets: {
        info: {id: layerId, label},
        data: processed,
      },
      options: {
        centerMap: isFirstLayer,
        readOnly: false,
      },
    };

    // Only add config on the first layer load
    if (isFirstLayer) {
      payload.config = buildMapConfig([layerId]);
    }

    dispatch(addDataToMap(payload));
    setLoadedLayers(prev => [...prev, layerId]);
  }

  // -------------------------------------------------------------------
  // Initial load: fetch core layers sequentially
  // -------------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;

    async function loadCoreLayers() {
      try {
        for (let i = 0; i < CORE_LAYERS.length; i++) {
          if (cancelled) return;
          await loadLayer(CORE_LAYERS[i], i === 0);
        }
        if (!cancelled) setLoading(false);
      } catch (err) {
        console.error('Error loading map data:', err);
        if (!cancelled) {
          setError(err.message);
          setLoading(false);
        }
      }
    }

    loadCoreLayers();
    return () => { cancelled = true; };
  }, []);

  // -------------------------------------------------------------------
  // Load archive layers on demand
  // -------------------------------------------------------------------
  async function handleLoadArchives() {
    setArchivesLoaded(true);
    for (const layerId of ARCHIVE_LAYERS) {
      try {
        await loadLayer(layerId, false);
      } catch (err) {
        console.warn(`Failed to load archive ${layerId}:`, err);
      }
    }
  }

  // -------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------
  if (error) {
    return (
      <div style={{padding: 40, fontFamily: 'system-ui'}}>
        <h2>Error loading map data</h2>
        <p>{error}</p>
        <p style={{color: '#666'}}>
          Make sure the <code>data/</code> folder contains the GeoJSON files.
          Run <code>python3 convert_kmz.py</code> to generate them.
        </p>
      </div>
    );
  }

  return (
    <div style={{position: 'absolute', width: '100%', height: '100%'}}>
      {/* Status bar */}
      <div style={{
        position: 'absolute',
        top: 12,
        right: 16,
        zIndex: 1000,
        display: 'flex',
        gap: 8,
        alignItems: 'center',
      }}>
        {loading && (
          <span style={{
            background: 'rgba(0,0,0,0.65)',
            color: '#fff',
            padding: '6px 14px',
            borderRadius: 6,
            fontSize: 13,
          }}>
            Loading layers… ({loadedLayers.length}/{CORE_LAYERS.length})
          </span>
        )}

        {!loading && !archivesLoaded && (
          <button
            onClick={handleLoadArchives}
            style={{
              background: 'rgba(0,0,0,0.65)',
              color: '#fff',
              padding: '6px 14px',
              borderRadius: 6,
              fontSize: 13,
              border: 'none',
              cursor: 'pointer',
            }}
          >
            Load Archives (27k points)
          </button>
        )}
      </div>

      {/* Kepler.gl Map */}
      <AutoSizer>
        {({height, width}) => (
          <KeplerGl
            id={MAP_ID}
            width={width}
            height={height}
            mapboxApiAccessToken=""
          />
        )}
      </AutoSizer>
    </div>
  );
}

export default App;
