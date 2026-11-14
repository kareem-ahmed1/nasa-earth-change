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

                <!-- Right Header Links & User Menu -->
                <div class="flex items-center gap-4 text-xs font-medium text-slate-600">
                    <a href="#about" class="hidden sm:flex items-center gap-1.5 hover:text-slate-900 transition-colors">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke-width="2" />
                            <line x1="12" y1="16" x2="12" y2="12" stroke-width="2" />
                            <line x1="12" y1="8" x2="12.01" y2="8" stroke-width="2" />
                        </svg>
                        <span>About</span>
                    </a>

                    <a href="#help" class="hidden sm:flex items-center gap-1.5 hover:text-slate-900 transition-colors">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke-width="2" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
                            <line x1="12" y1="17" x2="12.01" y2="17" stroke-width="2" />
                        </svg>
                        <span>Help</span>
                    </a>

                    <a href="#how-it-works" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 transition-all shadow-2xs">
                        <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <polygon points="5 3 19 12 5 21 5 3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        <span>How it works</span>
                    </a>

                    <!-- User Profile / Logout -->
                    <div class="flex items-center gap-2 pl-2 border-l border-slate-200">
                        <span class="text-xs font-semibold text-slate-700 hidden md:inline"><?php echo e(Auth::user()->name); ?></span>
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
                        <span>New Analysis</span>
                    </a>

                    <a href="#my-analyses" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                        <span>My Analyses</span>
                    </a>

                    <a href="#data-sources" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7c0-2-1.5-3-3.5-3h-9C5.5 4 4 5 4 7z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6" />
                        </svg>
                        <span>Data Sources</span>
                    </a>

                    <a href="#methodology" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke-width="2" />
                            <line x1="12" y1="16" x2="12" y2="12" stroke-width="2" />
                            <line x1="12" y1="8" x2="12.01" y2="8" stroke-width="2" />
                        </svg>
                        <span>Methodology</span>
                    </a>

                    <a href="#about-project" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" stroke-width="2" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3" />
                        </svg>
                        <span>About Project</span>
                    </a>
                </nav>

                <!-- Sidebar Footer: Demo Mode & Theme -->
                <div class="mt-8 space-y-4 pt-4 border-t border-slate-800 text-xs">
                    <div class="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80">
                        <div class="flex items-center gap-1.5 text-slate-300 font-bold mb-1">
                            <svg class="w-3.5 h-3.5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <circle cx="12" cy="12" r="10" stroke-width="2" />
                                <line x1="12" y1="16" x2="12" y2="12" stroke-width="2" />
                            </svg>
                            <span>Demo Mode</span>
                        </div>
                        <p class="text-[11px] text-slate-400 leading-relaxed">
                            This is a demonstration version. Data may be sample or pre-downloaded.
                        </p>
                        <a href="#demo" class="text-blue-400 hover:underline text-[11px] mt-1 inline-block">Learn more</a>
                    </div>

                    <!-- Theme Toggle Indicator -->
                    <div class="flex items-center justify-between text-slate-400 text-[11px] px-1">
                        <span>Theme</span>
                        <div class="flex items-center gap-1 bg-slate-950 p-1 rounded-full border border-slate-800">
                            <span class="w-5 h-5 rounded-full bg-blue-600 text-white flex items-center justify-center">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <circle cx="12" cy="12" r="5" stroke-width="2" />
                                    <line x1="12" y1="1" x2="12" y2="3" stroke-width="2" />
                                </svg>
                            </span>
                            <span class="w-5 h-5 rounded-full flex items-center justify-center text-slate-500">
                                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" stroke-width="2" />
                                </svg>
                            </span>
                        </div>
                    </div>
                </div>
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
                                <button type="button" class="text-slate-400 hover:text-slate-600" title="Variable Info">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <circle cx="12" cy="12" r="10" stroke-width="2" />
                                        <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" stroke-width="2" />
                                        <line x1="12" y1="17" x2="12.01" y2="17" stroke-width="2" />
                                    </svg>
                                </button>
                            </div>

                            <!-- Variable Select Box -->
                            <div class="relative">
                                <button type="button" class="w-full flex items-center justify-between p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-left text-xs font-semibold text-slate-800 shadow-2xs hover:border-slate-400">
                                    <div class="flex items-center gap-2">
                                        <span class="text-amber-500">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                            </svg>
                                        </span>
                                        <span>Land Surface Temperature (Day)</span>
                                    </div>
                                    <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <polyline points="6 9 12 15 18 9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                    </svg>
                                </button>
                            </div>

                            <p class="text-[11px] text-slate-500 mt-2 leading-relaxed">
                                Average land surface temperature during daytime.
                            </p>

                            <!-- Variable Metadata Table -->
                            <div class="mt-3 pt-3 border-t border-slate-100 space-y-1.5 text-[11px] text-slate-600">
                                <div class="flex items-center gap-2">
                                    <span class="text-slate-400 font-mono">🌡 Unit:</span>
                                    <span class="font-medium text-slate-800">°C</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="text-slate-400 font-mono">🛰 Source:</span>
                                    <span class="font-medium text-slate-800">Synthetic demo data (not NASA)</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="text-slate-400 font-mono">⏱ Temporal Resolution:</span>
                                    <span class="font-medium text-slate-800">Monthly (generated)</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="text-slate-400 font-mono">📅 Available:</span>
                                    <span class="font-medium text-slate-800">Demo range: 2015-01 to 2020-12</span>
                                </div>
                            </div>
                        </div>

                        <!-- 2. Select Time Period -->
                        <div class="bg-white rounded-xl p-4 sm:p-5 border border-slate-200 shadow-2xs">
                            <div class="flex items-center justify-between mb-3">
                                <h3 class="text-sm font-bold text-slate-900">2. Select Time Period</h3>
                                <button type="button" class="text-slate-400 hover:text-slate-600" title="Time Period Info">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <circle cx="12" cy="12" r="10" stroke-width="2" />
                                        <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" stroke-width="2" />
                                        <line x1="12" y1="17" x2="12.01" y2="17" stroke-width="2" />
                                    </svg>
                                </button>
                            </div>

                            <div class="space-y-3">
                                <div>
                                    <label class="block text-[11px] font-semibold text-slate-600 mb-1">Start Date</label>
                                    <div class="relative">
                                        <input id="analysis-start-date" type="text" value="2015-01-01" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono font-medium text-slate-800 focus:outline-none focus:border-blue-500" readonly />
                                        <span class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 pointer-events-none">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                                                <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" />
                                                <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" />
                                                <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                                            </svg>
                                        </span>
                                    </div>
                                </div>

                                <div>
                                    <label class="block text-[11px] font-semibold text-slate-600 mb-1">End Date</label>
                                    <div class="relative">
                                        <input id="analysis-end-date" type="text" value="2020-12-31" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs font-mono font-medium text-slate-800 focus:outline-none focus:border-blue-500" readonly />
                                        <span class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 pointer-events-none">
                                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke-width="2" />
                                                <line x1="16" y1="2" x2="16" y2="6" stroke-width="2" />
                                                <line x1="8" y1="2" x2="8" y2="6" stroke-width="2" />
                                                <line x1="3" y1="10" x2="21" y2="10" stroke-width="2" />
                                            </svg>
                                        </span>
                                    </div>
                                </div>

                                <div class="p-2 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-medium flex items-center gap-1.5">
                                    <svg class="w-4 h-4 text-emerald-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <circle cx="12" cy="12" r="10" stroke-width="2" />
                                        <polyline points="9 12 11 14 15 10" stroke-width="2" />
                                    </svg>
                                    <span>Selected period is within the demo range.</span>
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

                        <!-- Analyze Action Bar (Below the map, matching reference image) -->
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
                            <div class="flex items-center gap-3">
                                <button 
                                    type="button" 
                                    id="btn-analyze-execute"
                                    disabled
                                    class="flex items-center gap-2 px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm shadow-emerald-700/20 transition-all cursor-pointer"
                                >
                                    <svg class="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                                        <polygon points="5 3 19 12 5 21 5 3" />
                                    </svg>
                                    <span>Analyze</span>
                                </button>
                                <span id="analysis-status" role="status" class="text-xs text-slate-500 font-medium">
                                    Click an African region on the map, then select Analyze.
                                </span>
                            </div>

                            <button 
                                type="button" 
                                id="btn-reset-all"
                                onclick="window.earthTrendMap && window.earthTrendMap.clearRegion()"
                                class="flex items-center gap-1.5 px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 border border-slate-200 hover:border-slate-300 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
                            >
                                <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                <span>Reset All</span>
                            </button>
                        </div>

                        <!-- Results Section (Matching Reference Image) -->
                        <div id="analysis-results" class="hidden bg-white rounded-xl border border-slate-200 shadow-2xs p-5">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                                <div class="flex items-center gap-2">
                                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                    <h3 class="text-base font-bold text-slate-900">Results</h3>
                                </div>

                                <button type="button" class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-700 border border-slate-200 rounded-lg hover:bg-slate-50 shadow-2xs">
                                    <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                    </svg>
                                    <span>Download Result</span>
                                    <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <polyline points="6 9 12 15 18 9" />
                                    </svg>
                                </button>
                            </div>

                            <div class="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-200 text-[11px] text-amber-900">
                                Demo only: all values below are synthetic and are not NASA observations or scientific findings.
                            </div>

                            <!-- Results Tabs -->
                            <div class="flex items-center gap-1 border-b border-slate-200 pb-1 mb-5 text-xs font-semibold">
                                <button class="px-3.5 py-1.5 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs">Time Series</button>
                                <button class="px-3.5 py-1.5 text-slate-500 hover:text-slate-800">Summary</button>
                                <button class="px-3.5 py-1.5 text-slate-500 hover:text-slate-800">Map (Mean)</button>
                                <button class="px-3.5 py-1.5 text-slate-500 hover:text-slate-800">Details &amp; Source</button>
                            </div>

                            <!-- Results Grid (Time Series Chart + Trend Summary & Metadata) -->
                            <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">

                                <!-- Chart & Summary (Col 8) -->
                                <div class="xl:col-span-8 space-y-4">
                                    <div class="flex items-center justify-between">
                                        <div>
                                            <h4 class="text-xs font-bold text-slate-800">Average Land Surface Temperature (Day)</h4>
                                            <p id="analysis-period" class="text-[11px] text-slate-500">Select a region and run Analyze.</p>
                                        </div>
                                        <!-- Chart Tools -->
                                        <div class="flex items-center gap-1 text-slate-400 text-xs">
                                            <button class="p-1 hover:text-slate-700" title="Zoom in">🔍+</button>
                                            <button class="p-1 hover:text-slate-700" title="Zoom out">🔍-</button>
                                            <button class="p-1 hover:text-slate-700" title="Pan">✋</button>
                                            <button class="p-1 hover:text-slate-700" title="Reset">🏠</button>
                                        </div>
                                    </div>

                                    <!-- Chart Visual (SVG Time Series Line matching reference image) -->
                                    <div class="h-56 w-full border border-slate-100 rounded-lg p-2 bg-slate-50/50 flex flex-col justify-between">
                                        <svg id="analysis-chart" class="w-full h-full" viewBox="0 0 600 180" preserveAspectRatio="none"></svg>

                                    </div>

                                    <!-- Chart Legend -->
                                    <div class="flex items-center justify-center gap-6 text-[11px] font-medium text-slate-600">
                                        <div class="flex items-center gap-1.5">
                                            <span class="w-3 h-1 bg-sky-600 rounded"></span>
                                            <span>Synthetic monthly mean</span>
                                        </div>
                                        <div class="flex items-center gap-1.5">
                                            <span class="w-3 h-0.5 bg-sky-600 border-b border-dashed border-sky-600"></span>
                                            <span>Illustrative trend</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Trend Summary Card (Col 4) -->
                                <div class="xl:col-span-4 space-y-4">
                                    <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
                                        <h4 class="text-xs font-bold text-slate-900 mb-3">Trend Summary</h4>
                                        
                                        <div class="space-y-2.5 text-xs">
                                            <div>
                                                <span class="text-[10px] text-slate-400 uppercase font-mono block">Direction</span>
                                                <span id="analysis-direction" class="font-bold text-slate-700">
                                                    Awaiting analysis
                                                </span>
                                            </div>

                                            <div>
                                                <span class="text-[10px] text-slate-400 uppercase font-mono block">Illustrative trend (annual means)</span>
                                                <span id="analysis-slope" class="font-bold text-slate-800 font-mono">-- °C per year</span>
                                            </div>

                                            <div>
                                                <span class="text-[10px] text-slate-400 uppercase font-mono block">Mean temperature (synthetic)</span>
                                                <span id="analysis-mean" class="font-bold text-slate-800 font-mono">-- °C</span>
                                            </div>

                                            <div>
                                                <span class="text-[10px] text-slate-400 uppercase font-mono block">Synthetic observations</span>
                                                <span id="analysis-observation-count" class="font-bold text-slate-800 font-mono">--</span>
                                            </div>

                                            <div class="pt-2 border-t border-slate-200 text-[11px] text-slate-500">
                                                <div>Illustrative values only; no significance test.</div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Right Metadata Box (Data Source & Region) -->
                                    <div class="space-y-2 text-xs">
                                        <div class="p-3 rounded-lg border border-slate-200 bg-white">
                                            <div class="text-[10px] text-slate-400 uppercase font-mono">Data Source</div>
                                            <div id="analysis-source" class="font-semibold text-slate-800 text-[11px]">Synthetic demo data (not NASA)</div>
                                        </div>

                                        <div class="p-3 rounded-lg border border-slate-200 bg-white">
                                            <div class="text-[10px] text-slate-400 uppercase font-mono">Region</div>
                                            <div id="analysis-region-info" class="font-semibold text-slate-800 text-[11px]">Not analyzed</div>
                                            <a href="#view-map" onclick="window.earthTrendMap && window.earthTrendMap.currentLayer && window.earthTrendMap.map.flyToBounds(window.earthTrendMap.currentLayer.getBounds())" class="text-blue-600 hover:underline text-[10px] font-medium inline-block mt-0.5">View on Map</a>
                                        </div>

                                        <!-- Warnings & Notes -->
                                        <div class="p-3 rounded-lg bg-amber-50/60 border border-amber-200/80 text-[11px] text-amber-900 leading-relaxed">
                                            <div class="font-bold flex items-center gap-1 text-amber-800 mb-1">
                                                <span>⚠️</span> Warnings &amp; Notes
                                            </div>
                                            <ul class="list-disc list-inside space-y-0.5 text-[10px] text-amber-800">
                                                <li>Synthetic monthly values are generated for the interface demo.</li>
                                                <li>Do not use these values for research or decisions.</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>

                            </div>

                            <!-- Footer Attribution Note -->
                            <div class="mt-6 pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-400">
                                <span>ⓘ Demo results are synthetic and do not represent measured Earth observations.</span>
                                <span id="analysis-generated-at">Not run</span>
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
<?php /**PATH D:\laragon\www\nasa-earth-change\nasa-laravel\resources\views/dashboard.blade.php ENDPATH**/ ?>