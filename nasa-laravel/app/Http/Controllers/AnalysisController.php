<?php

namespace App\Http\Controllers;

use App\Services\AnalysisService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Validator;
use Throwable;

class AnalysisController extends Controller
{

    public function __construct(protected AnalysisService $analysisService)
    {
    }

    /**
     * Return list of supported African regions and coverage.
     */
    public function regions(): JsonResponse
    {
        $data = $this->analysisService->getRegions();
        return response()->json($data);
    }

    /**
     * Return supported Earth science variables and scientific metadata.
     */
    public function variables(): JsonResponse
    {
        $variables = $this->analysisService->getVariables();
        return response()->json([
            'variables' => $variables,
        ]);
    }

    /**
     * Execute scientific trend analysis on real NASA observations.
     */
    public function analyze(Request $request): JsonResponse
    {
        $validator = Validator::make($request->all(), [
            'region' => ['required', 'string'],
            'variable' => ['nullable', 'string', 'in:temperature_anomaly,precipitation_mm'],
            'start_year' => ['nullable', 'integer', 'min:2004', 'max:2024'],
            'end_year' => ['nullable', 'integer', 'min:2004', 'max:2024'],
        ]);

        if ($validator->fails()) {
            return response()->json([
                'success' => false,
                'error' => 'Validation failed',
                'messages' => $validator->errors()->all(),
            ], 422);
        }

        $region = $request->input('region');
        $variable = $request->input('variable', 'temperature_anomaly');
        $startYear = $request->filled('start_year') ? (int) $request->input('start_year') : null;
        $endYear = $request->filled('end_year') ? (int) $request->input('end_year') : null;

        if ($startYear !== null && $endYear !== null && $startYear > $endYear) {
            return response()->json([
                'success' => false,
                'error' => 'Invalid date selection: start_year must be less than or equal to end_year.',
            ], 422);
        }

        try {
            $result = $this->analysisService->analyze($region, $variable, $startYear, $endYear);
            return response()->json($result);
        } catch (Throwable $e) {
            $statusCode = $e->getCode();
            if ($statusCode < 400 || $statusCode > 599) {
                $statusCode = 500;
            }

            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], $statusCode);
        }
    }

    /**
     * Get next-month environmental condition risk prediction (Model 1 v6).
     */
    public function predict(Request $request): JsonResponse
    {
        $region = $request->input('region');
        $variable = $request->input('variable');

        try {
            $result = $this->analysisService->predictNextMonth($region, $variable);
            return response()->json($result);
        } catch (Throwable $e) {
            $statusCode = $e->getCode();
            if ($statusCode < 400 || $statusCode > 599) {
                $statusCode = 500;
            }

            return response()->json([
                'success' => false,
                'error' => $e->getMessage(),
            ], $statusCode);
        }
    }
}
