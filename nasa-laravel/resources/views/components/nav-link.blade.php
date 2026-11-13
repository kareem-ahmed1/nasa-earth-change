@props(['active'])

@php
$classes = ($active ?? false)
            ? 'inline-flex items-center px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-sm font-semibold text-emerald-700 transition duration-150 ease-in-out'
            : 'inline-flex items-center px-3 py-1.5 rounded-lg border border-transparent text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 hover:border-slate-200 transition duration-150 ease-in-out';
@endphp

<a {{ $attributes->merge(['class' => $classes]) }}>
    {{ $slot }}
</a>
