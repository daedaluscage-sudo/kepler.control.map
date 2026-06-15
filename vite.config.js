import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  // For GitHub Pages: change 'kepler-ua-map' to your repo name
  base: '/kepler.control.map/',
  build: {
    outDir: 'dist',
    sourcemap: false,
    commonjsOptions: {
      // kepler.gl sub-packages are CJS
      include: [/node_modules/],
      transformMixedEsModules: true,
    },
  },
  optimizeDeps: {
    include: [
      '@kepler.gl/components',
      '@kepler.gl/actions',
      '@kepler.gl/reducers',
      '@kepler.gl/processors',
      '@kepler.gl/constants',
      'react-palm/tasks',
    ],
    esbuildOptions: {
      define: {
        global: 'globalThis',
      },
    },
  },
  define: {
    'process.env': '{}',
    'global': 'globalThis',
  },
  resolve: {
    alias: {
      'mapbox-gl': 'maplibre-gl',
    },
  },
});
