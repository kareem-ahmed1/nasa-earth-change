@props(['active'])

@php
$classes = ($active ?? false)
            ? 'block w-full rounded-lg px-3 py-2 text-start text-sm font-semibold text-emerald-700 bg-emerald-50 focus:outline-none transition duration-150 ease-in-out'
            : 'block w-full rounded-lg px-3 py-2 text-start text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-50 focus:outline-none transition duration-150 ease-in-out';
@endphp

<a {{ $attributes->merge(['class' => $classes]) }}>
    {{ $slot }}
</a>
