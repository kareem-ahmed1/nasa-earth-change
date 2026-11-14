<!-- Earth Trend Explorer Interactive Map Component -->
<div class="relative w-full rounded-xl overflow-hidden border border-slate-200 shadow-md bg-slate-100" style="min-height: 440px;">
    <!-- Leaflet Map Container -->
    <div id="earth-map" class="w-full h-[440px] lg:h-[490px] z-0"></div>

    <!-- Custom Floating Map Toolbar (Left side of map, matching reference image) -->
    <div class="absolute top-4 left-4 z-[400] flex flex-col bg-white rounded-lg shadow-lg border border-slate-200 overflow-hidden divide-y divide-slate-100">
        <!-- Select / Navigation Mode -->
        <button 
            type="button" 
            data-map-tool="select" 
            title="Navigation / Selection Tool"
            class="p-2.5 transition-colors bg-blue-600 text-white cursor-pointer"
        >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3l7 18 3-7 7-3L3 3z" />
            </svg>
        </button>

        <!-- Delete Selection -->
        <button 
            type="button" 
            data-map-tool="delete" 
            title="Clear / Delete Selected Region"
            class="p-2.5 transition-colors bg-white text-slate-700 hover:bg-slate-50 cursor-pointer"
        >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
        </button>

        <!-- Zoom In -->
        <button 
            type="button" 
            data-map-tool="zoom-in" 
            title="Zoom In"
            class="p-2.5 transition-colors bg-white text-slate-700 hover:bg-slate-50 cursor-pointer"
        >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
        </button>

        <!-- Zoom Out -->
        <button 
            type="button" 
            data-map-tool="zoom-out" 
            title="Zoom Out"
            class="p-2.5 transition-colors bg-white text-slate-700 hover:bg-slate-50 cursor-pointer"
        >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
        </button>

        <!-- Switch Layers (Satellite / Street) -->
        <button 
            type="button" 
            data-map-tool="layers" 
            title="Toggle Map Layers (Satellite / Street)"
            class="p-2.5 transition-colors bg-white text-slate-700 hover:bg-slate-50 cursor-pointer"
        >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 2 7 12 12 22 7 12 2" />
                <polyline points="2 17 12 22 22 17" />
                <polyline points="2 12 12 17 22 12" />
            </svg>
        </button>
    </div>

    <!-- Floating Map Tips Card (Top right of map, matching reference image) -->
    <div class="absolute top-4 right-4 z-[400] w-64 bg-white/95 backdrop-blur-sm rounded-xl p-3.5 shadow-lg border border-slate-200/80 text-xs">
        <div class="flex items-center gap-1.5 font-bold text-slate-800 mb-1.5">
            <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" stroke-width="2" />
                <line x1="12" y1="16" x2="12" y2="12" stroke-width="2" />
                <line x1="12" y1="8" x2="12.01" y2="8" stroke-width="2" />
            </svg>
            <span>Map Tips</span>
        </div>
        <ul class="space-y-1 text-slate-600 text-[11px] leading-relaxed">
            <li class="flex items-start gap-1.5">
                <span class="text-slate-400">•</span>
                <span>Click a colored African region to select it.</span>
            </li>
            <li class="flex items-start gap-1.5">
                <span class="text-slate-400">•</span>
                <span>Press Analyze after selecting a region.</span>
            </li>
            <li class="flex items-start gap-1.5">
                <span class="text-slate-400">•</span>
                <span>Zoom in to see country names.</span>
            </li>
        </ul>
        <div class="mt-2 pt-1 border-t border-slate-100">
            <a href="#how-it-works" class="text-blue-600 hover:underline font-medium text-[11px]">Learn more</a>
        </div>
    </div>

    <!-- Inset Mini-Map (Bottom right of map, matching reference image) -->
    <div class="absolute bottom-4 right-4 z-[400] hidden sm:block w-36 h-24 rounded-lg overflow-hidden border-2 border-white/80 shadow-xl bg-slate-100">
        <div id="earth-minimap" class="w-full h-full pointer-events-none"></div>
    </div>
</div>
<?php /**PATH D:\laragon\www\nasa-earth-change\nasa-laravel\resources\views/components/earth-map.blade.php ENDPATH**/ ?>