/**
 * Earth Trend Explorer - Interactive Leaflet Map & Scientific Analysis Module
 * 
 * Provides interactive satellite mapping, African region selection,
 * asynchronous communication with the Laravel/FastAPI scientific analysis backend,
 * and Plotly.js time-series trend visualizations.
 */

import L from 'leaflet';
window.L = L;
import africaRegions from './africa-regions.json';

// Spherical Earth radius in meters (WGS84 authalic radius)
const EARTH_RADIUS = 6371008.8;

function calculateGeodesicAreaKm2(latLngs) {
    if (!latLngs || latLngs.length < 3) return 0;
    
    const points = Array.isArray(latLngs[0]) && typeof latLngs[0][0] === 'object' 
        ? latLngs[0] 
        : latLngs;

    const rad = Math.PI / 180;
    let total = 0;

    for (let i = 0; i < points.length; i++) {
        const p1 = points[i];
        const p2 = points[(i + 1) % points.length];
        
        const lat1 = (p1.lat !== undefined ? p1.lat : p1[0]) * rad;
        const lng1 = (p1.lng !== undefined ? p1.lng : p1[1]) * rad;
        const lat2 = (p2.lat !== undefined ? p2.lat : p2[0]) * rad;
        const lng2 = (p2.lng !== undefined ? p2.lng : p2[1]) * rad;

        total += (lng2 - lng1) * (2 + Math.sin(lat1) + Math.sin(lat2));
    }

    const areaM2 = Math.abs((total * EARTH_RADIUS * EARTH_RADIUS) / 2.0);
    return Math.round(areaM2 / 1000000);
}

function calculateGeoJsonAreaKm2(geometry) {
    const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    let area = 0;

    polygons.forEach(rings => {
        rings.forEach((ring, index) => {
            const ringArea = calculateGeodesicAreaKm2(ring.map(([lng, lat]) => [lat, lng]));
            area += index === 0 ? ringArea : -ringArea;
        });
    });

    return Math.max(0, Math.round(area));
}

function generateMiniPolygonSvg(latLngs) {
    if (!latLngs || !latLngs.length) return '';
    const points = Array.isArray(latLngs[0])
        ? (Array.isArray(latLngs[0][0]) ? latLngs[0][0] : latLngs[0])
        : latLngs;
    if (points.length < 3) return '';
    
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    const coords = points.map(p => {
        const x = p.lng !== undefined ? p.lng : p[1];
        const y = -(p.lat !== undefined ? p.lat : p[0]);
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
        return { x, y };
    });

    const width = maxX - minX || 1;
    const height = maxY - minY || 1;
    const pad = 4;
    const svgSize = 48;
    const scale = (svgSize - pad * 2) / Math.max(width, height);

    return coords.map((c, i) => {
        const px = pad + (c.x - minX) * scale;
        const py = pad + (c.y - minY) * scale;
        return `${i === 0 ? 'M' : 'L'} ${px.toFixed(1)} ${py.toFixed(1)}`;
    }).join(' ') + ' Z';
}

export class EarthMap {
    constructor(containerId = 'earth-map', options = {}) {
        this.container = typeof containerId === 'string' ? document.getElementById(containerId) : containerId;
        if (!this.container) return;

        this.options = Object.assign({
            initialCenter: [0, 17],
            initialZoom: 3,
            minZoom: 3,
            maxZoom: 18,
            maxBounds: L.latLngBounds([[-36, -20], [38, 53]]),
            maxBoundsViscosity: 1,
            primaryTileUrl: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            primaryTileAttribution: '&copy; Esri, Maxar, Earthstar Geographics, CNES/Airbus DS, USGS, AeroGRID, IGN',
        }, options);

        this.map = null;
        this.currentLayer = null;
        this.selectedPredefinedRegionId = null;
        this.selectedVariable = 'temperature_anomaly';
        this.startYear = 2004;
        this.endYear = 2024;
        this.isAnalyzing = false;
        this.lastAnalysisData = null;

        this.variableMetadata = {
            'temperature_anomaly': {
                name: 'Surface Temperature Anomaly',
                unit: '°C',
                source: 'NASA GISTEMP v4 (GISS Surface Temperature Analysis)',
                resolution: 'Monthly',
                coverage: '2004–2024 (21 Years)',
                description: 'Monthly surface temperature anomaly relative to regional base periods. Positive values indicate warmer than baseline.'
            },
            'precipitation_mm': {
                name: 'Precipitation',
                unit: 'mm/day',
                source: 'NASA POWER / MERRA-2 (Precipitation Corrected)',
                resolution: 'Monthly (Mean Daily Rate)',
                coverage: '2004–2024 (21 Years)',
                description: 'Monthly mean daily precipitation rate (PRECTOTCORR) derived from MERRA-2 satellite-model assimilation.'
            }
        };

        this.init();
    }

    init() {
        this.map = L.map(this.container, {
            center: this.options.initialCenter,
            zoom: this.options.initialZoom,
            minZoom: this.options.minZoom,
            maxZoom: this.options.maxZoom,
            maxBounds: this.options.maxBounds,
            maxBoundsViscosity: this.options.maxBoundsViscosity,
            zoomControl: false,
            attributionControl: false,
            fadeAnimation: true
        });
        L.control.attribution({ position: 'bottomleft', prefix: false }).addTo(this.map);

        this.satelliteLayer = L.tileLayer(this.options.primaryTileUrl, {
            attribution: this.options.primaryTileAttribution,
            maxZoom: 18,
            subdomains: ['server', 'services']
        }).addTo(this.map);

        this.streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        });
        this.currentBaseLayer = 'satellite';
        this.initMapLabels();

        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false,
            maxWidth: 120
        }).addTo(this.map);

        this.bindEvents();
        this.initMiniMap();
        this.updateVariableMetadataUi();
    }

    setVariable(variableId) {
        if (!this.variableMetadata[variableId]) return;
        this.selectedVariable = variableId;

        const tempBtn = document.getElementById('var-btn-temp');
        const precipBtn = document.getElementById('var-btn-precip');

        if (variableId === 'temperature_anomaly') {
            if (tempBtn) {
                tempBtn.className = 'flex items-center justify-between p-2.5 rounded-lg border text-left text-xs font-semibold transition-all cursor-pointer bg-emerald-50/70 border-emerald-500 text-emerald-950 ring-1 ring-emerald-500/30';
            }
            if (precipBtn) {
                precipBtn.className = 'flex items-center justify-between p-2.5 rounded-lg border text-left text-xs font-semibold transition-all cursor-pointer bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100';
            }
        } else {
            if (precipBtn) {
                precipBtn.className = 'flex items-center justify-between p-2.5 rounded-lg border text-left text-xs font-semibold transition-all cursor-pointer bg-emerald-50/70 border-emerald-500 text-emerald-950 ring-1 ring-emerald-500/30';
            }
            if (tempBtn) {
                tempBtn.className = 'flex items-center justify-between p-2.5 rounded-lg border text-left text-xs font-semibold transition-all cursor-pointer bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100';
            }
        }

        this.updateVariableMetadataUi();

        // If results are currently showing and region is selected, automatically refresh analysis
        const resultsEl = document.getElementById('analysis-results');
        if (resultsEl && !resultsEl.classList.contains('hidden') && this.selectedPredefinedRegionId) {
            this.runScientificAnalysis();
        }
    }

    updateVariableMetadataUi() {
        const meta = this.variableMetadata[this.selectedVariable];
        if (!meta) return;

        const unitEl = document.getElementById('var-meta-unit');
        const sourceEl = document.getElementById('var-meta-source');
        const resEl = document.getElementById('var-meta-resolution');
        const covEl = document.getElementById('var-meta-coverage');
        const descEl = document.getElementById('var-desc');

        if (unitEl) unitEl.textContent = meta.unit;
        if (sourceEl) sourceEl.textContent = meta.source;
        if (resEl) resEl.textContent = meta.resolution;
        if (covEl) covEl.textContent = meta.coverage;
        if (descEl) descEl.textContent = meta.description;
    }

    onDateChange() {
        const startSelect = document.getElementById('analysis-start-year');
        const endSelect = document.getElementById('analysis-end-year');
        const badge = document.getElementById('date-validation-badge');
        const text = document.getElementById('date-validation-text');
        const analyzeBtn = document.getElementById('btn-analyze-execute');

        if (!startSelect || !endSelect) return;
        const start = parseInt(startSelect.value, 10);
        const end = parseInt(endSelect.value, 10);

        this.startYear = start;
        this.endYear = end;

        if (start > end) {
            if (badge) {
                badge.className = 'p-2 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-[11px] font-medium flex items-center gap-1.5';
            }
            if (text) {
                text.textContent = 'Invalid: Start Year must be less than or equal to End Year.';
            }
            if (analyzeBtn) {
                analyzeBtn.setAttribute('disabled', 'disabled');
            }
        } else {
            const span = end - start + 1;
            if (badge) {
                badge.className = 'p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1.5';
            }
            if (text) {
                text.textContent = `Selected period: ${start}–${end} (${span} observational year${span > 1 ? 's' : ''}).`;
            }
            if (analyzeBtn && this.selectedPredefinedRegionId) {
                analyzeBtn.removeAttribute('disabled');
            }
        }
    }

    bindEvents() {
        const clearBtn = document.getElementById('btn-clear-selection');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearRegion());
        }

        const btnZoomIn = document.getElementById('btn-zoom-in');
        const btnZoomOut = document.getElementById('btn-zoom-out');
        const btnLayerToggle = document.getElementById('btn-layer-toggle');

        if (btnZoomIn) btnZoomIn.addEventListener('click', () => this.map.zoomIn());
        if (btnZoomOut) btnZoomOut.addEventListener('click', () => this.map.zoomOut());
        if (btnLayerToggle) btnLayerToggle.addEventListener('click', () => this.toggleBaseLayer());
    }

    selectPredefinedRegion(feature, layer) {
        this.clearRegion();
        this.selectedPredefinedRegionId = feature.properties.id;
        this.currentLayer = layer;

        this.updateRegionLayerStyle();
        this.updateGeometryState(layer);
        
        const analysisStatus = document.getElementById('analysis-status');
        if (analysisStatus) {
            analysisStatus.textContent = `${feature.properties.name} selected. Click Analyze to process real NASA data.`;
        }

        const analyzeBtn = document.getElementById('btn-analyze-execute');
        if (analyzeBtn) {
            const start = parseInt(document.getElementById('analysis-start-year')?.value || '2004', 10);
            const end = parseInt(document.getElementById('analysis-end-year')?.value || '2024', 10);
            if (start <= end) {
                analyzeBtn.removeAttribute('disabled');
            }
        }
        const predictBtn = document.getElementById('btn-predict-execute');
        if (predictBtn) {
            predictBtn.removeAttribute('disabled');
        }
    }

    updateRegionLayerStyle() {
        if (!this.regionsLayer) return;

        this.regionsLayer.setStyle(feature => ({
            color: '#ffffff',
            weight: 0,
            fillColor: feature.properties.color,
            fillOpacity: feature.properties.id === this.selectedPredefinedRegionId ? 0.85 : 0.65
        }));
    }

    updateGeometryState(layer) {
        if (!layer) return;

        const bounds = layer.getBounds();
        const latLngs = layer.getLatLngs ? layer.getLatLngs() : [];
        const areaKm2 = calculateGeodesicAreaKm2(latLngs);
        const svgPath = generateMiniPolygonSvg(latLngs);

        const boundsString = `${bounds.getWest().toFixed(2)}°, ${bounds.getSouth().toFixed(2)}°, ${bounds.getEast().toFixed(2)}°, ${bounds.getNorth().toFixed(2)}°`;

        const feature = layer.feature || {};
        const regionName = feature.properties ? feature.properties.name : 'Selected Region';

        const geojson = {
            type: 'Feature',
            geometry: layer.toGeoJSON ? layer.toGeoJSON().geometry : {},
            properties: {
                name: regionName,
                id: this.selectedPredefinedRegionId,
                areaKm2: areaKm2,
                boundsFormatted: boundsString
            }
        };

        window.EarthTrendExplorer = window.EarthTrendExplorer || {};
        window.EarthTrendExplorer.geojson = geojson;
        window.EarthTrendExplorer.areaKm2 = areaKm2;
        window.EarthTrendExplorer.bounds = boundsString;
        window.EarthTrendExplorer.selectedRegionId = this.selectedPredefinedRegionId;

        this.updateUiCard(geojson, areaKm2, boundsString, svgPath);
    }

    updateUiCard(geojson, areaKm2, boundsString, svgPath) {
        const areaEl = document.getElementById('selected-region-area');
        const boundsEl = document.getElementById('selected-region-bounds');
        const cardEl = document.getElementById('selected-region-card');
        const emptyEl = document.getElementById('selected-region-empty');
        const nameEl = document.getElementById('selected-region-name');
        const svgEl = document.getElementById('selected-region-svg-path');
        const analyzeBtn = document.getElementById('btn-analyze-execute');
        const predictBtn = document.getElementById('btn-predict-execute');

        if (geojson) {
            if (nameEl) nameEl.textContent = geojson.properties.name || 'Selected Region';
            if (areaEl) areaEl.textContent = areaKm2.toLocaleString('en-US') + ' km²';
            if (boundsEl) boundsEl.textContent = boundsString;
            if (cardEl) cardEl.classList.remove('hidden');
            if (emptyEl) emptyEl.classList.add('hidden');
            if (svgEl) svgEl.setAttribute('d', svgPath || 'M 6 12 L 38 8 L 42 36 L 10 40 Z');
            if (analyzeBtn) {
                analyzeBtn.removeAttribute('disabled');
            }
            if (predictBtn) {
                predictBtn.removeAttribute('disabled');
            }
        } else {
            if (nameEl) nameEl.textContent = 'Selected Region';
            if (areaEl) areaEl.textContent = '0 km²';
            if (boundsEl) boundsEl.textContent = 'None';
            if (cardEl) cardEl.classList.add('hidden');
            if (emptyEl) emptyEl.classList.remove('hidden');
            if (analyzeBtn) {
                analyzeBtn.setAttribute('disabled', 'disabled');
            }
            if (predictBtn) {
                predictBtn.setAttribute('disabled', 'disabled');
            }
        }
    }

    clearRegion() {
        this.selectedPredefinedRegionId = null;
        this.currentLayer = null;

        if (this.regionsLayer) {
            this.regionsLayer.setStyle({
                color: '#ffffff',
                weight: 0,
                fillOpacity: 0.65
            });
        }

        const analyzeBtn = document.getElementById('btn-analyze-execute');
        if (analyzeBtn) analyzeBtn.setAttribute('disabled', 'disabled');

        const predictBtn = document.getElementById('btn-predict-execute');
        if (predictBtn) predictBtn.setAttribute('disabled', 'disabled');

        const analysisStatus = document.getElementById('analysis-status');
        if (analysisStatus) {
            analysisStatus.textContent = 'Click an African region on the map, then select Analyze or Predict.';
        }

        const resultsEl = document.getElementById('analysis-results');
        if (resultsEl) resultsEl.classList.add('hidden');

        const predictCardEl = document.getElementById('prediction-results-card');
        if (predictCardEl) predictCardEl.classList.add('hidden');

        const chartSelect = document.getElementById('chart-type-select');
        if (chartSelect) chartSelect.value = 'trending';
        this.selectedChartType = 'trending';
        const explainerEl = document.getElementById('chart-quick-explainer');
        if (explainerEl) explainerEl.textContent = '';
        this.updateChartExplanationPanel('trending', null);
        this.lastAnalysisData = null;

        this.updateUiCard(null, 0, 'None', '');
    }

    async runScientificAnalysis() {
        if (!this.selectedPredefinedRegionId) {
            const status = document.getElementById('analysis-status');
            if (status) status.textContent = 'Please select a region on the map first.';
            return;
        }

        const startSelect = document.getElementById('analysis-start-year');
        const endSelect = document.getElementById('analysis-end-year');
        const startYear = parseInt(startSelect ? startSelect.value : '2004', 10);
        const endYear = parseInt(endSelect ? endSelect.value : '2024', 10);

        if (startYear > endYear) {
            alert('Start Year must be less than or equal to End Year.');
            return;
        }

        const analyzeBtn = document.getElementById('btn-analyze-execute');
        const icon = document.getElementById('btn-analyze-icon');
        const spinner = document.getElementById('btn-analyze-spinner');
        const label = document.getElementById('btn-analyze-label');
        const status = document.getElementById('analysis-status');

        this.isAnalyzing = true;
        if (analyzeBtn) analyzeBtn.setAttribute('disabled', 'disabled');
        if (icon) icon.classList.add('hidden');
        if (spinner) spinner.classList.remove('hidden');
        if (label) label.textContent = 'Analyzing...';
        if (status) status.textContent = 'Querying NASA climate observations and computing Mann-Kendall trend...';

        const chartSelect = document.getElementById('chart-type-select');
        const chartType = chartSelect ? chartSelect.value : (this.selectedChartType || 'trending');
        this.selectedChartType = chartType;

        const url = `/api/analyze?region=${encodeURIComponent(this.selectedPredefinedRegionId)}&variable=${encodeURIComponent(this.selectedVariable)}&start_year=${startYear}&end_year=${endYear}&chart_type=${encodeURIComponent(chartType)}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                const errorMsg = data.error || (data.messages ? data.messages.join(', ') : 'Scientific analysis failed.');
                throw new Error(errorMsg);
            }

            this.lastAnalysisData = data;
            this.displayAnalysisResults(data);

            if (status) {
                status.textContent = `Analysis complete for ${data.region.name} (${data.period.start_year}–${data.period.end_year}).`;
            }
        } catch (err) {
            console.error('Scientific analysis error:', err);
            if (status) {
                status.innerHTML = `<span class="text-rose-600 font-semibold">⚠️ ${err.message}</span>`;
            }
            alert(`Analysis Error:\n${err.message}\n\nPlease verify that the FastAPI backend service is running on port 8001.`);
        } finally {
            this.isAnalyzing = false;
            if (analyzeBtn && this.selectedPredefinedRegionId) analyzeBtn.removeAttribute('disabled');
            if (icon) icon.classList.remove('hidden');
            if (spinner) spinner.classList.add('hidden');
            if (label) label.textContent = 'Analyze';
        }
    }

    displayAnalysisResults(data) {
        const resultsEl = document.getElementById('analysis-results');
        if (!resultsEl) return;

        resultsEl.classList.remove('hidden');

        // Subtitle
        const subtitleEl = document.getElementById('analysis-results-subtitle');
        if (subtitleEl) {
            subtitleEl.textContent = `${data.variable.name} across ${data.region.name} (${data.period.start_year}–${data.period.end_year})`;
        }

        // Variable & Period
        const titleEl = document.getElementById('chart-variable-title');
        if (titleEl) {
            titleEl.textContent = `Monthly ${data.variable.name} & Trend Line`;
        }
        const periodEl = document.getElementById('analysis-period');
        if (periodEl) {
            periodEl.textContent = `${data.period.start_year}–${data.period.end_year} (${data.time_series.length} monthly observations)`;
        }

        // Direction Badge
        const dirBadge = document.getElementById('analysis-direction-badge');
        if (dirBadge) {
            const dir = data.metrics.direction;
            if (dir === 'increasing') {
                dirBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-rose-100 text-rose-800 border border-rose-200';
                dirBadge.innerHTML = '▲ Increasing Trend';
            } else if (dir === 'decreasing') {
                dirBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-sky-100 text-sky-800 border border-sky-200';
                dirBadge.innerHTML = '▼ Decreasing Trend';
            } else {
                dirBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-slate-100 text-slate-800 border border-slate-200';
                dirBadge.innerHTML = '━ No Clear Monotonic Trend';
            }
        }

        // Sen's Slope
        const slopeDecade = document.getElementById('analysis-slope-decade');
        const slopeYear = document.getElementById('analysis-slope-year');
        const sign = data.metrics.slope_per_decade >= 0 ? '+' : '';
        if (slopeDecade) {
            slopeDecade.textContent = `${sign}${data.metrics.slope_per_decade.toFixed(3)} ${data.variable.unit} / decade`;
        }
        if (slopeYear) {
            slopeYear.textContent = `(${sign}${data.metrics.slope_per_year.toFixed(4)} ${data.variable.unit} / year)`;
        }

        // Statistical Significance Verdict Badge
        const sigBadge = document.getElementById('analysis-significance-badge');
        if (sigBadge) {
            if (data.metrics.is_significant) {
                sigBadge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300';
                sigBadge.innerHTML = '✓ Statistically Significant (p &lt; 0.05)';
            } else {
                sigBadge.className = 'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300';
                sigBadge.innerHTML = '✗ Not Statistically Significant (p ≥ 0.05)';
            }
        }

        // Statistics Details
        const pValEl = document.getElementById('analysis-p-value');
        if (pValEl) pValEl.textContent = data.metrics.p_value.toFixed(4);

        const tauEl = document.getElementById('analysis-kendall-tau');
        if (tauEl) tauEl.textContent = data.metrics.kendall_tau.toFixed(4);

        const nEl = document.getElementById('analysis-sample-size');
        if (nEl) nEl.textContent = `${data.metrics.sample_size} years (${data.time_series.length} months)`;

        // Plain-Language Interpretation
        const interpEl = document.getElementById('analysis-plain-language');
        if (interpEl) {
            interpEl.textContent = data.metrics.interpretation;
        }

        // Data Source & Region Info
        const sourceEl = document.getElementById('analysis-source');
        if (sourceEl) sourceEl.textContent = data.variable.source;

        const regInfoEl = document.getElementById('analysis-region-info');
        if (regInfoEl) {
            regInfoEl.textContent = `${data.region.name} (Macro-Region)`;
        }

        // Caveats list
        const caveatsList = document.getElementById('analysis-caveats-list');
        if (caveatsList && Array.isArray(data.caveats)) {
            caveatsList.innerHTML = data.caveats.map(c => `<li>${c}</li>`).join('');
        }

        const genAt = document.getElementById('analysis-generated-at');
        if (genAt) genAt.textContent = `Generated: ${new Date().toLocaleTimeString()} (UTC ${new Date().getUTCHours()}:${new Date().getUTCMinutes()})`;

        // Render Plotly Interactive Time Series Chart
        this.renderPlotlyChart(data);

        // Scroll results into view smoothly
        resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    onChartTypeChange(newType) {
        this.selectedChartType = newType;
        if (!this.lastAnalysisData) return;
        this.renderChart(newType);
    }

    renderPlotlyChart(data) {
        this.lastAnalysisData = data;
        const chartSelect = document.getElementById('chart-type-select');
        if (chartSelect) {
            chartSelect.value = this.selectedChartType || 'trending';
        }
        this.renderChart(this.selectedChartType || 'trending');
    }

    renderChart(type) {
        const data = this.lastAnalysisData;
        if (!data) return;

        const container = document.getElementById('plotly-timeseries');
        if (!container || typeof Plotly === 'undefined') {
            console.warn('Plotly is not loaded yet or container missing');
            return;
        }

        const titleEl = document.getElementById('chart-variable-title');
        const periodEl = document.getElementById('analysis-period');
        const explainerEl = document.getElementById('chart-quick-explainer');
        const overlay = document.getElementById('chart-loading-overlay');

        if (overlay) overlay.classList.remove('hidden');

        try {
            const isTemp = data.variable.id === 'temperature_anomaly';
            const primaryColor = isTemp ? '#dc2626' : '#0284c7';
            const primaryFill = isTemp ? 'rgba(220, 38, 38, 0.06)' : 'rgba(2, 132, 199, 0.06)';

            let traces = [];
            let layout = {};

            if (type === 'mann_kendall_sen') {
                // 4. Mann-Kendall / Sen's slope
                if (titleEl) titleEl.textContent = `Annual ${data.variable.name} & Sen's Slope (Mann-Kendall)`;
                if (periodEl) periodEl.textContent = `${data.period.start_year}–${data.period.end_year} (Annual Aggregated Means)`;
                if (explainerEl) {
                    explainerEl.textContent = `Non-parametric rank test on annual averages: evaluates monotonic trend immune to seasonal cycles (p = ${data.metrics.p_value.toFixed(4)}, τ = ${data.metrics.kendall_tau.toFixed(4)}, Sen's slope = ${data.metrics.slope_per_decade >= 0 ? '+' : ''}${data.metrics.slope_per_decade.toFixed(3)} ${data.variable.unit}/decade).`;
                }

                const annualPoints = (data.trends && data.trends[data.variable.id]) ? data.trends[data.variable.id] : (data.annual_trend || []);
                const years = annualPoints.map(p => p.year);
                const values = annualPoints.map(p => p.value);
                const senLines = annualPoints.map(p => p.sen_line);

                traces.push({
                    x: years,
                    y: values,
                    type: 'scatter',
                    mode: 'markers',
                    name: `Annual Mean ${data.variable.short_name}`,
                    marker: { size: 7, color: primaryColor, symbol: 'circle' },
                    hovertemplate: `<b>Year %{x}</b><br>Annual Mean: %{y:.2f} ${data.variable.unit}<extra></extra>`
                });

                if (senLines && senLines.some(v => v !== null && v !== undefined)) {
                    traces.push({
                        x: years,
                        y: senLines,
                        type: 'scatter',
                        mode: 'lines',
                        name: `Sen's Slope (${data.metrics.slope_per_decade >= 0 ? '+' : ''}${data.metrics.slope_per_decade.toFixed(3)} ${data.variable.unit}/decade)`,
                        line: { color: '#ea580c', width: 2.5, dash: 'dash' },
                        hovertemplate: `<b>Sen's Slope Trend</b><br>Value: %{y:.2f} ${data.variable.unit}<extra></extra>`
                    });
                }

                layout = {
                    margin: { t: 25, r: 25, b: 45, l: 55 },
                    xaxis: {
                        title: { text: 'Calendar Year', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#e2e8f0',
                        dtick: 2,
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    yaxis: {
                        title: { text: `Annual Mean ${data.variable.name} (${data.variable.unit})`, font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#cbd5e1',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    legend: { orientation: 'h', x: 0, y: 1.15, font: { size: 11, color: '#334155' } },
                    hovermode: 'closest',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    autosize: true
                };

            } else if (type === 'correlation') {
                // 3. Correlation (Bivariate Scatter Plot)
                if (titleEl) titleEl.textContent = `Bivariate Climate Correlation: Precipitation vs Temperature Anomaly`;
                if (periodEl) periodEl.textContent = `${data.period.start_year}–${data.period.end_year} (Paired Monthly Observations)`;
                if (explainerEl) {
                    const c = data.correlation;
                    if (c && c.coefficient !== null && c.coefficient !== undefined) {
                        const ciStr = (c.confidence_interval_95 && c.confidence_interval_95.length === 2) 
                            ? ` [95% CI: ${c.confidence_interval_95[0].toFixed(3)} to ${c.confidence_interval_95[1].toFixed(3)}]` 
                            : '';
                        explainerEl.textContent = `Pearson correlation between monthly Precipitation (mm/day) and Temperature Anomaly (°C): r = ${c.coefficient.toFixed(3)}${ciStr}, p = ${c.p_value.toFixed(4)} (n = ${c.sample_size}). ${c.interpretation}`;
                    } else {
                        explainerEl.textContent = `Correlation between paired monthly precipitation and temperature anomaly observations.`;
                    }
                }

                const scatter = data.scatter || [];
                traces.push({
                    x: scatter.map(p => p.precipitation_mm),
                    y: scatter.map(p => p.temperature_anomaly),
                    customdata: scatter.map(p => p.date),
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Monthly Pairs',
                    marker: { size: 6, color: '#0284c7', opacity: 0.75 },
                    hovertemplate: `<b>%{customdata}</b><br>Precipitation: %{x:.2f} mm/day<br>Temp Anomaly: %{y:.2f} °C<extra></extra>`
                });

                layout = {
                    margin: { t: 25, r: 25, b: 45, l: 55 },
                    xaxis: {
                        title: { text: 'Precipitation Rate (mm/day)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#e2e8f0',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    yaxis: {
                        title: { text: 'Surface Temperature Anomaly (°C)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#cbd5e1',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    legend: { orientation: 'h', x: 0, y: 1.15, font: { size: 11, color: '#334155' } },
                    hovermode: 'closest',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    autosize: true
                };

            } else if (type === 'linear_regression') {
                // 2. Linear Regression (Scatter + Fitted OLS Line)
                if (titleEl) titleEl.textContent = `Linear Regression: Temperature Anomaly vs Precipitation`;
                if (periodEl) periodEl.textContent = `${data.period.start_year}–${data.period.end_year} (Ordinary Least Squares)`;
                if (explainerEl) {
                    const r = data.regression;
                    if (r && r.slope !== null && r.slope !== undefined) {
                        explainerEl.textContent = `Ordinary Least Squares (OLS) model: Temp = (${r.slope.toFixed(4)} × Precip) + (${r.intercept.toFixed(3)}) | R² = ${r.r_squared.toFixed(4)} (${(r.r_squared * 100).toFixed(1)}% variance explained), p = ${r.p_value.toFixed(4)}, SE = ${r.standard_error.toFixed(4)}.`;
                    } else {
                        explainerEl.textContent = `Linear regression model fitted between monthly precipitation and temperature anomaly observations.`;
                    }
                }

                const scatter = data.scatter || [];
                traces.push({
                    x: scatter.map(p => p.precipitation_mm),
                    y: scatter.map(p => p.temperature_anomaly),
                    customdata: scatter.map(p => p.date),
                    type: 'scatter',
                    mode: 'markers',
                    name: 'Observations',
                    marker: { size: 5, color: '#64748b', opacity: 0.65 },
                    hovertemplate: `<b>%{customdata}</b><br>Precipitation: %{x:.2f} mm/day<br>Temp Anomaly: %{y:.2f} °C<extra></extra>`
                });

                if (data.regression_line && data.regression_line.length >= 2) {
                    const rLine = data.regression_line;
                    const r = data.regression;
                    const lineName = (r && r.slope !== null) 
                        ? `OLS Fit: y = ${r.slope.toFixed(3)}x + (${r.intercept.toFixed(2)}) (R² = ${r.r_squared.toFixed(3)})` 
                        : 'Regression Line';

                    traces.push({
                        x: rLine.map(p => p.precipitation_mm),
                        y: rLine.map(p => p.temperature_anomaly),
                        type: 'scatter',
                        mode: 'lines',
                        name: lineName,
                        line: { color: '#2563eb', width: 2.5 },
                        hovertemplate: `<b>Linear Fit</b><br>Precipitation: %{x:.2f} mm/day<br>Fitted Temp: %{y:.2f} °C<extra></extra>`
                    });
                }

                layout = {
                    margin: { t: 25, r: 25, b: 45, l: 55 },
                    xaxis: {
                        title: { text: 'Precipitation Rate (mm/day)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#e2e8f0',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    yaxis: {
                        title: { text: 'Surface Temperature Anomaly (°C)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#cbd5e1',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    legend: { orientation: 'h', x: 0, y: 1.15, font: { size: 11, color: '#334155' } },
                    hovermode: 'closest',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    autosize: true
                };

            } else if (type === 'regression') {
                // 1. Regression (Residuals Plot)
                if (titleEl) titleEl.textContent = `Regression Residuals: Model Fit Errors Over Time`;
                if (periodEl) periodEl.textContent = `${data.period.start_year}–${data.period.end_year} (Residuals: Observed - Fitted)`;
                if (explainerEl) {
                    explainerEl.textContent = `Regression residuals (e = y - ŷ): shows monthly deviation of actual temperature anomaly from the linear regression prediction. Homogeneous spread around zero indicates unbiased fit.`;
                }

                const residuals = data.residuals || [];
                traces.push({
                    x: residuals.map(p => p.date),
                    y: residuals.map(p => p.residual),
                    type: 'bar',
                    name: 'Residual Error',
                    marker: {
                        color: residuals.map(p => p.residual >= 0 ? '#10b981' : '#f43f5e'),
                        opacity: 0.85
                    },
                    hovertemplate: `<b>%{x}</b><br>Residual Error: %{y:.3f} °C<extra></extra>`
                });

                if (residuals.length >= 2) {
                    traces.push({
                        x: [residuals[0].date, residuals[residuals.length - 1].date],
                        y: [0, 0],
                        type: 'scatter',
                        mode: 'lines',
                        name: 'Zero Error Baseline',
                        line: { color: '#475569', width: 1.5, dash: 'dot' },
                        hoverinfo: 'none'
                    });
                }

                layout = {
                    margin: { t: 25, r: 25, b: 45, l: 55 },
                    xaxis: {
                        title: { text: 'Time (Year-Month)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#e2e8f0',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    yaxis: {
                        title: { text: 'Residual Error (°C)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#cbd5e1',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    legend: { orientation: 'h', x: 0, y: 1.15, font: { size: 11, color: '#334155' } },
                    hovermode: 'closest',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    autosize: true
                };

            } else {
                // 5. Trending (Default: Monthly observations + Sen's slope line)
                if (titleEl) titleEl.textContent = `Monthly ${data.variable.name} & Trend Line`;
                if (periodEl) periodEl.textContent = `${data.period.start_year}–${data.period.end_year} (${data.time_series.length} monthly observations)`;
                if (explainerEl) {
                    explainerEl.textContent = `Continuous monthly observations with Sen's non-parametric median slope fitted trend line (${data.metrics.slope_per_decade >= 0 ? '+' : ''}${data.metrics.slope_per_decade.toFixed(3)} ${data.variable.unit}/decade).`;
                }

                const dates = data.time_series.map(pt => pt.date);
                const values = data.time_series.map(pt => pt.value);

                traces.push({
                    x: dates,
                    y: values,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: `Monthly ${data.variable.short_name}`,
                    line: { color: primaryColor, width: 1.5 },
                    marker: { size: 3, color: primaryColor },
                    fill: 'tozeroy',
                    fillcolor: primaryFill,
                    hovertemplate: `<b>%{x}</b><br>Value: %{y:.2f} ${data.variable.unit}<extra></extra>`
                });

                const annualPoints = (data.trends && data.trends[data.variable.id]) ? data.trends[data.variable.id] : (data.annual_trend || []);
                if (annualPoints && annualPoints.length >= 2 && annualPoints.some(p => p.sen_line !== null && p.sen_line !== undefined)) {
                    traces.push({
                        x: annualPoints.map(p => `${p.year}-06`),
                        y: annualPoints.map(p => p.sen_line),
                        type: 'scatter',
                        mode: 'lines',
                        name: "Sen's Slope Trend",
                        line: { color: '#ea580c', width: 3, dash: 'dash' },
                        hovertemplate: `<b>Trend Estimate</b><br>Rate: ${data.metrics.slope_per_decade >= 0 ? '+' : ''}${data.metrics.slope_per_decade.toFixed(3)} ${data.variable.unit}/decade<extra></extra>`
                    });
                }

                layout = {
                    margin: { t: 25, r: 25, b: 45, l: 55 },
                    xaxis: {
                        title: { text: 'Time (Year-Month)', font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#e2e8f0',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    yaxis: {
                        title: { text: `${data.variable.name} (${data.variable.unit})`, font: { size: 11, color: '#64748b' } },
                        gridcolor: '#f1f5f9',
                        zerolinecolor: '#cbd5e1',
                        tickfont: { size: 10, color: '#64748b' }
                    },
                    legend: { orientation: 'h', x: 0, y: 1.15, font: { size: 11, color: '#334155' } },
                    hovermode: 'closest',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent',
                    autosize: true
                };
            }

            const config = {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['lasso2d', 'select2d'],
                displaylogo: false
            };

            Plotly.newPlot(container, traces, layout, config);
        } catch (plotErr) {
            console.error('Plotly render error:', plotErr);
            container.innerHTML = `<div class="p-6 text-center text-xs text-rose-600 font-semibold">⚠️ Failed to render chart: ${plotErr.message}</div>`;
        } finally {
            if (overlay) overlay.classList.add('hidden');
            this.updateChartExplanationPanel(type, data);
        }
    }

    /**
     * Updates the collapsible "How to read this chart" panel with precise technical
     * definitions and real API synthesis results for the current selection.
     */
    updateChartExplanationPanel(chartType, data) {
        const typeBadge = document.getElementById('chart-guide-type-badge');
        const howToReadEl = document.getElementById('chart-guide-how-to-read');
        const currentResultEl = document.getElementById('chart-guide-current-result');

        const labels = {
            'trending': 'Trending',
            'mann_kendall_sen': "Mann-Kendall / Sen's slope",
            'correlation': 'Correlation',
            'linear_regression': 'Linear Regression',
            'regression': 'Regression (Residuals)'
        };

        if (typeBadge) {
            typeBadge.textContent = labels[chartType] || 'Trending';
        }

        if (!data || !data.success) {
            if (howToReadEl) {
                howToReadEl.textContent = 'Select an African region and run an analysis to view visual guidance.';
            }
            if (currentResultEl) {
                currentResultEl.textContent = 'No result available for this selection.';
            }
            return;
        }

        const varName = data.variable.name;
        const varUnit = data.variable.unit;
        const regionName = data.region.name;
        const startYear = data.period.start_year;
        const endYear = data.period.end_year;

        const formatPValue = (p) => {
            if (p === null || p === undefined) return '--';
            if (p < 0.0001) return 'p < 0.0001';
            return `p = ${p.toFixed(4)}`;
        };

        // Static Technical Guides (3 to 5 sentences tailored for scientists and researchers)
        const staticGuides = {
            'trending': `The horizontal axis indexes time across continuous monthly observations (Year-Month), while the vertical axis measures ${varName} in ${varUnit}. Solid markers and lines indicate monthly observed anomalies with a subtle shaded area anchored to zero. The dashed line depicts the non-parametric Sen's median slope fitted across the selected window. This representation reveals seasonal cycles, intra-annual extremes, and long-term trajectory simultaneously.`,
            'mann_kendall_sen': `The horizontal axis represents calendar years, while the vertical axis plots annual aggregated mean ${varName} in ${varUnit}. Circular markers show annual mean values, effectively filtering high-frequency intra-annual seasonality. The overlaid dashed line illustrates Sen's robust, non-parametric median slope estimator. This configuration accompanies the rank-based Mann-Kendall test to evaluate monotonic multi-year trends without assuming residual normality.`,
            'correlation': `The horizontal axis plots monthly Precipitation Rate (mm/day), and the vertical axis plots Surface Temperature Anomaly (°C). Each circular point represents a single paired monthly observation in the selected macro-region. The distribution of points illustrates the bivariate dispersion and joint distribution between moisture and thermal variations. No causal mechanism is inferred; the visualization evaluates empirical co-variation and linear association.`,
            'linear_regression': `The horizontal axis represents the predictor variable (Precipitation Rate in mm/day), and the vertical axis represents the dependent response (Surface Temperature Anomaly in °C). Scattered points represent empirical paired monthly observations. The solid linear fit line is estimated via Ordinary Least Squares (OLS) minimizing sum-of-squared errors. This bivariate model evaluates the rate of change and proportion of variance explained between climate variables.`,
            'regression': `The horizontal axis tracks time by monthly intervals, and the vertical axis plots regression residuals (errors) in °C. Each vertical bar shows the residual difference between observed and fitted temperature anomaly (e = y - ŷ). A dashed baseline marks zero residual error. Homogeneous, symmetric spread around zero indicates an unbiased model fit, whereas clustering or persistent drifts signify unmodeled non-linear dynamics or autocorrelation.`
        };

        if (howToReadEl) {
            howToReadEl.textContent = staticGuides[chartType] || staticGuides['trending'];
        }

        // Dynamic synthesis sentences derived strictly from real API metrics
        if (currentResultEl) {
            let resultSentence = 'No result available for this selection.';

            if (chartType === 'mann_kendall_sen') {
                const m = data.metrics;
                const sign = m.slope_per_decade >= 0 ? '+' : '';
                resultSentence = `For ${regionName} (${startYear}–${endYear}), annual mean ${varName} exhibits an estimated Sen's slope of ${sign}${m.slope_per_decade.toFixed(3)} ${varUnit}/decade (Kendall's τ = ${m.kendall_tau.toFixed(4)}, ${formatPValue(m.p_value)}, n = ${m.sample_size} annual means), evaluated as ${m.verdict.toLowerCase()} at α = 0.05.`;
            } else if (chartType === 'correlation') {
                const c = data.correlation;
                if (c && c.coefficient !== null && c.coefficient !== undefined) {
                    const ciStr = (c.confidence_interval_95 && c.confidence_interval_95.length === 2)
                        ? ` (95% CI [${c.confidence_interval_95[0].toFixed(3)}, ${c.confidence_interval_95[1].toFixed(3)}])`
                        : '';
                    resultSentence = `The empirical association between monthly Precipitation and Surface Temperature Anomaly across ${regionName} yields a Pearson correlation of r = ${c.coefficient.toFixed(3)}${ciStr} (${formatPValue(c.p_value)}, n = ${c.sample_size} paired months), indicating ${c.interpretation.toLowerCase()}`;
                }
            } else if (chartType === 'linear_regression') {
                const r = data.regression;
                if (r && r.slope !== null && r.slope !== undefined) {
                    const r2Pct = (r.r_squared * 100).toFixed(1);
                    resultSentence = `The fitted OLS model for ${regionName} estimates a slope of ${r.slope.toFixed(4)} °C/(mm/day) with intercept ${r.intercept.toFixed(3)} °C (R² = ${r.r_squared.toFixed(4)}, accounting for ${r2Pct}% of temperature variance; ${formatPValue(r.p_value)}, SE = ${r.standard_error.toFixed(4)}, n = ${r.sample_size} months).`;
                }
            } else if (chartType === 'regression') {
                const r = data.regression;
                if (r && r.r_squared !== null && r.r_squared !== undefined) {
                    const r2Pct = (r.r_squared * 100).toFixed(1);
                    resultSentence = `Analysis of regression residuals across ${regionName} (${r.sample_size} monthly points) reflects an OLS model explaining ${r2Pct}% of variance (R² = ${r.r_squared.toFixed(4)}, standard error = ${r.standard_error.toFixed(4)} °C), with deviations indicating variance unexplained by a simple linear association.`;
                }
            } else {
                // trending (default)
                const m = data.metrics;
                const sign = m.slope_per_decade >= 0 ? '+' : '';
                resultSentence = `Over the ${startYear}–${endYear} record (${data.time_series.length} monthly observations), ${regionName} demonstrates a ${m.direction} trend in ${varName} at an estimated rate of ${sign}${m.slope_per_decade.toFixed(3)} ${varUnit}/decade (${formatPValue(m.p_value)}, ${m.is_significant ? 'significant' : 'non-significant'} at α = 0.05).`;
            }

            currentResultEl.textContent = resultSentence;
        }
    }

    async runPrediction() {
        if (!this.selectedPredefinedRegionId) {
            const status = document.getElementById('analysis-status');
            if (status) status.textContent = 'Please select a region on the map first.';
            return;
        }

        const predictBtn = document.getElementById('btn-predict-execute');
        const icon = document.getElementById('btn-predict-icon');
        const spinner = document.getElementById('btn-predict-spinner');
        const label = document.getElementById('btn-predict-label');
        const status = document.getElementById('analysis-status');

        if (predictBtn) predictBtn.setAttribute('disabled', 'disabled');
        if (icon) icon.classList.add('hidden');
        if (spinner) spinner.classList.remove('hidden');
        if (label) label.textContent = 'Forecasting...';
        if (status) status.textContent = 'Running Model 1 v6 machine learning projection for January 2025...';

        const url = `/api/predict?region=${encodeURIComponent(this.selectedPredefinedRegionId)}&variable=${encodeURIComponent(this.selectedVariable)}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const errJson = await response.json().catch(() => ({}));
                throw new Error(errJson.error || `Prediction service returned error HTTP ${response.status}`);
            }

            const data = await response.json();
            if (!data.success || !data.records || data.records.length === 0) {
                throw new Error('No prediction records returned by inference engine.');
            }

            this.displayPredictionResults(data);

            if (status) {
                const regTitle = data.records[0].region_name || data.records[0].region;
                status.textContent = `Forecast ready for ${regTitle} (${data.target_horizon}).`;
            }
        } catch (err) {
            console.error('Prediction error:', err);
            if (status) {
                status.textContent = `Forecast error: ${err.message}`;
            }
            alert(`Predictive Forecast Error:\n${err.message}`);
        } finally {
            if (predictBtn && this.selectedPredefinedRegionId) predictBtn.removeAttribute('disabled');
            if (icon) icon.classList.remove('hidden');
            if (spinner) spinner.classList.add('hidden');
            if (label) label.textContent = 'Predict Next Month (Jan 2025)';
        }
    }

    displayPredictionResults(data) {
        const cardEl = document.getElementById('prediction-results-card');
        if (!cardEl) return;

        cardEl.classList.remove('hidden');

        const rec = data.records[0];

        // Subtitle
        const subTitle = document.getElementById('prediction-results-subtitle');
        if (subTitle) {
            subTitle.textContent = `${rec.target} projection for ${rec.region_name || rec.region} (${data.target_horizon})`;
        }

        // Badges
        const targetBadge = document.getElementById('prediction-target-badge');
        if (targetBadge) targetBadge.textContent = `Horizon: ${data.target_horizon}`;

        const baseBadge = document.getElementById('prediction-baseline-tag');
        if (baseBadge) baseBadge.textContent = `Baseline: ${data.latest_observation}`;

        // Variable & Region names
        const targetName = document.getElementById('prediction-target-name');
        if (targetName) targetName.textContent = rec.target;

        const regionName = document.getElementById('prediction-region-name');
        if (regionName) regionName.textContent = `Region: ${rec.region_name || rec.region}`;

        // Risk % and Lift
        const riskPctEl = document.getElementById('prediction-risk-pct');
        if (riskPctEl) {
            riskPctEl.textContent = (rec.risk_pct !== null && rec.risk_pct !== undefined) ? `${rec.risk_pct.toFixed(1)}%` : 'N/A';
        }

        const liftEl = document.getElementById('prediction-lift');
        if (liftEl) {
            liftEl.textContent = (rec.lift !== null && rec.lift !== undefined) ? `${rec.lift.toFixed(2)}x` : 'N/A';
        }

        // Tier badge
        const tierBadge = document.getElementById('prediction-tier-badge');
        if (tierBadge) {
            tierBadge.textContent = rec.tier || 'Unknown';
            if (rec.tier === 'High') {
                tierBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300';
            } else if (rec.tier === 'Elevated') {
                tierBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300';
            } else if (rec.tier === 'Low') {
                tierBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300';
            } else {
                tierBadge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-slate-200 text-slate-800 border border-slate-300';
            }
        }

        const tierVal = document.getElementById('prediction-tier-validation');
        if (tierVal) {
            if (rec.tier_validated) {
                tierVal.className = 'text-[10px] text-emerald-700 font-semibold';
                tierVal.textContent = '✓ Statistically Validated Tier';
            } else {
                tierVal.className = 'text-[10px] text-amber-700 font-semibold';
                tierVal.textContent = (rec.tier && rec.tier.includes('dry season')) 
                    ? '⚠️ Masked (Climatological Dry Season)' 
                    : '⚠️ Advisory Tier (Unvalidated)';
            }
        }

        // Skill Banner
        const skillBanner = document.getElementById('prediction-skill-banner');
        const skillDot = document.getElementById('prediction-skill-dot');
        const skillText = document.getElementById('prediction-skill-text');
        const skillMetric = document.getElementById('prediction-skill-metric');

        const isTemp = rec.variable_id === 'temperature_anomaly';
        if (skillBanner) {
            skillBanner.className = isTemp 
                ? 'p-3 rounded-lg bg-emerald-50/80 border border-emerald-200 text-xs text-emerald-950 flex flex-col sm:flex-row sm:items-center justify-between gap-2'
                : 'p-3 rounded-lg bg-amber-50/80 border border-amber-200 text-xs text-amber-950 flex flex-col sm:flex-row sm:items-center justify-between gap-2';
        }
        if (skillDot) {
            skillDot.className = isTemp ? 'w-2 h-2 rounded-full bg-emerald-500 shrink-0' : 'w-2 h-2 rounded-full bg-amber-500 shrink-0';
        }
        if (skillText) {
            skillText.textContent = isTemp 
                ? 'Temperature Model Skill: CONFIRMED (Test ROC-AUC: 0.753 vs Baseline 0.675, Diff: +0.079)'
                : 'Precipitation Model Skill: NO RELIABLE SKILL (Test ROC-AUC: 0.562 vs Baseline 0.520 - Advisory Only)';
        }
        if (skillMetric) {
            skillMetric.textContent = (data.model_metadata && data.model_metadata.validation_protocol) 
                ? data.model_metadata.validation_protocol 
                : 'Walk-Forward CV + Held-Out Test (2022–2024)';
        }

        // Narrative Interpretation
        const interpEl = document.getElementById('prediction-interpretation-text');
        if (interpEl) {
            interpEl.textContent = rec.interpretation;
        }

        const genAt = document.getElementById('prediction-generated-at');
        if (genAt) {
            genAt.textContent = `Generated: ${new Date().toLocaleTimeString()} (UTC ${new Date().getUTCHours()}:${new Date().getUTCMinutes()})`;
        }

        // Smooth scroll into view
        cardEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    initMapLabels() {
        this.regionsLayer = L.geoJSON(africaRegions, {
            attribution: 'Region boundaries &copy; Natural Earth',
            style: feature => ({
                color: '#ffffff',
                weight: 0,
                fillColor: feature.properties.color,
                fillOpacity: 0.65
            }),
            onEachFeature: (feature, layer) => {
                layer.on('click', () => this.selectPredefinedRegion(feature, layer));
            }
        }).addTo(this.map);

        this.regionLabelsLayer = L.layerGroup([
            ['North Africa', 25, 13],
            ['West Africa', 8, -5],
            ['Central<br>Africa', 1, 20],
            ['East Africa', 1, 36],
            ['Southern<br>Africa', -24, 23]
        ].map(([name, lat, lng]) => L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'earth-region-marker',
                html: `<span>${name}</span>`,
                iconSize: [0, 0]
            }),
            interactive: false,
            keyboard: false
        })));

        this.countryLabelsPane = this.map.createPane('earthCountryLabelsPane');
        this.countryLabelsPane.style.zIndex = 450;
        this.countryLabelsPane.style.pointerEvents = 'none';

        this.countryLabelsLayer = L.tileLayer(
            'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
            {
                attribution: 'Labels &copy; Esri and its contributors',
                maxZoom: 18,
                minZoom: 4,
                pane: 'earthCountryLabelsPane'
            }
        );

        this.map.on('zoomend', () => this.updateMapLabels());
        this.updateMapLabels();
    }

    updateMapLabels() {
        const zoom = this.map.getZoom();
        const showRegionLabels = zoom < 4;
        const showCountryLabels = this.currentBaseLayer === 'satellite' && zoom >= 4;

        if (showRegionLabels && !this.map.hasLayer(this.regionLabelsLayer)) {
            this.regionLabelsLayer.addTo(this.map);
        } else if (!showRegionLabels && this.map.hasLayer(this.regionLabelsLayer)) {
            this.map.removeLayer(this.regionLabelsLayer);
        }

        if (showCountryLabels && !this.map.hasLayer(this.countryLabelsLayer)) {
            this.countryLabelsLayer.addTo(this.map);
        } else if (!showCountryLabels && this.map.hasLayer(this.countryLabelsLayer)) {
            this.map.removeLayer(this.countryLabelsLayer);
        }
    }

    toggleBaseLayer() {
        if (this.currentBaseLayer === 'satellite') {
            this.map.removeLayer(this.satelliteLayer);
            this.map.addLayer(this.streetLayer);
            this.currentBaseLayer = 'streets';
        } else {
            this.map.removeLayer(this.streetLayer);
            this.map.addLayer(this.satelliteLayer);
            this.currentBaseLayer = 'satellite';
        }
        this.updateMapLabels();
    }

    initMiniMap() {
        const miniContainer = document.getElementById('earth-minimap');
        if (!miniContainer) return;

        try {
            this.miniMap = L.map(miniContainer, {
                center: [0, 17],
                zoom: 1,
                minZoom: 1,
                maxBounds: this.options.maxBounds,
                maxBoundsViscosity: 1,
                zoomControl: false,
                attributionControl: false,
                dragging: false,
                touchZoom: false,
                scrollWheelZoom: false,
                doubleClickZoom: false,
                boxZoom: false
            });

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 4,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(this.miniMap);

            this.miniMapRect = L.rectangle(this.map.getBounds(), {
                color: '#22c55e',
                weight: 1.5,
                fillColor: '#22c55e',
                fillOpacity: 0.25
            }).addTo(this.miniMap);

            this.map.on('move', () => {
                if (this.miniMap && this.miniMapRect) {
                    this.miniMapRect.setBounds(this.map.getBounds());
                }
            });
        } catch (err) {
            console.warn('MiniMap init warning:', err);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('earth-map')) {
        window.earthTrendMap = new EarthMap('earth-map');
    }
});
