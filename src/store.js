import {createStore, combineReducers, applyMiddleware, compose} from 'redux';
import {keplerGlReducer} from '@kepler.gl/reducers';
import {enhanceReduxMiddleware} from '@kepler.gl/reducers';
import {taskMiddleware} from 'react-palm/tasks';

// Custom initial state for the kepler.gl instance
const customizedKeplerGlReducer = keplerGlReducer.initialState({
  uiState: {
    // Hide the data-upload modal on load — we load data programmatically
    currentModal: null,
    activeSidePanel: 'layer',
    readOnly: false,
  },
  mapStyle: {
    // Use CARTO Positron (light) as default — good for conflict-area overlays
    styleType: 'positron',
  },
});

const reducers = combineReducers({
  keplerGl: customizedKeplerGlReducer,
});

// Kepler.gl uses react-palm for async task handling
const middlewares = enhanceReduxMiddleware([taskMiddleware]);
const enhancers = [applyMiddleware(...middlewares)];

const store = createStore(reducers, {}, compose(...enhancers));

export default store;
