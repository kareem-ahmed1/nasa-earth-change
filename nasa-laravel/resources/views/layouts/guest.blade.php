<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}" class="light">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="{{ csrf_token() }}">

        <title>{{ config('app.name', 'Earth Trend Explorer') }} — Explore. Analyze. Understand Our Planet.</title>

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600,700,800&display=swap" rel="stylesheet" />

        <!-- Scripts & Styles -->
        @vite(['resources/css/app.css', 'resources/js/app.js'])
    </head>
    <body class="font-sans text-slate-800 antialiased bg-[#f8fafc] min-h-screen flex flex-col justify-between selection:bg-emerald-500 selection:text-white">

        <!-- Top Navigation Header (Matching Earth Trend Explorer Reference) -->
        <header class="w-full bg-white border-b border-slate-200 px-4 sm:px-8 py-3 sticky top-0 z-30 shadow-2xs">
            <div class="max-w-7xl mx-auto flex items-center justify-between">
                <!-- Brand / Logo -->
                <a href="/" class="flex items-center gap-2 group transition-opacity hover:opacity-90">
                    <x-application-logo class="h-9 w-auto" />
                </a>

                <!-- Quick Navigation Links -->
                <div class="flex items-center gap-4 text-xs font-medium text-slate-600">
                    <a href="{{ url('/') }}" class="hidden sm:inline hover:text-slate-900 transition-colors">
                        Home
                    </a>
                    <a href="#about" class="hidden sm:inline hover:text-slate-900 transition-colors">
                        About
                    </a>
                    <a href="#how-it-works" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 transition-all shadow-2xs">
                        <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <polygon points="5 3 19 12 5 21 5 3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                        <span>How it works</span>
                    </a>
                </div>
            </div>
        </header>

        <!-- Main Content Area -->
        <main class="flex-1 flex items-center justify-center py-8 sm:py-12 px-4 sm:px-6">
            {{ $slot }}
        </main>

        <!-- Footer (Matching Earth Trend Explorer Reference) -->
        <footer class="w-full bg-white border-t border-slate-200 py-5 px-4 sm:px-8 text-xs text-slate-500 font-medium">
            <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
                <span>Earth Trend Explorer is a demonstration project for educational and research purposes.</span>
                <span>© 2024 Earth Trend Explorer Team</span>
                <div class="flex items-center gap-4 text-slate-500">
                    <a href="#privacy" class="hover:underline">Privacy Policy</a>
                    <a href="#terms" class="hover:underline">Terms of Use</a>
                    <a href="#contact" class="hover:underline">Contact</a>
                </div>
            </div>
        </footer>

    </body>
</html>
