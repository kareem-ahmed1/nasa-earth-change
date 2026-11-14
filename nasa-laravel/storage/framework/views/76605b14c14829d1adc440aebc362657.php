<!DOCTYPE html>
<html lang="<?php echo e(str_replace('_', '-', app()->getLocale())); ?>" class="light">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="<?php echo e(csrf_token()); ?>">

        <title>Earth Trend Explorer — Explore. Analyze. Understand Our Planet.</title>

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600,700,800&display=swap" rel="stylesheet" />

        <!-- Scripts & Styles -->
        <?php echo app('Illuminate\Foundation\Vite')(['resources/css/app.css', 'resources/js/app.js']); ?>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    </head>
    <body class="font-sans antialiased bg-[#f8fafc] text-slate-800 min-h-screen flex flex-col selection:bg-emerald-500 selection:text-white">

        <!-- Top Header Navigation (Matching Reference Image) -->
        <header class="w-full bg-white border-b border-slate-200 px-4 sm:px-6 py-2.5 sticky top-0 z-40 shadow-xs">
            <div class="max-w-[1720px] mx-auto flex items-center justify-between">
                <!-- Brand / Logo -->
                <div class="flex items-center gap-3">
                    <!-- Earth Globe Logo -->
                    <div class="w-10 h-10 rounded-full bg-emerald-600 flex items-center justify-center text-white shadow-md shadow-emerald-600/20 shrink-0">
                        <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                            <circle cx="12" cy="12" r="10" />
                            <path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
                        </svg>
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-extrabold text-lg text-slate-900 tracking-tight">Earth Trend Explorer</span>
                        </div>
                        <p class="text-[11px] text-slate-500 font-medium">Explore. Analyze. Understand Our Planet.</p>
                    </div>
                </div>

                <!-- Center Title & Subtitle -->
                <div class="hidden xl:block text-center">
                    <h2 class="text-sm font-bold text-slate-800">Analyze changes in Earth system variables</h2>
                    <p class="text-xs text-slate-500">Select a variable, time period and region to discover trends in our changing planet.</p>
                </div>




                    <!-- User Profile / Logout -->
                    <div class="flex items-center gap-2 pl-2 border-l border-slate-200">
                        <span class="text-xs font-semibold text-slate-700 hidden md:inline"><?php echo e(Auth::user()?->name ?? 'Researcher'); ?></span>
                        <form method="POST" action="<?php echo e(route('logout')); ?>" class="inline">
                            <?php echo csrf_field(); ?>
                            <button type="submit" class="text-xs text-slate-400 hover:text-rose-600 transition-colors cursor-pointer" title="Log Out">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Body (Sidebar + Content) -->
        <div class="flex-1 max-w-[1720px] w-full mx-auto flex flex-col lg:flex-row">

            <!-- Left Fixed Sidebar (Matching Reference Image) -->
            <aside class="w-full lg:w-56 bg-slate-900 text-slate-300 p-4 shrink-0 flex flex-col justify-between border-r border-slate-800">
                <!-- Sidebar Nav Items -->
                <nav class="space-y-1">
                    <a href="<?php echo e(url('/')); ?>" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                        </svg>
                        <span>Home</span>
                    </a>

                    <a href="<?php echo e(route('dashboard')); ?>" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold text-emerald-400 bg-slate-800 border-l-3 border-emerald-500 shadow-sm transition-colors">
                        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span>Analysis</span>
                    </a>
                </nav>


            </aside>

            <!-- Main Work Area (Left Controls + Right Map & Results) -->
            <main class="flex-1 p-4 sm:p-6 lg:p-7 overflow-x-hidden">
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

                    <!-- Left Column: Controls (1. Variable, 2. Time Period, 3. Select Region) -->
                    <div class="lg:col-span-4 xl:col-span-3 space-y-6">

                        <!-- 1. Select Variable -->
                        <div class="bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-2xs">
                            <div class="flex items-center justify-between mb-3">
                                <h3 class="text-sm font-bold text-slate-900">1. Select Variable</h3>
                                <span class="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">NASA Data</span>
                            </div>

                            <!-- Variable Selection Radio Buttons -->
                            <div class="grid grid-cols-1 gap-2 mb-3">
                                <button
                                    type="button"
                                    id="var-btn-temp"
                                    onclick="window.earthTrendMap && window.earthTrendMap.setVariable('temperature_anomaly')"
                                    class="flex items-center justify-between p-2.5 rounded-lg border text-left text-xs font-semibold transition-all cursor-pointer bg-emerald-50/70 border-emerald-500 text-emerald-950 ring-1 ring-emerald-500/30"
                                >
                                    <div class="flex items-center gap-2">
                                        <span class="w-2.5 h-2.5 rounded-full bg-rose-500 shrink-0"></span>
                                        <span>Surface Temperature Anomaly</span>
                                    </div>
                                    <span class="text-[11px] font-mono text-slate-500 font-normal">°C</span>
                                </button>

                                <button
                                    type="button"
                                    id="var-btn-precip"
                                    onclick="window.earthTrendMap && window.earthTrendMap.setVariable('precipitation_mm')"
                                    class="flex items-center justify-between p-2.5 rounded-lg border text-left text-xs font-semibold transition-all cursor-pointer bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100"
                                >
                                    <div class="flex items-center gap-2">
                                        <span class="w-2.5 h-2.5 rounded-full bg-sky-500 shrink-0"></span>
                                        <span>Precipitation (Daily Rate)</span>
                                    </div>
                                    <span class="text-[11px] font-mono text-slate-500 font-normal">mm/day</span>
                                </button>
                            </div>

                            <p id="var-desc" class="text-[11px] text-slate-600 leading-relaxed min-h-[32px]">
                                Monthly surface temperature anomaly relative to regional base periods.
                            </p>

                            <!-- Variable Metadata Table -->
                            <div class="mt-3 pt-3 border-t border-slate-100 space-y-1.5 text-[11px] text-slate-600">
                                <div class="flex items-center justify-between">
                                    <span class="text-slate-400 font-mono">Measurement Unit:</span>
                                    <span id="var-meta-unit" class="font-bold text-slate-800 font-mono">°C</span>
                                </div>
                                <div class="flex items-start justify-between gap-2">
                                    <span class="text-slate-400 font-mono shrink-0">Data Source:</span>
                                    <span id="var-meta-source" class="font-medium text-slate-800 text-right text-[10px]">NASA GISTEMP v4</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span class="text-slate-400 font-mono">Temporal Resolution:</span>
                                    <span id="var-meta-resolution" class="font-medium text-slate-800">Monthly</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span class="text-slate-400 font-mono">Coverage:</span>
                                    <span id="var-meta-coverage" class="font-bold text-emerald-700 font-mono">2004–2024 (21 Years)</span>
                                </div>
                            </div>
                        </div>

                        <!-- 2. Select Time Period -->
                        <div class="bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-2xs">
                            <div class="flex items-center justify-between mb-3">
                                <h3 class="text-sm font-bold text-slate-900">2. Select Time Period</h3>
                                <span class="text-[10px] font-mono text-slate-400">Coverage: 2004–2024</span>
                            </div>

                            <div class="space-y-3">
                                <div class="grid grid-cols-2 gap-3">
                                    <div>
                                        <label for="analysis-start-year" class="block text-[11px] font-semibold text-slate-600 mb-1">Start Year</label>
                                        <select
                                            id="analysis-start-year"
                                            onchange="window.earthTrendMap && window.earthTrendMap.onDateChange()"
                                            class="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-mono font-semibold text-slate-800 focus:outline-none focus:border-emerald-500 focus:bg-white"
                                        >
                                            <?php for($y = 2004; $y <= 2024; $y++): ?>
                                                <option value="<?php echo e($y); ?>" <?php echo e($y === 2004 ? 'selected' : ''); ?>><?php echo e($y); ?></option>
                                            <?php endfor; ?>
                                        </select>
                                    </div>

                                    <div>
                                        <label for="analysis-end-year" class="block text-[11px] font-semibold text-slate-600 mb-1">End Year</label>
                                        <select
                                            id="analysis-end-year"
                                            onchange="window.earthTrendMap && window.earthTrendMap.onDateChange()"
                                            class="w-full bg-slate-50 border border-slate-300 rounded-lg px-2.5 py-2 text-xs font-mono font-semibold text-slate-800 focus:outline-none focus:border-emerald-500 focus:bg-white"
                                        >
                                            <?php for($y = 2004; $y <= 2024; $y++): ?>
                                                <option value="<?php echo e($y); ?>" <?php echo e($y === 2024 ? 'selected' : ''); ?>><?php echo e($y); ?></option>
                                            <?php endfor; ?>
                                        </select>
                                    </div>
                                </div>

                                <div id="date-validation-badge" class="p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1.5">
                                    <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <circle cx="12" cy="12" r="10" stroke-width="2" />
                                        <polyline points="9 12 11 14 15 10" stroke-width="2" />
                                    </svg>
                                    <span id="date-validation-text">Selected period covers 21 full observational years (2004–2024).</span>
                                </div>
                            </div>
                        </div>

                        <!-- 3. Select Region (Connected to Leaflet Map) -->
                        <div class="bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-2xs">
                            <div class="flex items-center justify-between mb-2">
                                <h3 class="text-sm font-bold text-slate-900">3. Select Region</h3>
                                <button type="button" class="text-slate-400 hover:text-slate-600" title="Region Selection Info">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <circle cx="12" cy="12" r="10" stroke-width="2" />
                                        <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" stroke-width="2" />
                                        <line x1="12" y1="17" x2="12.01" y2="17" stroke-width="2" />
                                    </svg>
                                </button>
                            </div>

                            <p class="text-[11px] text-slate-500 mb-3.5">
                                Click one of the colored regions on the map to select it for analysis.
                            </p>

                            <div class="grid grid-cols-2 gap-x-3 gap-y-1.5 mb-3 text-[10px] text-slate-600">
                                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-[#d5a837]"></span>North Africa</span>
                                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-[#159451]"></span>West Africa</span>
                                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-[#7950a6]"></span>Central Africa</span>
                                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-[#397faa]"></span>East Africa</span>
                                <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-sm bg-[#b84537]"></span>Southern Africa</span>
                            </div>

                            <!-- Clear Selection Button -->
                            <button
                                type="button"
                                id="btn-clear-selection"
                                class="w-full flex items-center justify-center gap-1.5 px-3 py-1.5 bg-white hover:bg-rose-50 border border-rose-200 text-rose-600 font-medium text-xs rounded-lg transition-colors cursor-pointer"
                            >
                                <svg class="w-3.5 h-3.5 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                                <span>Clear Selection</span>
                            </button>

                            <!-- Selected Region Details Card (matching reference image) -->
                            <div id="selected-region-card" class="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200 relative">
                                <div class="flex items-center justify-between mb-2">
                                    <span id="selected-region-name" class="text-xs font-bold text-slate-900">Selected Region</span>
                                    <span class="w-4 h-4 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                        </svg>
                                    </span>
                                </div>

                                <div class="flex items-center justify-between">
                                    <div class="space-y-1">
                                        <div>
                                            <span class="text-[10px] text-slate-400 uppercase font-mono block">Area</span>
                                            <span id="selected-region-area" class="text-xs font-bold text-slate-800 font-mono">125,430 km²</span>
                                        </div>
                                        <div>
                                            <span class="text-[10px] text-slate-400 uppercase font-mono block">Bounds (W, S, E, N)</span>
                                            <span id="selected-region-bounds" class="text-[10px] font-mono text-slate-600 block">44.08°, 23.56°, 47.01°, 26.43°</span>
                                        </div>
                                    </div>

                                    <!-- Mini SVG Polygon Preview Shape -->
                                    <div class="w-12 h-12 rounded-lg bg-emerald-100/60 border border-emerald-300 flex items-center justify-center p-1 shrink-0">
                                        <svg class="w-10 h-10" viewBox="0 0 48 48">
                                            <path
                                                id="selected-region-svg-path"
                                                d="M 10 12 L 38 8 L 42 36 L 10 40 Z"
                                                fill="#86efac"
                                                fill-opacity="0.6"
                                                stroke="#22c55e"
                                                stroke-width="2"
                                            />
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            <!-- Empty Region Placeholder (Hidden when region exists) -->
                            <div id="selected-region-empty" class="hidden mt-4 p-3.5 rounded-xl border border-dashed border-slate-300 text-center text-xs text-slate-400">
                                No region selected. Click one of the colored regions on the map.
                            </div>
                        </div>

                    </div>

                    <!-- Right Column: Interactive Map Component & Results Section -->
                    <div class="lg:col-span-8 xl:col-span-9 space-y-5">

                        <!-- The Map Component -->
                        <?php if (isset($component)) { $__componentOriginal319c8ddb0b98d43996b85482af6f1b93 = $component; } ?>
<?php if (isset($attributes)) { $__attributesOriginal319c8ddb0b98d43996b85482af6f1b93 = $attributes; } ?>
<?php $component = Illuminate\View\AnonymousComponent::resolve(['view' => 'components.earth-map','data' => []] + (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag ? $attributes->all() : [])); ?>
<?php $component->withName('earth-map'); ?>
<?php if ($component->shouldRender()): ?>
<?php $__env->startComponent($component->resolveView(), $component->data()); ?>
<?php if (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag): ?>
<?php $attributes = $attributes->except(\Illuminate\View\AnonymousComponent::ignoredParameterNames()); ?>
<?php endif; ?>
<?php $component->withAttributes([]); ?>
<?php echo $__env->renderComponent(); ?>
<?php endif; ?>
<?php if (isset($__attributesOriginal319c8ddb0b98d43996b85482af6f1b93)): ?>
<?php $attributes = $__attributesOriginal319c8ddb0b98d43996b85482af6f1b93; ?>
<?php unset($__attributesOriginal319c8ddb0b98d43996b85482af6f1b93); ?>
<?php endif; ?>
<?php if (isset($__componentOriginal319c8ddb0b98d43996b85482af6f1b93)): ?>
<?php $component = $__componentOriginal319c8ddb0b98d43996b85482af6f1b93; ?>
<?php unset($__componentOriginal319c8ddb0b98d43996b85482af6f1b93); ?>
<?php endif; ?>

                        <!-- Analyze & Predict Action Bar (Below the map, matching reference image) -->
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
                            <div class="flex flex-wrap items-center gap-2.5">
                                <button
                                    type="button"
                                    id="btn-analyze-execute"
                                    onclick="window.earthTrendMap && window.earthTrendMap.runScientificAnalysis()"
                                    disabled
                                    class="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold text-xs rounded-lg shadow-sm shadow-emerald-700/20 transition-all cursor-pointer"
                                >
                                    <svg id="btn-analyze-icon" class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                                        <polygon points="5 3 19 12 5 21 5 3" />
                                    </svg>
                                    <svg id="btn-analyze-spinner" class="hidden animate-spin w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                                    </svg>
                                    <span id="btn-analyze-label">Analyze Historical Trend</span>
                                </button>

                                <button
                                    type="button"
                                    id="btn-predict-execute"
                                    onclick="window.earthTrendMap && window.earthTrendMap.runPrediction()"
                                    disabled
                                    class="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white font-bold text-xs rounded-lg shadow-sm shadow-indigo-700/20 transition-all cursor-pointer"
                                >
                                    <svg id="btn-predict-icon" class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                                        <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
                                    </svg>
                                    <svg id="btn-predict-spinner" class="hidden animate-spin w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                                    </svg>
                                    <span id="btn-predict-label">Predict Next Month (Jan 2025)</span>
                                </button>

                                <span id="analysis-status" role="status" class="text-xs text-slate-500 font-medium">
                                    Click an African region on the map, then select Analyze or Predict.
                                </span>
                            </div>

                            <button
                                type="button"
                                id="btn-reset-all"
                                onclick="window.earthTrendMap && window.earthTrendMap.clearRegion()"
                                class="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 border border-slate-200 hover:border-slate-300 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer shrink-0"
                            >
                                <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                <span>Reset All</span>
                            </button>
                        </div>

                        <!-- Results Section (NASA Observation Data & Mann-Kendall Trend) -->
                        <div id="analysis-results" class="hidden bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-5">

                            <!-- Header with Scientific Verification Badge -->
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                                <div class="flex items-center gap-2.5">
                                    <div class="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 class="text-base font-bold text-slate-900">Scientific Analysis Results</h3>
                                        <p id="analysis-results-subtitle" class="text-xs text-slate-500">Surface Temperature Anomaly across North Africa (2004–2024)</p>
                                    </div>
                                </div>

                                <div class="flex items-center gap-2">
                                    <span id="analysis-provenance-tag" class="text-[11px] font-mono font-medium px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                                        NASA Satellite Observations
                                    </span>
                                    <button
                                        type="button"
                                        onclick="window.print()"
                                        class="flex items-center gap-1.5 px-3 py-1 text-xs font-semibold text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50 shadow-2xs cursor-pointer"
                                    >
                                        <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                        </svg>
                                        <span>Export</span>
                                    </button>
                                </div>
                            </div>

                            <!-- Scientific Integrity Banner -->
                            <div class="p-3 rounded-lg bg-emerald-50/80 border border-emerald-200 text-xs text-emerald-950 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full bg-emerald-500 shrink-0"></span>
                                    <span>Verified historical data: <strong>1,260 monthly NASA observations</strong> compiled from GISTEMP v4 and MERRA-2.</span>
                                </div>
                                <span class="text-[10px] text-emerald-700 font-mono">Statistical Method: Mann-Kendall &amp; Sen's Slope</span>
                            </div>

                            <!-- Results Grid (Time Series Chart + Trend Summary & Metadata) -->
                            <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">

                                <!-- Chart & Summary (Col 8) -->
                                <div class="xl:col-span-8 space-y-4">
                                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                                        <div>
                                            <h4 id="chart-variable-title" class="text-xs font-bold text-slate-800">Monthly Time Series &amp; Long-Term Trend</h4>
                                            <p id="analysis-period" class="text-[11px] text-slate-500">2004–2024</p>
                                        </div>
                                        
                                        <!-- Chart Type Selector Dropdown -->
                                        <div class="flex items-center gap-2">
                                            <label for="chart-type-select" class="text-[11px] font-bold text-slate-600 shrink-0">Chart type:</label>
                                            <select 
                                                id="chart-type-select" 
                                                onchange="window.earthTrendMap && window.earthTrendMap.onChartTypeChange(this.value)"
                                                class="bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-slate-800 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 shadow-2xs cursor-pointer"
                                            >
                                                <option value="trending" selected>Trending</option>
                                                <option value="mann_kendall_sen">Mann-Kendall / Sen's slope</option>
                                                <option value="correlation">Correlation</option>
                                                <option value="linear_regression">Linear Regression</option>
                                                <option value="regression">Regression</option>
                                            </select>
                                        </div>
                                    </div>

                                    <!-- Plotly Time Series Chart Container -->
                                    <div class="w-full bg-slate-50/70 border border-slate-200 rounded-xl p-2 min-h-[320px] relative">
                                        <div id="chart-loading-overlay" class="hidden absolute inset-0 bg-white/70 backdrop-blur-xs flex items-center justify-center z-10 rounded-xl">
                                            <div class="flex items-center gap-2 text-xs font-bold text-slate-700">
                                                <svg class="animate-spin w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24">
                                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                                                </svg>
                                                <span>Rendering chart...</span>
                                            </div>
                                        </div>
                                        <div id="plotly-timeseries" class="w-full h-80"></div>
                                    </div>
                                    
                                    <!-- One short plain-language line explaining what the chart shows -->
                                    <p id="chart-quick-explainer" class="text-[11px] text-slate-500 italic px-1"></p>

                                    <!-- Collapsible "How to read this chart" Panel -->
                                    <div 
                                        x-data="{ open: window.innerWidth >= 1024 }" 
                                        class="rounded-xl border border-slate-200 bg-white overflow-hidden shadow-2xs"
                                    >
                                        <button 
                                            type="button" 
                                            @click="open = !open" 
                                            :aria-expanded="open.toString()" 
                                            aria-controls="chart-guide-body"
                                            class="w-full flex items-center justify-between px-4 py-3 bg-slate-50/70 hover:bg-slate-100/80 text-left transition-colors cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                                        >
                                            <div class="flex items-center gap-2">
                                                <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                <span class="text-xs font-bold text-slate-800">How to read this chart</span>
                                                <span id="chart-guide-type-badge" class="ml-1 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-200 text-slate-700 font-semibold">Trending</span>
                                            </div>
                                            <div class="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
                                                <span x-text="open ? 'Hide guide' : 'Show guide'" class="text-[11px]"></span>
                                                <svg 
                                                    class="w-4 h-4 text-slate-400 transition-transform duration-200" 
                                                    :class="open ? 'rotate-180' : ''" 
                                                    fill="none" 
                                                    stroke="currentColor" 
                                                    viewBox="0 0 24 24"
                                                >
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                                                </svg>
                                            </div>
                                        </button>

                                        <div 
                                            id="chart-guide-body" 
                                            x-show="open" 
                                            x-transition:enter="transition ease-out duration-150"
                                            x-transition:enter-start="opacity-0 -translate-y-1"
                                            x-transition:enter-end="opacity-100 translate-y-0"
                                            x-transition:leave="transition ease-in duration-100"
                                            x-transition:leave-start="opacity-100 translate-y-0"
                                            x-transition:leave-end="opacity-0 -translate-y-1"
                                            class="p-4 space-y-3.5 border-t border-slate-200/80 text-xs"
                                        >
                                            <!-- Section 1: How to read the chart (Technical Static Description) -->
                                            <div>
                                                <div class="text-[10px] uppercase font-mono tracking-wider font-bold text-slate-400 mb-1 flex items-center gap-1.5">
                                                    <span>1. Guide &amp; Visual Representation</span>
                                                </div>
                                                <p id="chart-guide-how-to-read" class="text-xs text-slate-700 leading-relaxed">
                                                    Select an African region and run an analysis to view visual guidance.
                                                </p>
                                            </div>

                                            <!-- Section 2: Result for the current selection (Dynamic API Synthesis) -->
                                            <div class="pt-2.5 border-t border-slate-100">
                                                <div class="text-[10px] uppercase font-mono tracking-wider font-bold text-slate-400 mb-1 flex items-center gap-1.5">
                                                    <span>2. Result for Current Selection</span>
                                                </div>
                                                <p id="chart-guide-current-result" class="text-xs font-medium text-slate-900 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                                                    No result available for this selection.
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Chart Footnote & Plain-Language Interpretation -->
                                    <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-2">
                                        <div class="font-bold text-slate-900 flex items-center gap-1.5">
                                            <span>📊</span> Scientific Interpretation
                                        </div>
                                        <p id="analysis-plain-language" class="text-xs text-slate-700 leading-relaxed">
                                            Awaiting analysis.
                                        </p>
                                    </div>
                                </div>

                                <!-- Statistical Metrics Card (Col 4) -->
                                <div class="xl:col-span-4 space-y-4">

                                    <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3.5">
                                        <h4 class="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">Statistical Test Results</h4>

                                        <!-- Trend Direction Badge -->
                                        <div>
                                            <span class="text-[10px] text-slate-400 uppercase font-mono block mb-1">Detected Trend</span>
                                            <div id="analysis-direction-badge" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-slate-200 text-slate-800">
                                                Awaiting analysis
                                            </div>
                                        </div>

                                        <!-- Sen's Slope Rate -->
                                        <div>
                                            <span class="text-[10px] text-slate-400 uppercase font-mono block">Estimated Rate of Change (Sen's Slope)</span>
                                            <div id="analysis-slope-decade" class="text-base font-extrabold text-slate-900 font-mono">--</div>
                                            <div id="analysis-slope-year" class="text-[11px] text-slate-500 font-mono">--</div>
                                        </div>

                                        <!-- Statistical Significance Verdict -->
                                        <div class="p-3 rounded-lg bg-white border border-slate-200 space-y-2">
                                            <span class="text-[10px] text-slate-400 uppercase font-mono block">Statistical Significance (α = 0.05)</span>
                                            <div id="analysis-significance-badge" class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-bold bg-slate-100 text-slate-700">
                                                Not Assessed
                                            </div>
                                            <div class="text-[11px] text-slate-600 space-y-1 pt-1 font-mono">
                                                <div class="flex justify-between">
                                                    <span class="text-slate-400">Exact p-value:</span>
                                                    <span id="analysis-p-value" class="font-bold text-slate-800">--</span>
                                                </div>
                                                <div class="flex justify-between">
                                                    <span class="text-slate-400">Kendall's tau (τ):</span>
                                                    <span id="analysis-kendall-tau" class="font-bold text-slate-800">--</span>
                                                </div>
                                                <div class="flex justify-between">
                                                    <span class="text-slate-400">Annual Samples (n):</span>
                                                    <span id="analysis-sample-size" class="font-bold text-slate-800">--</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="text-[10px] text-slate-500 italic">
                                            Test: Mann-Kendall non-parametric test on annual aggregates. Null hypothesis (H₀: no monotonic trend) rejected when p &lt; 0.05.
                                        </div>
                                    </div>

                                    <!-- Provenance & Traceability Box -->
                                    <div class="space-y-2 text-xs">
                                        <div class="p-3 rounded-lg border border-slate-200 bg-white">
                                            <div class="text-[10px] text-slate-400 uppercase font-mono">Data Source &amp; Sensor</div>
                                            <div id="analysis-source" class="font-semibold text-slate-800 text-[11px] mt-0.5">NASA GISTEMP v4 / MERRA-2</div>
                                        </div>

                                        <div class="p-3 rounded-lg border border-slate-200 bg-white">
                                            <div class="text-[10px] text-slate-400 uppercase font-mono">Region &amp; Geographic Scope</div>
                                            <div id="analysis-region-info" class="font-semibold text-slate-800 text-[11px] mt-0.5">Select a region</div>
                                        </div>


                                    </div>

                                </div>

                            </div>

                            <!-- Footer Attribution Note -->
                            <div class="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400">
                                <span>Traceable to NASA satellite archives &amp; SciPy non-parametric statistical engine.</span>
                                <span id="analysis-generated-at">Ready</span>
                            </div>
                        </div>

                        <!-- ML Prediction Section (Model 1 v6 - Next Month Forecasting) -->
                        <div id="prediction-results-card" class="hidden bg-white rounded-xl border border-slate-200 shadow-2xs p-5 space-y-5">

                            <!-- Header with Model Badge -->
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                                <div class="flex items-center gap-2.5">
                                    <div class="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center shrink-0">
                                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
                                        </svg>
                                    </div>
                                    <div>
                                        <h3 class="text-base font-bold text-slate-900">Next Month Predictive Risk Forecast</h3>
                                        <p id="prediction-results-subtitle" class="text-xs text-slate-500">Machine learning projection for January 2025</p>
                                    </div>
                                </div>

                                <div class="flex items-center gap-2">
                                    <span id="prediction-target-badge" class="text-[11px] font-mono font-medium px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-800 border border-indigo-200">
                                        Horizon: 2025-01
                                    </span>
                                    <span id="prediction-baseline-tag" class="text-[11px] font-mono font-medium px-2.5 py-1 rounded-md bg-slate-50 text-slate-600 border border-slate-200">
                                        Baseline: 2024-12
                                    </span>
                                </div>
                            </div>

                            <!-- Model Skill & Validation Status Banner -->
                            <div id="prediction-skill-banner" class="p-3 rounded-lg bg-indigo-50/80 border border-indigo-200 text-xs text-indigo-950 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div class="flex items-center gap-2">
                                    <span id="prediction-skill-dot" class="w-2 h-2 rounded-full bg-indigo-500 shrink-0"></span>
                                    <span id="prediction-skill-text">Model 1 v6 Walk-Forward Cross Validation</span>
                                </div>
                                <span id="prediction-skill-metric" class="text-[10px] text-indigo-700 font-mono">Test ROC-AUC: 0.753 (+0.079 vs baseline)</span>
                            </div>

                            <!-- Key Metrics Cards Grid -->
                            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">

                                <!-- Risk Tier Card -->
                                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                                    <span class="text-[10px] text-slate-400 uppercase font-mono block">Projected Risk Tier</span>
                                    <div id="prediction-tier-badge" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-slate-200 text-slate-800">
                                        --
                                    </div>
                                    <p id="prediction-tier-validation" class="text-[10px] text-slate-500 font-medium">Validated Tier</p>
                                </div>

                                <!-- Probability Card -->
                                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                                    <span class="text-[10px] text-slate-400 uppercase font-mono block">Exceedance Probability</span>
                                    <div id="prediction-risk-pct" class="text-2xl font-black text-slate-900 font-mono">--%</div>
                                    <p class="text-[10px] text-slate-500">Likelihood of top-decile extreme anomaly</p>
                                </div>

                                <!-- Lift Card -->
                                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                                    <span class="text-[10px] text-slate-400 uppercase font-mono block">Baseline Risk Lift</span>
                                    <div id="prediction-lift" class="text-2xl font-black text-indigo-700 font-mono">--x</div>
                                    <p class="text-[10px] text-slate-500">Relative risk multiplier over climatology</p>
                                </div>

                                <!-- Target Variable Card -->
                                <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
                                    <span class="text-[10px] text-slate-400 uppercase font-mono block">Forecast Target</span>
                                    <div id="prediction-target-name" class="text-sm font-bold text-slate-900">Temperature Anomaly</div>
                                    <p id="prediction-region-name" class="text-[10px] text-slate-500">Region: --</p>
                                </div>

                            </div>

                            <!-- Narrative Interpretation Box -->
                            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-2">
                                <div class="font-bold text-slate-900 flex items-center gap-1.5">
                                    <span>🧠</span> Model Interpretation &amp; Diagnostic Narrative
                                </div>
                                <p id="prediction-interpretation-text" class="text-xs text-slate-700 leading-relaxed font-sans">
                                    Awaiting prediction execution.
                                </p>
                            </div>

                            <!-- Footer Attribution -->
                            <div class="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400">
                                <span>Model 1 v6 Frozen Engine · Ridge / Logistic Calibration with Walk-Forward Cross Validation</span>
                                <span id="prediction-generated-at">Ready</span>
                            </div>

                        </div>

                    </div>

                </div>
            </main>
        </div>

        <!-- Footer -->
        <footer class="w-full bg-slate-900 border-t border-slate-800 py-3.5 px-4 sm:px-6 text-xs text-slate-400 font-medium">
            <div class="max-w-[1720px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center">
                <span>Earth Trend Explorer is a demonstration project for educational and research purposes.</span>
                <span>© 2024 Earth Trend Explorer Team</span>
                <div class="flex items-center gap-4 text-slate-400 text-xs">
                    <a href="#privacy" class="hover:underline">Privacy Policy</a>
                    <a href="#terms" class="hover:underline">Terms of Use</a>
                    <a href="#contact" class="hover:underline">Contact</a>
                </div>
            </div>
        </footer>

    </body>
</html>
<?php /**PATH D:\laragon\www\nasa-earth-change\nasa-earth-change\nasa-laravel\resources\views/dashboard.blade.php ENDPATH**/ ?>