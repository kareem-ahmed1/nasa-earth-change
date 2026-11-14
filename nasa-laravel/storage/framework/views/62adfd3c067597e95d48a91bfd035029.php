<!DOCTYPE html>
<html lang="<?php echo e(str_replace('_', '-', app()->getLocale())); ?>" class="light">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="csrf-token" content="<?php echo e(csrf_token()); ?>">

        <title><?php echo e(config('app.name', 'Earth Trend Explorer')); ?> — Explore. Analyze. Understand Our Planet.</title>

        <!-- Fonts -->
        <link rel="preconnect" href="https://fonts.bunny.net">
        <link href="https://fonts.bunny.net/css?family=figtree:400,500,600,700,800&display=swap" rel="stylesheet" />

        <!-- Scripts & Styles -->
        <?php echo app('Illuminate\Foundation\Vite')(['resources/css/app.css', 'resources/js/app.js']); ?>
    </head>
    <body class="font-sans antialiased bg-slate-50 text-slate-800 min-h-screen flex flex-col selection:bg-emerald-500 selection:text-white">
        <div class="flex-1 flex flex-col">
            <?php echo $__env->make('layouts.navigation', array_diff_key(get_defined_vars(), ['__data' => 1, '__path' => 1]))->render(); ?>

            <?php if(isset($header)): ?>
                <header class="border-b border-slate-200 bg-white">
                    <div class="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
                        <?php echo e($header); ?>

                    </div>
                </header>
            <?php endif; ?>

            <main class="flex-1">
                <?php echo e($slot); ?>

            </main>
        </div>

        <footer class="w-full border-t border-slate-200 bg-white py-5 px-4 sm:px-8 text-xs text-slate-500 mt-12">
            <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
                <div class="flex items-center gap-2">
                    <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    <span>Earth Trend Explorer • Explore. Analyze. Understand Our Planet.</span>
                </div>
                <div class="flex items-center gap-4">
                    <a href="<?php echo e(url('/#about')); ?>" class="hover:text-slate-800 hover:underline">About</a>
                    <a href="<?php echo e(url('/#how-it-works')); ?>" class="hover:text-slate-800 hover:underline">How it works</a>
                </div>
            </div>
        </footer>
    </body>
</html>
<?php /**PATH D:\laragon\www\nasa-earth-change\nasa-laravel\resources\views/layouts/app.blade.php ENDPATH**/ ?>