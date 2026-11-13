import './bootstrap';

import 'leaflet/dist/leaflet.css';

import Alpine from 'alpinejs';
window.Alpine = Alpine;
Alpine.start();

// Earth Trend Explorer Leaflet Map Module
import './map/earth-map.js';
