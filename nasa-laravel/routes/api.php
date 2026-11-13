<?php

use App\Http\Controllers\AnalysisController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Earth Trend Explorer scientific analysis routes
Route::get('/regions', [AnalysisController::class, 'regions']);
Route::get('/variables', [AnalysisController::class, 'variables']);
Route::get('/analyze', [AnalysisController::class, 'analyze']);
Route::post('/analyze', [AnalysisController::class, 'analyze']);
Route::get('/predict', [AnalysisController::class, 'predict']);
Route::post('/predict', [AnalysisController::class, 'predict']);
