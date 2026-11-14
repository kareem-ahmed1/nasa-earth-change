<x-guest-layout>
    <div class="w-full max-w-md mx-auto">
        <div class="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200 shadow-sm">
            <div class="mb-5 text-center">
                <div class="w-12 h-12 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center mx-auto mb-3 shadow-2xs">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                </div>
                <h2 class="text-xl font-bold text-slate-900 tracking-tight">Reset Password</h2>
                <p class="mt-1.5 text-xs text-slate-500 leading-relaxed">
                    {{ __('Forgot your password? Enter your email address and we will email you a password reset link.') }}
                </p>
            </div>

            <x-auth-session-status class="mb-4" :status="session('status')" />

            <form method="POST" action="{{ route('password.email') }}" class="space-y-4">
                @csrf

                <div>
                    <x-input-label for="email" :value="__('Email Address')" />
                    <div class="relative mt-1">
                        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                            </svg>
                        </div>
                        <x-text-input 
                            id="email" 
                            class="pl-9 pr-3 py-2.5" 
                            type="email" 
                            name="email" 
                            :value="old('email')" 
                            placeholder="researcher@institution.org"
                            required 
                            autofocus 
                        />
                    </div>
                    <x-input-error :messages="$errors->get('email')" class="mt-1.5" />
                </div>

                <div class="pt-2">
                    <button 
                        type="submit" 
                        class="w-full flex items-center justify-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 active:bg-emerald-800 text-white font-semibold text-sm rounded-lg shadow-sm shadow-emerald-700/20 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition-all cursor-pointer"
                    >
                        <span>{{ __('Send Password Reset Link') }}</span>
                    </button>
                </div>

                <div class="pt-4 border-t border-slate-100 text-center">
                    <a href="{{ route('login') }}" class="text-xs text-slate-500 hover:text-slate-800 transition-colors inline-flex items-center gap-1">
                        <span>← Return to Sign In</span>
                    </a>
                </div>
            </form>
        </div>
    </div>
</x-guest-layout>
