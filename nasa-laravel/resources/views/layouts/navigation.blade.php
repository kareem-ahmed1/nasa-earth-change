<nav x-data="{ open: false }" class="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 items-center justify-between">
            <div class="flex items-center gap-8">
                <a href="{{ route('dashboard') }}" class="shrink-0 transition-opacity hover:opacity-80">
                    <x-application-logo class="block h-10 w-auto" />
                </a>

                <div class="hidden items-center gap-2 sm:flex">
                    <x-nav-link :href="route('dashboard')" :active="request()->routeIs('dashboard')">
                        {{ __('Dashboard') }}
                    </x-nav-link>
                    <a href="{{ url('/#vital-signs') }}" class="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900">
                        {{ __('Planetary Signs') }}
                    </a>
                    <a href="{{ url('/#constellations') }}" class="rounded-lg px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900">
                        {{ __('Satellites') }}
                    </a>
                </div>
            </div>

            <div class="hidden items-center gap-4 sm:flex">
                <span class="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                    <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
                    {{ __('Sensors online') }}
                </span>

                <x-dropdown align="right" width="48" contentClasses="py-1.5 bg-white border border-slate-200 shadow-lg rounded-xl">
                    <x-slot name="trigger">
                        <button class="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-emerald-500/30">
                            <span class="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700">
                                {{ strtoupper(substr(Auth::user()->name, 0, 1)) }}
                            </span>
                            <span class="max-w-[120px] truncate">{{ Auth::user()->name }}</span>
                            <svg class="h-4 w-4 text-slate-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                            </svg>
                        </button>
                    </x-slot>

                    <x-slot name="content">
                        <div class="border-b border-slate-100 px-4 py-2">
                            <div class="text-[11px] font-semibold uppercase tracking-wide text-slate-500">{{ __('Signed in as') }}</div>
                            <div class="truncate text-sm font-semibold text-slate-900">{{ Auth::user()->name }}</div>
                            <div class="truncate text-xs text-slate-500">{{ Auth::user()->email }}</div>
                        </div>
                        <x-dropdown-link :href="route('profile.edit')">
                            {{ __('Profile settings') }}
                        </x-dropdown-link>
                        <a href="{{ url('/') }}" class="block w-full px-4 py-2 text-start text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900">
                            {{ __('Public home') }}
                        </a>
                        <form method="POST" action="{{ route('logout') }}" class="mt-1 border-t border-slate-100 pt-1">
                            @csrf
                            <button type="submit" class="block w-full px-4 py-2 text-start text-sm font-medium text-rose-600 transition hover:bg-rose-50">
                                {{ __('Log out') }}
                            </button>
                        </form>
                    </x-slot>
                </x-dropdown>
            </div>

            <button @click="open = !open" class="inline-flex items-center justify-center rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 focus:outline-none sm:hidden" aria-label="{{ __('Toggle navigation') }}">
                <svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                    <path :class="{ 'hidden': open, 'inline-flex': !open }" class="inline-flex" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                    <path :class="{ 'hidden': !open, 'inline-flex': open }" class="hidden" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
    </div>

    <div x-show="open" x-transition class="border-t border-slate-200 bg-white px-4 pb-4 pt-2 sm:hidden">
        <div class="space-y-1">
            <x-responsive-nav-link :href="route('dashboard')" :active="request()->routeIs('dashboard')">
                {{ __('Dashboard') }}
            </x-responsive-nav-link>
            <a href="{{ url('/#vital-signs') }}" class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900">
                {{ __('Planetary Signs') }}
            </a>
            <a href="{{ url('/#constellations') }}" class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900">
                {{ __('Satellites') }}
            </a>
            <x-responsive-nav-link :href="route('profile.edit')">
                {{ __('Profile settings') }}
            </x-responsive-nav-link>
            <a href="{{ url('/') }}" class="block rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900">
                {{ __('Public home') }}
            </a>
        </div>

        <div class="mt-3 flex items-center justify-between border-t border-slate-100 pt-3">
            <div class="min-w-0">
                <div class="truncate text-sm font-semibold text-slate-800">{{ Auth::user()->name }}</div>
                <div class="truncate text-xs text-slate-500">{{ Auth::user()->email }}</div>
            </div>
            <form method="POST" action="{{ route('logout') }}">
                @csrf
                <button type="submit" class="rounded-lg px-3 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50">
                    {{ __('Log out') }}
                </button>
            </form>
        </div>
    </div>
</nav>
