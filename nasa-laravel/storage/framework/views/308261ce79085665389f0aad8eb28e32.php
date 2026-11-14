<!DOCTYPE html>
<html lang="<?php echo e(str_replace('_', '-', app()->getLocale())); ?>" class="light">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title><?php echo e(config('app.name', 'NASA Earth Change')); ?> — Global Earth Science & Climate Telemetry</title>

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600,700,800,900&display=swap" rel="stylesheet" />

        <!-- Styles / Scripts -->
        <?php echo app('Illuminate\Foundation\Vite')(['resources/css/app.css', 'resources/js/app.js']); ?>
    </head>
    <body class="landing-light font-sans text-slate-700 antialiased bg-slate-50 min-h-screen relative flex flex-col justify-between selection:bg-emerald-500 selection:text-white overflow-x-hidden">

        <!-- Top Navigation Header -->
        <header class="relative z-30 w-full border-b border-cyan-500/15 bg-slate-950/60 backdrop-blur-md px-4 sm:px-8 py-3.5 sticky top-0">
            <div class="max-w-7xl mx-auto flex items-center justify-between">
                <!-- Brand / Logo -->
                <a href="/" class="flex items-center gap-2 group transition-opacity hover:opacity-90">
                    <?php if (isset($component)) { $__componentOriginal8892e718f3d0d7a916180885c6f012e7 = $component; } ?>
<?php if (isset($attributes)) { $__attributesOriginal8892e718f3d0d7a916180885c6f012e7 = $attributes; } ?>
<?php $component = Illuminate\View\AnonymousComponent::resolve(['view' => 'components.application-logo','data' => ['class' => 'h-9 sm:h-10 w-auto']] + (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag ? $attributes->all() : [])); ?>
<?php $component->withName('application-logo'); ?>
<?php if ($component->shouldRender()): ?>
<?php $__env->startComponent($component->resolveView(), $component->data()); ?>
<?php if (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag): ?>
<?php $attributes = $attributes->except(\Illuminate\View\AnonymousComponent::ignoredParameterNames()); ?>
<?php endif; ?>
<?php $component->withAttributes(['class' => 'h-9 sm:h-10 w-auto']); ?>
<?php echo $__env->renderComponent(); ?>
<?php endif; ?>
<?php if (isset($__attributesOriginal8892e718f3d0d7a916180885c6f012e7)): ?>
<?php $attributes = $__attributesOriginal8892e718f3d0d7a916180885c6f012e7; ?>
<?php unset($__attributesOriginal8892e718f3d0d7a916180885c6f012e7); ?>
<?php endif; ?>
<?php if (isset($__componentOriginal8892e718f3d0d7a916180885c6f012e7)): ?>
<?php $component = $__componentOriginal8892e718f3d0d7a916180885c6f012e7; ?>
<?php unset($__componentOriginal8892e718f3d0d7a916180885c6f012e7); ?>
<?php endif; ?>
                </a>

                <!-- Navigation Links / CTAs -->
                <nav class="flex items-center gap-3 sm:gap-6 text-xs sm:text-sm font-medium">
                    <!-- Desktop Nav Links -->
                    <div class="hidden md:flex items-center gap-6 text-slate-300">
                        <a href="#vital-signs" class="hover:text-cyan-400 transition-colors">Vital Signs</a>
                        <a href="#constellations" class="hover:text-cyan-400 transition-colors">Satellites</a>
                        <a href="#capabilities" class="hover:text-cyan-400 transition-colors">Capabilities</a>
                        <a href="#stories" class="hover:text-cyan-400 transition-colors">Case Studies</a>
                    </div>

                    <!-- Auth State Navigation -->
                    <?php if(Route::has('login')): ?>
                        <div class="flex items-center gap-2 sm:gap-3">
                            <?php if(auth()->guard()->check()): ?>
                                <a
                                    href="<?php echo e(url('/dashboard')); ?>"
                                    class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-xs transition-all shadow-md shadow-cyan-950/50"
                                >
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                                    </svg>
                                    <span>Console Dashboard</span>
                                </a>
                            <?php else: ?>
                                <a
                                    href="<?php echo e(route('login')); ?>"
                                    class="px-3.5 py-1.5 sm:px-4 sm:py-2 text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-lg text-xs font-semibold transition-all border border-transparent hover:border-slate-700"
                                >
                                    Log In
                                </a>

                                <?php if(Route::has('register')): ?>
                                    <a
                                        href="<?php echo e(route('register')); ?>"
                                        class="inline-flex items-center gap-1.5 px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-lg bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-semibold text-xs transition-all shadow-md shadow-emerald-950/50 hover:shadow-emerald-500/25"
                                    >
                                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                                        </svg>
                                        <span>Join Network</span>
                                    </a>
                                <?php endif; ?>
                            <?php endif; ?>
                        </div>
                    <?php endif; ?>
                </nav>
            </div>
        </header>

        <!-- Main Content -->
        <main class="relative z-10 flex-1">
            <!-- Hero Section -->
            <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-16 sm:pt-20 sm:pb-24 text-center">
                <!-- Live Telemetry Pill -->
                <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900/80 border border-cyan-500/30 text-cyan-300 text-xs font-mono shadow-lg shadow-cyan-950/50 mb-6">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span class="tracking-wider uppercase font-semibold">NASA EARTH SCIENCE // LIVE SATELLITE TELEMETRY</span>
                </div>

                <!-- Main Headline -->
                <h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight">
                    Monitoring Earth's <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-400">Vital Signs</span> From Space
                </h1>

                <!-- Subtitle -->
                <p class="mt-6 text-base sm:text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
                    Witness half a century of planetary transformation. Access calibrated multispectral satellite telemetry, deep-learning environmental change detection, and global climate indicators.
                </p>

                <!-- Action Buttons -->
                <div class="mt-8 flex flex-wrap items-center justify-center gap-4">
                    <?php if(auth()->guard()->check()): ?>
                        <a href="<?php echo e(url('/dashboard')); ?>" class="px-7 py-3.5 rounded-xl bg-gradient-to-r from-cyan-600 via-sky-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 text-white font-bold text-sm shadow-xl shadow-cyan-950/60 hover:shadow-cyan-500/30 transition-all transform hover:-translate-y-0.5">
                            Open Telemetry Console →
                        </a>
                    <?php else: ?>
                        <a href="<?php echo e(route('register')); ?>" class="px-7 py-3.5 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold text-sm shadow-xl shadow-emerald-950/60 hover:shadow-emerald-500/30 transition-all transform hover:-translate-y-0.5 flex items-center gap-2">
                            <svg class="w-4 h-4 text-emerald-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                            <span>Initialize Researcher Account</span>
                        </a>
                        <a href="<?php echo e(route('login')); ?>" class="px-7 py-3.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-slate-200 hover:text-white font-semibold text-sm border border-slate-700 hover:border-cyan-500/50 shadow-lg transition-all flex items-center gap-2">
                            <svg class="w-4 h-4 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                            </svg>
                            <span>Mission Control Login</span>
                        </a>
                    <?php endif; ?>
                </div>

                <!-- Constellation Ticker -->
                <div class="mt-12 flex flex-wrap items-center justify-center gap-4 text-xs font-mono text-slate-400">
                    <span class="text-cyan-400 flex items-center gap-1.5">
                        <span class="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                        CONSTELLATION:
                    </span>
                    <span class="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800">LANDSAT 8 & 9</span>
                    <span class="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800">SENTINEL-2A/B</span>
                    <span class="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800">MODIS TERRA & AQUA</span>
                    <span class="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800">ICESAT-2</span>
                    <span class="px-2.5 py-1 rounded bg-slate-900/60 border border-slate-800">GRACE-FO</span>
                </div>
            </section>

            <!-- Planetary Vital Signs (Climate Metrics Grid) -->
            <section id="vital-signs" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 border-t border-slate-800/80">
                <div class="text-center max-w-2xl mx-auto mb-10">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-2">
                        <span>PLANETARY VITAL SIGNS</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Key Indicators of Global Climate Change</h2>
                    <p class="text-xs sm:text-sm text-slate-400 mt-2">
                        Synthesizing real-time observations from Earth-orbiting satellites and climate research models.
                    </p>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <!-- Metric 1: Temperature Anomaly -->
                    <div class="glass-card p-5 rounded-2xl hover:border-cyan-500/50 transition-all duration-300 group">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase tracking-wider text-slate-400">Global Temp Delta</span>
                            <span class="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-black text-white font-mono">+1.26°C</span>
                            <p class="text-xs text-amber-300 font-semibold mt-1">Above Pre-Industrial Baseline</p>
                        </div>
                        <div class="mt-3 pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 flex items-center justify-between">
                            <span>GISTEMP v4 Analysis</span>
                            <span class="text-amber-400">Warming</span>
                        </div>
                    </div>

                    <!-- Metric 2: Arctic Sea Ice -->
                    <div class="glass-card p-5 rounded-2xl hover:border-cyan-500/50 transition-all duration-300 group">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase tracking-wider text-slate-400">Arctic Sea Ice</span>
                            <span class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                                </svg>
                            </span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-black text-cyan-200 font-mono">-12.2%</span>
                            <p class="text-xs text-cyan-400 font-semibold mt-1">Decline Per Decade</p>
                        </div>
                        <div class="mt-3 pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 flex items-center justify-between">
                            <span>Microwave Radiometry</span>
                            <span class="text-cyan-400">Historic Minimums</span>
                        </div>
                    </div>

                    <!-- Metric 3: Sea Level -->
                    <div class="glass-card p-5 rounded-2xl hover:border-cyan-500/50 transition-all duration-300 group">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase tracking-wider text-slate-400">Global Sea Level</span>
                            <span class="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                                </svg>
                            </span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-black text-white font-mono">+103 mm</span>
                            <p class="text-xs text-sky-300 font-semibold mt-1">+3.4 mm/year Acceleration</p>
                        </div>
                        <div class="mt-3 pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 flex items-center justify-between">
                            <span>Sentinel-6 &amp; Jason-3</span>
                            <span class="text-sky-300">Altimetry</span>
                        </div>
                    </div>

                    <!-- Metric 4: Carbon Dioxide -->
                    <div class="glass-card p-5 rounded-2xl hover:border-cyan-500/50 transition-all duration-300 group">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-mono uppercase tracking-wider text-slate-400">Carbon Dioxide (CO₂)</span>
                            <span class="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                            </span>
                        </div>
                        <div class="mt-3">
                            <span class="text-3xl font-black text-white font-mono">424.5 ppm</span>
                            <p class="text-xs text-rose-400 font-semibold mt-1">Highest in 2 Million Years</p>
                        </div>
                        <div class="mt-3 pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 flex items-center justify-between">
                            <span>AIRS &amp; OCO-2 Spectrometry</span>
                            <span class="text-rose-400">Elevated</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Satellite Constellations & Sensors -->
            <section id="constellations" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-800/80">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-emerald-300 text-xs font-mono mb-2">
                        <span>SPACE-BASED SENSING FLEET</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Earth Observation Constellation</h2>
                    <p class="text-xs sm:text-sm text-slate-400 mt-2">
                        Integrating continuous observations across optical, thermal, radar, and gravimetric sensor arrays.
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <!-- Sensor 1: Landsat 8/9 -->
                    <div class="glass-panel-subtle p-6 rounded-2xl border border-slate-700/60 hover:border-cyan-500/40 transition-all duration-300">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-mono px-2.5 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/50">LANDSAT 8 / 9</span>
                            <span class="text-[11px] font-mono text-emerald-400">ACTIVE • 705 KM ORBIT</span>
                        </div>
                        <h3 class="text-lg font-bold text-white">Multispectral Surface Imagery</h3>
                        <p class="text-xs text-slate-300 mt-2 leading-relaxed">
                            OLI-2 and TIRS-2 sensors deliver 30m resolution multispectral tracking across visible, NIR, and thermal bands, powering global vegetation health (NDVI) and urban expansion analytics.
                        </p>
                        <div class="mt-4 flex flex-wrap gap-1.5 text-[10px] font-mono text-slate-400">
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">11 Spectral Bands</span>
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">16-Day Repeat</span>
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">50-Year Archive</span>
                        </div>
                    </div>

                    <!-- Sensor 2: Sentinel-2 -->
                    <div class="glass-panel-subtle p-6 rounded-2xl border border-slate-700/60 hover:border-emerald-500/40 transition-all duration-300">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-mono px-2.5 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/50">SENTINEL-2A &amp; 2B</span>
                            <span class="text-[11px] font-mono text-emerald-400">ACTIVE • 786 KM ORBIT</span>
                        </div>
                        <h3 class="text-lg font-bold text-white">High-Frequency Land Monitoring</h3>
                        <p class="text-xs text-slate-300 mt-2 leading-relaxed">
                            Twin satellites with 10m spatial resolution and 5-day revisit rate providing rapid response alerts for wildfire perimeters, agricultural drought, and coastal water turbidity.
                        </p>
                        <div class="mt-4 flex flex-wrap gap-1.5 text-[10px] font-mono text-slate-400">
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">13 Spectral Bands</span>
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">5-Day Revisit</span>
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">10m Ground Res</span>
                        </div>
                    </div>

                    <!-- Sensor 3: Terra & Aqua MODIS -->
                    <div class="glass-panel-subtle p-6 rounded-2xl border border-slate-700/60 hover:border-amber-500/40 transition-all duration-300">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-xs font-mono px-2.5 py-1 rounded bg-amber-950 text-amber-300 border border-amber-800/50">MODIS TERRA &amp; AQUA</span>
                            <span class="text-[11px] font-mono text-emerald-400">ACTIVE • SUN-SYNC</span>
                        </div>
                        <h3 class="text-lg font-bold text-white">Daily Global Biosphere Scans</h3>
                        <p class="text-xs text-slate-300 mt-2 leading-relaxed">
                            Capturing entire planet views every 1 to 2 days across 36 spectral bands to monitor ocean phytoplankton blooms, atmospheric aerosol optical depth, and global snow cover.
                        </p>
                        <div class="mt-4 flex flex-wrap gap-1.5 text-[10px] font-mono text-slate-400">
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">36 Bands</span>
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">Daily Global View</span>
                            <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800">Thermal Anomalies</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Platform Capabilities Grid -->
            <section id="capabilities" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-800/80">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-2">
                        <span>ANALYTICS CAPABILITIES</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Earth Change Platform Architecture</h2>
                    <p class="text-xs sm:text-sm text-slate-400 mt-2">
                        Purpose-built for scientists, universities, and environmental analysts studying planetary shifts.
                    </p>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    <!-- Cap 1 -->
                    <div class="glass-card p-6 rounded-2xl hover:border-cyan-500/40 transition-all">
                        <div class="w-10 h-10 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center mb-4">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h3 class="text-base font-bold text-white">50-Year Raster Archive</h3>
                        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                            Continuous data coverage dating back to Landsat 1 in 1972, providing unprecedented temporal baselines.
                        </p>
                    </div>

                    <!-- Cap 2 -->
                    <div class="glass-card p-6 rounded-2xl hover:border-emerald-500/40 transition-all">
                        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-4">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                        </div>
                        <h3 class="text-base font-bold text-white">AI Change Detection</h3>
                        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                            Convolutional neural networks trained to detect illegal logging, glacier calving, and surface water changes.
                        </p>
                    </div>

                    <!-- Cap 3 -->
                    <div class="glass-card p-6 rounded-2xl hover:border-sky-500/40 transition-all">
                        <div class="w-10 h-10 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20 flex items-center justify-center mb-4">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                            </svg>
                        </div>
                        <h3 class="text-base font-bold text-white">Open REST &amp; STAC API</h3>
                        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                            Direct cloud-optimized GeoTIFF streaming into Python notebooks, QGIS, and international research pipelines.
                        </p>
                    </div>

                    <!-- Cap 4 -->
                    <div class="glass-card p-6 rounded-2xl hover:border-emerald-500/40 transition-all">
                        <div class="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-4">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                        </div>
                        <h3 class="text-base font-bold text-white">Peer Review Network</h3>
                        <p class="text-xs text-slate-400 mt-2 leading-relaxed">
                            Join over 12,000 active researchers cross-validating field observations against space measurements.
                        </p>
                    </div>
                </div>
            </section>

            <!-- Case Studies / Earth Changes in Focus -->
            <section id="stories" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-800/80">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/60 border border-amber-500/30 text-amber-300 text-xs font-mono mb-2">
                        <span>PLANETARY ANOMALIES IN FOCUS</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Documented Planetary Shifts</h2>
                    <p class="text-xs sm:text-sm text-slate-400 mt-2">
                        Longitudinal evidence of global ecosystem transformations recorded by NASA satellites.
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <!-- Story 1: Aral Sea -->
                    <div class="glass-card rounded-2xl p-5 border border-slate-700/60 flex flex-col justify-between">
                        <div>
                            <div class="text-xs font-mono text-cyan-400 mb-2">HYDROSPHERE LOSS • CENTRAL ASIA</div>
                            <h3 class="text-lg font-bold text-white">Aral Sea Desiccation</h3>
                            <p class="text-xs text-slate-300 mt-2 leading-relaxed">
                                Once the fourth-largest lake on Earth, satellite imagery tracks its contraction into the Aralkum Desert, providing stark evidence of regional water diversion and aridification.
                            </p>
                        </div>
                        <div class="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
                            <span>SURFACE LOSS:</span>
                            <span class="text-rose-400 font-bold">-90% since 1960</span>
                        </div>
                    </div>

                    <!-- Story 2: Greenland -->
                    <div class="glass-card rounded-2xl p-5 border border-slate-700/60 flex flex-col justify-between">
                        <div>
                            <div class="text-xs font-mono text-cyan-400 mb-2">CRYOSPHERE COLLAPSE • ARCTIC</div>
                            <h3 class="text-lg font-bold text-white">Greenland Ice Sheet Thinning</h3>
                            <p class="text-xs text-slate-300 mt-2 leading-relaxed">
                                GRACE-FO gravimetry and ICESat-2 laser profiling reveal an average mass loss of 280 billion metric tons of ice annually, driving global ocean volume expansion.
                            </p>
                        </div>
                        <div class="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
                            <span>ANNUAL RETREAT:</span>
                            <span class="text-cyan-400 font-bold">-280 Gt / Year</span>
                        </div>
                    </div>

                    <!-- Story 3: Amazon Basin -->
                    <div class="glass-card rounded-2xl p-5 border border-slate-700/60 flex flex-col justify-between">
                        <div>
                            <div class="text-xs font-mono text-cyan-400 mb-2">BIOSPHERE RECOVERY • SOUTH AMERICA</div>
                            <h3 class="text-lg font-bold text-white">Amazon Canopy Dynamics</h3>
                            <p class="text-xs text-slate-300 mt-2 leading-relaxed">
                                Synthetic Aperture Radar (SAR) and optical NDVI metrics provide bi-weekly deforestation alerts and identify critical ecological restoration corridors across the Amazon basin.
                            </p>
                        </div>
                        <div class="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
                            <span>OBSERVED ALERT CYCLE:</span>
                            <span class="text-emerald-400 font-bold">Bi-Weekly 10m Scans</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Bottom CTA Banner -->
            <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div class="glass-card rounded-3xl p-8 sm:p-12 relative overflow-hidden border border-cyan-500/30 text-center shadow-2xl shadow-cyan-950/80">
                    <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-sky-400 to-emerald-400"></div>
                    <div class="max-w-2xl mx-auto">
                        <span class="text-xs font-mono px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-500/30 text-cyan-300 uppercase">
                            OPEN SCIENCE ACCESS
                        </span>
                        <h2 class="text-3xl sm:text-4xl font-extrabold text-white mt-4 tracking-tight">
                            Ready to Explore Earth's Changing Climate?
                        </h2>
                        <p class="mt-3 text-sm text-slate-300 leading-relaxed">
                            Join thousands of university researchers, environmental scientists, and aerospace developers accessing open planetary satellite telemetry.
                        </p>
                        <div class="mt-6 flex flex-wrap items-center justify-center gap-4">
                            <?php if(auth()->guard()->check()): ?>
                                <a href="<?php echo e(url('/dashboard')); ?>" class="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-sm shadow-lg transition-all">
                                    Return to Console Dashboard
                                </a>
                            <?php else: ?>
                                <a href="<?php echo e(route('register')); ?>" class="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 text-white font-bold text-sm shadow-lg shadow-emerald-950/60 transition-all">
                                    Create Free Research Account
                                </a>
                                <a href="<?php echo e(route('login')); ?>" class="px-6 py-3 rounded-xl bg-slate-900 border border-slate-700 hover:border-slate-500 text-slate-200 hover:text-white font-semibold text-sm transition-all">
                                    Sign In to Portal
                                </a>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </section>
        </main>

        <!-- Mission Footer -->
        <footer class="relative z-20 w-full border-t border-slate-800/80 bg-slate-950/80 backdrop-blur-md py-8 px-4 sm:px-8 text-xs text-slate-400 font-mono">
            <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <?php if (isset($component)) { $__componentOriginal8892e718f3d0d7a916180885c6f012e7 = $component; } ?>
<?php if (isset($attributes)) { $__attributesOriginal8892e718f3d0d7a916180885c6f012e7 = $attributes; } ?>
<?php $component = Illuminate\View\AnonymousComponent::resolve(['view' => 'components.application-logo','data' => ['class' => 'h-8 w-auto']] + (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag ? $attributes->all() : [])); ?>
<?php $component->withName('application-logo'); ?>
<?php if ($component->shouldRender()): ?>
<?php $__env->startComponent($component->resolveView(), $component->data()); ?>
<?php if (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag): ?>
<?php $attributes = $attributes->except(\Illuminate\View\AnonymousComponent::ignoredParameterNames()); ?>
<?php endif; ?>
<?php $component->withAttributes(['class' => 'h-8 w-auto']); ?>
<?php echo $__env->renderComponent(); ?>
<?php endif; ?>
<?php if (isset($__attributesOriginal8892e718f3d0d7a916180885c6f012e7)): ?>
<?php $attributes = $__attributesOriginal8892e718f3d0d7a916180885c6f012e7; ?>
<?php unset($__attributesOriginal8892e718f3d0d7a916180885c6f012e7); ?>
<?php endif; ?>
<?php if (isset($__componentOriginal8892e718f3d0d7a916180885c6f012e7)): ?>
<?php $component = $__componentOriginal8892e718f3d0d7a916180885c6f012e7; ?>
<?php unset($__componentOriginal8892e718f3d0d7a916180885c6f012e7); ?>
<?php endif; ?>
                    <span class="text-slate-500">|</span>
                    <span class="text-slate-400">Earth Science Division • Open Planetary Data</span>
                </div>
                <div class="flex flex-wrap items-center justify-center gap-6 text-[11px] text-slate-500">
                    <span>NASA GODDARD SPACE FLIGHT CENTER</span>
                    <span>•</span>
                    <span>USGS LANDSAT PROGRAM</span>
                    <span>•</span>
                    <span>ESA COPERNICUS</span>
                </div>
            </div>
            <div class="max-w-7xl mx-auto mt-4 pt-4 border-t border-slate-900 text-center text-[11px] text-slate-500">
                Documenting Earth's evolution to preserve humanity's shared home. All satellite telemetry processed under Open Science and Creative Commons Open Data policies.
            </div>
        </footer>
    </body>
</html>
<?php /**PATH D:\laragon\www\nasa-earth-change\nasa-laravel\resources\views/welcome.blade.php ENDPATH**/ ?>