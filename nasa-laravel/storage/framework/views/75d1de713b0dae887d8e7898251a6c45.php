<!DOCTYPE html>
<html lang="<?php echo e(str_replace('_', '-', app()->getLocale())); ?>" class="scroll-smooth">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title><?php echo e(config('app.name', 'Earth Trend Explorer')); ?> — Africa Climate Trend Analysis & Predictive Risk</title>

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600,700,800,900&display=swap" rel="stylesheet" />

        <!-- Styles / Scripts -->
        <?php echo app('Illuminate\Foundation\Vite')(['resources/css/app.css', 'resources/js/app.js']); ?>
    </head>
    <body class="font-sans text-slate-800 antialiased bg-slate-50 min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-white overflow-x-hidden">

        <!-- Top Navigation Header -->
        <header class="relative z-30 w-full border-b border-slate-200 bg-white/95 backdrop-blur-md px-4 sm:px-8 py-3.5 sticky top-0 shadow-2xs">
            <div class="max-w-7xl mx-auto flex items-center justify-between">
                <!-- Brand / Logo -->
                <a href="<?php echo e(url('/')); ?>" class="flex items-center gap-2 group transition-opacity hover:opacity-95">
                    <?php if (isset($component)) { $__componentOriginal8892e718f3d0d7a916180885c6f012e7 = $component; } ?>
<?php if (isset($attributes)) { $__attributesOriginal8892e718f3d0d7a916180885c6f012e7 = $attributes; } ?>
<?php $component = Illuminate\View\AnonymousComponent::resolve(['view' => 'components.application-logo','data' => ['class' => 'h-9 w-auto']] + (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag ? $attributes->all() : [])); ?>
<?php $component->withName('application-logo'); ?>
<?php if ($component->shouldRender()): ?>
<?php $__env->startComponent($component->resolveView(), $component->data()); ?>
<?php if (isset($attributes) && $attributes instanceof Illuminate\View\ComponentAttributeBag): ?>
<?php $attributes = $attributes->except(\Illuminate\View\AnonymousComponent::ignoredParameterNames()); ?>
<?php endif; ?>
<?php $component->withAttributes(['class' => 'h-9 w-auto']); ?>
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

                <!-- Desktop Nav Links -->
                <nav class="hidden lg:flex items-center gap-6 text-xs font-semibold text-slate-600">
                    <a href="#four-questions" class="hover:text-emerald-700 transition-colors">The 4 Questions</a>
                    <a href="#regions" class="hover:text-emerald-700 transition-colors">African Regions</a>
                    <a href="#data-methods" class="hover:text-emerald-700 transition-colors">Data &amp; Methods</a>
                    <a href="#predict-next-month" class="hover:text-indigo-700 transition-colors">Predict Next Month</a>
                    <a href="#limitations" class="hover:text-amber-800 transition-colors">Limitations</a>
                    <a href="#architecture" class="hover:text-slate-900 transition-colors">How It Works</a>
                </nav>

                <!-- Action CTAs -->
                <div class="flex items-center gap-2 sm:gap-3">
                    <a 
                        href="<?php echo e(url('/dashboard')); ?>" 
                        class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm shadow-emerald-700/20 transition-all cursor-pointer"
                    >
                        <span>Open Dashboard</span>
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                    </a>

                    <?php if(Route::has('login')): ?>
                        <?php if(auth()->guard()->check()): ?>
                            <form method="POST" action="<?php echo e(route('logout')); ?>" class="hidden sm:inline">
                                <?php echo csrf_field(); ?>
                                <button type="submit" class="text-xs text-slate-500 hover:text-rose-600 px-2 py-1 transition-colors">
                                    Log Out
                                </button>
                            </form>
                        <?php else: ?>
                            <a href="<?php echo e(route('login')); ?>" class="hidden sm:inline-block text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors">
                                Log In
                            </a>
                        <?php endif; ?>
                    <?php endif; ?>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="relative z-10 flex-1">

            <!-- Hero Section -->
            <section class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-16 sm:pt-20 sm:pb-24 text-center">
                
                <!-- Verification Pill -->
                <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-mono shadow-2xs mb-6">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span class="tracking-wider uppercase font-semibold">NASA Satellite Observations · 2004–2024 · Africa Only</span>
                </div>

                <!-- Main Headline -->
                <h1 class="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 max-w-4xl mx-auto leading-tight">
                    Statistical Rigor for Understanding <br class="hidden sm:inline" />
                    <span class="text-emerald-700">Africa’s Changing Climate</span>
                </h1>

                <!-- Subtitle -->
                <p class="mt-6 text-sm sm:text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
                    Earth Trend Explorer investigates 21 continuous years of NASA satellite observations across Africa's five macro-regions. Quantify long-term trends with non-parametric Mann-Kendall statistics, evaluate Sen's slope rates of change, and explore next-month predictive risk.
                </p>

                <!-- Call to Action Buttons -->
                <div class="mt-8 flex flex-wrap items-center justify-center gap-3.5">
                    <a 
                        href="<?php echo e(url('/dashboard')); ?>" 
                        class="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-700/20 transition-all flex items-center gap-2"
                    >
                        <span>Launch Analysis Dashboard</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                    </a>

                    <a 
                        href="#four-questions" 
                        class="px-6 py-3 rounded-xl bg-white hover:bg-slate-100 text-slate-700 font-semibold text-sm border border-slate-300 shadow-2xs transition-all flex items-center gap-2"
                    >
                        <span>How It Works</span>
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                        </svg>
                    </a>
                </div>

                <!-- Integrity Metrics Bar -->
                <div class="mt-14 pt-8 border-t border-slate-200 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-left">
                    <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
                        <div class="text-[10px] text-slate-400 uppercase font-mono">NASA Observations</div>
                        <div class="text-xl font-black text-slate-900 font-mono mt-0.5">1,260</div>
                        <p class="text-[11px] text-slate-500 mt-1">Verified monthly records (2004–2024)</p>
                    </div>

                    <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
                        <div class="text-[10px] text-slate-400 uppercase font-mono">Geographic Scope</div>
                        <div class="text-xl font-black text-slate-900 font-mono mt-0.5">5 Regions</div>
                        <p class="text-[11px] text-slate-500 mt-1">African continental macro-regions</p>
                    </div>

                    <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
                        <div class="text-[10px] text-slate-400 uppercase font-mono">Statistical Method</div>
                        <div class="text-xl font-black text-emerald-700 font-mono mt-0.5">Mann-Kendall</div>
                        <p class="text-[11px] text-slate-500 mt-1">Non-parametric + Sen's slope</p>
                    </div>

                    <div class="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs">
                        <div class="text-[10px] text-slate-400 uppercase font-mono">Predictive Model</div>
                        <div class="text-xl font-black text-indigo-700 font-mono mt-0.5">Model 1 v6</div>
                        <p class="text-[11px] text-slate-500 mt-1">One-month-ahead exceedance risk</p>
                    </div>
                </div>

            </section>

            <!-- The 4 Core Questions Section -->
            <section id="four-questions" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-mono mb-2">
                        <span>FOUNDATIONAL FRAMEWORK</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">The Four Questions We Answer</h2>
                    <p class="text-xs sm:text-sm text-slate-500 mt-2">
                        For any selected variable, observational time window, and African macro-region, Earth Trend Explorer provides rigorous answers:
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    
                    <!-- Question 1: What is changing? -->
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs hover:border-emerald-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-4">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <span class="text-[11px] font-mono text-emerald-700 font-bold uppercase tracking-wider">Question 01</span>
                            <h3 class="text-base font-bold text-slate-900 mt-1">What is changing?</h3>
                            <p class="text-xs text-slate-600 mt-2.5 leading-relaxed">
                                Calibrated physical variables: <strong>Surface Temperature Anomaly</strong> (°C, NASA GISTEMP v4) and <strong>Precipitation Rate</strong> (mm/day, NASA POWER / MERRA-2). Every observation is tied to documented physical units.
                            </p>
                        </div>
                        <div class="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-400">
                            Unit Traceability: °C &amp; mm/day
                        </div>
                    </div>

                    <!-- Question 2: Where is it changing? -->
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs hover:border-emerald-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="w-10 h-10 rounded-xl bg-sky-50 text-sky-700 flex items-center justify-center mb-4">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                            </div>
                            <span class="text-[11px] font-mono text-sky-700 font-bold uppercase tracking-wider">Question 02</span>
                            <h3 class="text-base font-bold text-slate-900 mt-1">Where is it changing?</h3>
                            <p class="text-xs text-slate-600 mt-2.5 leading-relaxed">
                                Focused exclusively on Africa across 5 standardized continental macro-regions: <strong>North Africa, West Africa, Central Africa, East Africa, and Southern Africa</strong>. Selected interactively on a Leaflet map.
                            </p>
                        </div>
                        <div class="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-400">
                            Scope: 5 Macro-Regions
                        </div>
                    </div>

                    <!-- Question 3: How has it changed over time? -->
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs hover:border-emerald-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center mb-4">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                </svg>
                            </div>
                            <span class="text-[11px] font-mono text-amber-700 font-bold uppercase tracking-wider">Question 03</span>
                            <h3 class="text-base font-bold text-slate-900 mt-1">How has it changed?</h3>
                            <p class="text-xs text-slate-600 mt-2.5 leading-relaxed">
                                Interactive Plotly monthly time series paired with <strong>Sen's slope estimator</strong>. Computes the true median rate of change per decade and per year, resistant to seasonal shifts and outlier anomalies.
                            </p>
                        </div>
                        <div class="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-400">
                            Slope: Medians per decade
                        </div>
                    </div>

                    <!-- Question 4: How significant is the trend? -->
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs hover:border-emerald-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center mb-4">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <span class="text-[11px] font-mono text-indigo-700 font-bold uppercase tracking-wider">Question 04</span>
                            <h3 class="text-base font-bold text-slate-900 mt-1">How significant is it?</h3>
                            <p class="text-xs text-slate-600 mt-2.5 leading-relaxed">
                                Non-parametric <strong>Mann-Kendall test</strong> executed on aggregated annual baselines. Yields exact $p$-values, Kendall's tau ($\tau$), sample count $n$, and an unambiguous verdict at $\alpha = 0.05$.
                            </p>
                        </div>
                        <div class="mt-4 pt-3 border-t border-slate-100 text-[11px] font-mono text-slate-400">
                            Hypothesis: $H_0$ rejected at $p < 0.05$
                        </div>
                    </div>

                </div>
            </section>

            <!-- African Macro-Regions Section -->
            <section id="regions" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
                <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-10">
                    <div>
                        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-mono mb-2">
                            <span>GEOGRAPHIC COVERAGE</span>
                        </div>
                        <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">The 5 African Macro-Regions</h2>
                        <p class="text-xs sm:text-sm text-slate-500 mt-1">
                            Carefully partitioned along established continental boundaries (Africa only):
                        </p>
                    </div>

                    <a 
                        href="<?php echo e(url('/dashboard')); ?>" 
                        class="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-700 hover:text-emerald-800 transition-colors"
                    >
                        <span>View Interactive Map</span>
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                    </a>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    
                    <!-- Region 1: North Africa -->
                    <div class="bg-white p-4.5 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                                <span class="text-[10px] font-mono text-slate-400">GISTEMP v4</span>
                            </div>
                            <h3 class="text-sm font-bold text-slate-900">North Africa</h3>
                            <p class="text-[11px] text-slate-500 mt-1">
                                Sahara, Atlas Mountains &amp; Mediterranean coastlines.
                            </p>
                            <div class="mt-3 p-2 rounded-lg bg-rose-50/70 border border-rose-100 text-[11px] font-mono text-rose-900">
                                <strong>+0.395 °C</strong> / decade<br />
                                <span class="text-[10px] text-rose-700">Significant (p = 0.0033)</span>
                            </div>
                        </div>
                        <a href="<?php echo e(url('/dashboard')); ?>" class="mt-4 text-[11px] font-bold text-emerald-700 hover:underline">
                            Analyze Region →
                        </a>
                    </div>

                    <!-- Region 2: West Africa -->
                    <div class="bg-white p-4.5 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span>
                                <span class="text-[10px] font-mono text-slate-400">GISTEMP v4</span>
                            </div>
                            <h3 class="text-sm font-bold text-slate-900">West Africa</h3>
                            <p class="text-[11px] text-slate-500 mt-1">
                                Sahel transition belt, savannas &amp; Guinean coast.
                            </p>
                            <div class="mt-3 p-2 rounded-lg bg-amber-50/70 border border-amber-100 text-[11px] font-mono text-amber-900">
                                <strong>+0.165 °C</strong> / decade<br />
                                <span class="text-[10px] text-amber-700">Trend (p = 0.0753)</span>
                            </div>
                        </div>
                        <a href="<?php echo e(url('/dashboard')); ?>" class="mt-4 text-[11px] font-bold text-emerald-700 hover:underline">
                            Analyze Region →
                        </a>
                    </div>

                    <!-- Region 3: Central Africa -->
                    <div class="bg-white p-4.5 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                                <span class="text-[10px] font-mono text-slate-400">GISTEMP v4</span>
                            </div>
                            <h3 class="text-sm font-bold text-slate-900">Central Africa</h3>
                            <p class="text-[11px] text-slate-500 mt-1">
                                Congo River basin &amp; equatorial rainforest biome.
                            </p>
                            <div class="mt-3 p-2 rounded-lg bg-emerald-50/70 border border-emerald-100 text-[11px] font-mono text-emerald-900">
                                <strong>+0.117 °C</strong> / decade<br />
                                <span class="text-[10px] text-emerald-700">Stable (p = 0.2863)</span>
                            </div>
                        </div>
                        <a href="<?php echo e(url('/dashboard')); ?>" class="mt-4 text-[11px] font-bold text-emerald-700 hover:underline">
                            Analyze Region →
                        </a>
                    </div>

                    <!-- Region 4: East Africa -->
                    <div class="bg-white p-4.5 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-cyan-500"></span>
                                <span class="text-[10px] font-mono text-slate-400">GISTEMP v4</span>
                            </div>
                            <h3 class="text-sm font-bold text-slate-900">East Africa</h3>
                            <p class="text-[11px] text-slate-500 mt-1">
                                Horn of Africa, Great Rift Valley &amp; highlands.
                            </p>
                            <div class="mt-3 p-2 rounded-lg bg-cyan-50/70 border border-cyan-100 text-[11px] font-mono text-cyan-900">
                                <strong>+0.187 °C</strong> / decade<br />
                                <span class="text-[10px] text-cyan-700">Trend (p = 0.0886)</span>
                            </div>
                        </div>
                        <a href="<?php echo e(url('/dashboard')); ?>" class="mt-4 text-[11px] font-bold text-emerald-700 hover:underline">
                            Analyze Region →
                        </a>
                    </div>

                    <!-- Region 5: Southern Africa -->
                    <div class="bg-white p-4.5 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-purple-500"></span>
                                <span class="text-[10px] font-mono text-slate-400">GISTEMP v4</span>
                            </div>
                            <h3 class="text-sm font-bold text-slate-900">Southern Africa</h3>
                            <p class="text-[11px] text-slate-500 mt-1">
                                Kalahari basin, temperate veld &amp; southern cape.
                            </p>
                            <div class="mt-3 p-2 rounded-lg bg-purple-50/70 border border-purple-100 text-[11px] font-mono text-purple-900">
                                <strong>+0.287 °C</strong> / decade<br />
                                <span class="text-[10px] text-purple-700">Significant (p = 0.0163)</span>
                            </div>
                        </div>
                        <a href="<?php echo e(url('/dashboard')); ?>" class="mt-4 text-[11px] font-bold text-emerald-700 hover:underline">
                            Analyze Region →
                        </a>
                    </div>

                </div>
            </section>

            <!-- Data & Methods Section -->
            <section id="data-methods" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-mono mb-2">
                        <span>SCIENTIFIC PROVENANCE</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Verified Data &amp; Methodology</h2>
                    <p class="text-xs sm:text-sm text-slate-500 mt-2">
                        Zero synthetic data. Built on peer-reviewed NASA satellite archives and non-parametric statistics:
                    </p>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    <!-- Variables Metadata Card -->
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-5">
                        <div class="flex items-center gap-2.5 pb-3 border-b border-slate-100">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                            <h3 class="text-base font-bold text-slate-900">Observational Datasets (2004–2024)</h3>
                        </div>

                        <!-- Variable 1 -->
                        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-slate-900">Surface Temperature Anomaly</span>
                                <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">°C</span>
                            </div>
                            <div class="text-xs text-slate-600 grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                                <div><span class="text-slate-400">Sensor / Archive:</span> NASA GISTEMP v4</div>
                                <div><span class="text-slate-400">Baseline Normal:</span> 1951–1980 base</div>
                                <div><span class="text-slate-400">Resolution:</span> Monthly regional means</div>
                                <div><span class="text-slate-400">Record Length:</span> 252 months / region</div>
                            </div>
                        </div>

                        <!-- Variable 2 -->
                        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-slate-900">Precipitation Rate</span>
                                <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-sky-100 text-sky-800">mm/day</span>
                            </div>
                            <div class="text-xs text-slate-600 grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
                                <div><span class="text-slate-400">Sensor / Archive:</span> NASA POWER / MERRA-2</div>
                                <div><span class="text-slate-400">Parameter:</span> PRECTOTCORR</div>
                                <div><span class="text-slate-400">Resolution:</span> Monthly averages</div>
                                <div><span class="text-slate-400">Unit Note:</span> Millimeters per day</div>
                            </div>
                        </div>
                    </div>

                    <!-- Non-Parametric Methodology Card -->
                    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-5">
                        <div class="flex items-center gap-2.5 pb-3 border-b border-slate-100">
                            <span class="w-2.5 h-2.5 rounded-full bg-indigo-500"></span>
                            <h3 class="text-base font-bold text-slate-900">Why Non-Parametric Statistics?</h3>
                        </div>

                        <div class="space-y-4 text-xs text-slate-600 leading-relaxed">
                            <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                                <h4 class="font-bold text-slate-900 text-xs">Mann-Kendall Trend Test</h4>
                                <p>
                                    Environmental time series rarely conform to normal (Gaussian) distributions and frequently exhibit seasonal skewness. The Mann-Kendall test is rank-based and evaluates whether a monotonic upward or downward trend exists without assuming linear normality.
                                </p>
                            </div>

                            <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                                <h4 class="font-bold text-slate-900 text-xs">Sen's Slope Estimator</h4>
                                <p>
                                    Standard Ordinary Least Squares (OLS) linear regression can be severely biased by a single extreme anomalous flood or heatwave. Sen's slope calculates the median of all pairwise slopes between years, yielding a robust, outlier-resistant rate of change per decade.
                                </p>
                            </div>

                            <p class="text-[11px] text-slate-500 italic">
                                Implemented with SciPy and NumPy in our dedicated scientific service, matching peer-reviewed climatological standards.
                            </p>
                        </div>
                    </div>

                </div>
            </section>

            <!-- Predict Next Month Section -->
            <section id="predict-next-month" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
                <div class="bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 rounded-3xl p-6 sm:p-10 text-white border border-indigo-900/50 shadow-xl relative overflow-hidden">
                    <div class="max-w-3xl">
                        
                        <!-- Badge -->
                        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-900/60 border border-indigo-400/30 text-indigo-300 text-xs font-mono mb-4">
                            <span>MACHINE LEARNING ENGINE · MODEL 1 V6</span>
                        </div>

                        <h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight">
                            "Predict Next Month" — Exceedance Risk Estimation
                        </h2>

                        <p class="mt-3 text-xs sm:text-sm text-slate-300 leading-relaxed">
                            Rather than making unrealistic deterministic claims of exact weather numbers weeks in advance, Model 1 v6 formulates environmental prediction as an <strong>exceedance-risk probability</strong>: what is the likelihood that next month will experience a top-decile extreme anomaly compared to historical climatology?
                        </p>

                        <!-- Honesty & Validation Comparison Grid -->
                        <div class="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
                            
                            <!-- Temperature Card -->
                            <div class="p-4 rounded-xl bg-slate-900/80 border border-emerald-500/30 space-y-2">
                                <div class="flex items-center justify-between">
                                    <span class="text-xs font-bold text-emerald-400">Temperature Anomaly Model</span>
                                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">SKILL VERIFIED</span>
                                </div>
                                <p class="text-xs text-slate-300 leading-relaxed">
                                    Validated via 3-Fold Walk-Forward Cross Validation and held-out test set (2022–2024). Achieves <strong>Test ROC-AUC = 0.753</strong> vs 0.675 baseline (+0.079 lift, passing all 4 skill criteria). Risk tiers (High / Elevated / Low) are statistically calibrated.
                                </p>
                            </div>

                            <!-- Precipitation Card -->
                            <div class="p-4 rounded-xl bg-slate-900/80 border border-amber-500/30 space-y-2">
                                <div class="flex items-center justify-between">
                                    <span class="text-xs font-bold text-amber-400">Precipitation Rate Model</span>
                                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">ADVISORY ONLY</span>
                                </div>
                                <p class="text-xs text-slate-300 leading-relaxed">
                                    Precipitation demonstrates <strong>no reliable test set skill</strong> (Test ROC-AUC: 0.562 vs 0.520 baseline). Precipitation risk tiers are explicitly marked "NOT VALIDATED" in the interface. In West Africa, January is masked during climatological dry seasons.
                                </p>
                            </div>

                        </div>

                        <div class="mt-8 flex items-center gap-3">
                            <a 
                                href="<?php echo e(url('/dashboard')); ?>" 
                                class="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-sm shadow-indigo-600/30 transition-all flex items-center gap-1.5"
                            >
                                <span>Test Prediction Engine on Dashboard</span>
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </a>
                        </div>

                    </div>
                </div>
            </section>

            <!-- Transparency & Limitations Section -->
            <section id="limitations" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-900 text-xs font-mono mb-2">
                        <span>SCIENTIFIC INTEGRITY</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Transparency &amp; Limitations</h2>
                    <p class="text-xs sm:text-sm text-slate-500 mt-2">
                        Honest science requires explicit disclosure of analytical assumptions and boundaries:
                    </p>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                    
                    <div class="p-5 rounded-xl bg-white border border-amber-200/80 shadow-2xs space-y-2">
                        <div class="text-amber-800 font-bold text-xs flex items-center gap-1.5">
                            <span>⏳</span> 21-Year Record
                        </div>
                        <p class="text-xs text-slate-600 leading-relaxed">
                            Continuous data covers 2004–2024 (21 years). While robust for evaluating 21st-century acceleration, this is shorter than the standard World Meteorological Organization (WMO) 30-year climatological normal.
                        </p>
                    </div>

                    <div class="p-5 rounded-xl bg-white border border-amber-200/80 shadow-2xs space-y-2">
                        <div class="text-amber-800 font-bold text-xs flex items-center gap-1.5">
                            <span>🗺️</span> Regional Averaging
                        </div>
                        <p class="text-xs text-slate-600 leading-relaxed">
                            All indicators represent macro-regional spatial averages. Sub-regional microclimates (such as coastal sea breezes, localized rain shadows, or mountain elevations) are integrated into the macro-regional mean.
                        </p>
                    </div>

                    <div class="p-5 rounded-xl bg-white border border-amber-200/80 shadow-2xs space-y-2">
                        <div class="text-amber-800 font-bold text-xs flex items-center gap-1.5">
                            <span>📈</span> Autocorrelation
                        </div>
                        <p class="text-xs text-slate-600 leading-relaxed">
                            Annual aggregation effectively mitigates 12-month seasonal cycles; however, multi-year oceanic-atmospheric oscillations (such as ENSO and the Indian Ocean Dipole) can introduce serial autocorrelation.
                        </p>
                    </div>

                    <div class="p-5 rounded-xl bg-white border border-amber-200/80 shadow-2xs space-y-2">
                        <div class="text-amber-800 font-bold text-xs flex items-center gap-1.5">
                            <span>🌦️</span> Climate vs Weather
                        </div>
                        <p class="text-xs text-slate-600 leading-relaxed">
                            Earth Trend Explorer tracks multi-decadal shifts and top-decile exceedance risk. It is not an operational daily weather forecast and should not be used for daily precipitation scheduling.
                        </p>
                    </div>

                </div>
            </section>

            <!-- How It Works Architecture Section -->
            <section id="architecture" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
                <div class="text-center max-w-2xl mx-auto mb-12">
                    <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-mono mb-2">
                        <span>SYSTEM ARCHITECTURE</span>
                    </div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">How the Platform Works</h2>
                    <p class="text-xs sm:text-sm text-slate-500 mt-2">
                        An integrated, decoupled microservice pipeline connecting raw NASA archives to interactive visualization:
                    </p>
                </div>

                <div class="p-6 sm:p-8 rounded-2xl bg-white border border-slate-200 shadow-2xs max-w-4xl mx-auto">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                        
                        <!-- Step 1 -->
                        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
                            <div class="text-xs font-mono font-bold text-emerald-700 mb-1">01. DATA LAYER</div>
                            <h4 class="text-xs font-bold text-slate-900">NASA Archives</h4>
                            <p class="text-[11px] text-slate-500 mt-1">1,260 cleaned monthly records in CSV (GISTEMP &amp; POWER)</p>
                        </div>

                        <!-- Step 2 -->
                        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
                            <div class="text-xs font-mono font-bold text-indigo-700 mb-1">02. COMPUTE</div>
                            <h4 class="text-xs font-bold text-slate-900">FastAPI Microservice</h4>
                            <p class="text-[11px] text-slate-500 mt-1">Python engine computing Mann-Kendall, Sen's slope &amp; ML inference</p>
                        </div>

                        <!-- Step 3 -->
                        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
                            <div class="text-xs font-mono font-bold text-sky-700 mb-1">03. GATEWAY</div>
                            <h4 class="text-xs font-bold text-slate-900">Laravel Analysis API</h4>
                            <p class="text-[11px] text-slate-500 mt-1">Strict input validation, region ID normalization &amp; secure proxying</p>
                        </div>

                        <!-- Step 4 -->
                        <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
                            <div class="text-xs font-mono font-bold text-purple-700 mb-1">04. FRONTEND</div>
                            <h4 class="text-xs font-bold text-slate-900">Leaflet + Plotly</h4>
                            <p class="text-[11px] text-slate-500 mt-1">Interactive continental selection &amp; responsive non-parametric charts</p>
                        </div>

                    </div>
                </div>
            </section>

            <!-- Bottom Call to Action Banner -->
            <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div class="rounded-3xl p-8 sm:p-12 bg-white border border-slate-200 text-center shadow-sm">
                    <div class="max-w-2xl mx-auto">
                        <span class="text-xs font-mono px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 uppercase">
                            OPEN CLIMATE SCIENCE
                        </span>
                        <h2 class="text-3xl sm:text-4xl font-black text-slate-900 mt-4 tracking-tight">
                            Explore Africa’s Long-Term Climate Trends
                        </h2>
                        <p class="mt-3 text-xs sm:text-sm text-slate-600 leading-relaxed">
                            Analyze 21 years of NASA satellite observations across 5 African macro-regions with verified non-parametric statistics and transparent risk estimates.
                        </p>
                        <div class="mt-6 flex flex-wrap items-center justify-center gap-4">
                            <a 
                                href="<?php echo e(url('/dashboard')); ?>" 
                                class="px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md shadow-emerald-700/20 transition-all flex items-center gap-2"
                            >
                                <span>Open the Dashboard</span>
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </a>
                        </div>
                    </div>
                </div>
            </section>

        </main>

        <!-- Mission Footer -->
        <footer class="relative z-20 w-full border-t border-slate-200 bg-white py-8 px-4 sm:px-8 text-xs text-slate-500">
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
                    <span class="text-slate-300">|</span>
                    <span class="text-slate-600 font-medium">Earth Trend Explorer (Africa)</span>
                </div>
                <div class="flex flex-wrap items-center justify-center gap-4 text-[11px] font-mono text-slate-500">
                    <span>NASA GISTEMP v4</span>
                    <span>•</span>
                    <span>NASA POWER / MERRA-2</span>
                    <span>•</span>
                    <span>Natural Earth Data</span>
                </div>
            </div>
            <div class="max-w-7xl mx-auto mt-4 pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-400">
                <span>All telemetry processed directly from verified NASA archives. Zero synthetic data.</span>
                <span>© <?php echo e(date('Y')); ?> Earth Trend Explorer Team</span>
            </div>
        </footer>

    </body>
</html>
<?php /**PATH D:\laragon\www\nasa-earth-change\nasa-earth-change\nasa-laravel\resources\views/welcome.blade.php ENDPATH**/ ?>