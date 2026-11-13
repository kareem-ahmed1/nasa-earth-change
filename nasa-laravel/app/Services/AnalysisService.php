<?php

namespace App\Services;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use RuntimeException;

class AnalysisService
{
    protected string $baseUrl;

    public function __construct()
    {
        $this->baseUrl = rtrim(Config::get('services.analysis.url', 'http://127.0.0.1:8001'), '/');
    }

    /**
     * Return supported Earth science variables with verified metadata.
     */
    public function getVariables(): array
    {
        return [
            [
                'id' => 'temperature_anomaly',
                'name' => 'Surface Temperature Anomaly',
                'short_name' => 'Temperature Anomaly',
                'unit' => '°C',
                'source' => 'NASA GISTEMP v4 (GISS Surface Temperature Analysis)',
                'temporal_resolution' => 'Monthly',
                'coverage' => '2004–2024',
                'is_default' => true,
                'description' => 'Monthly surface temperature anomaly relative to regional base periods. Positive values indicate warmer than baseline.',
            ],
            [
                'id' => 'precipitation_mm',
                'name' => 'Precipitation',
                'short_name' => 'Precipitation',
                'unit' => 'mm/day',
                'source' => 'NASA POWER / MERRA-2 (Precipitation Corrected)',
                'temporal_resolution' => 'Monthly (Mean Daily Rate)',
                'coverage' => '2004–2024',
                'is_default' => false,
                'description' => 'Monthly mean daily precipitation rate (PRECTOTCORR) derived from MERRA-2 satellite-model assimilation.',
            ],
        ];
    }

    /**
     * Map Leaflet or URL region IDs to canonical Python API region labels.
     */
    public function normalizeRegion(string $region): string
    {
        $map = [
            'north-africa' => 'North_Africa',
            'north_africa' => 'North_Africa',
            'north africa' => 'North_Africa',
            'west-africa' => 'West_Africa',
            'west_africa' => 'West_Africa',
            'west africa' => 'West_Africa',
            'sahel_region' => 'West_Africa',
            'sahel' => 'West_Africa',
            'central-africa' => 'Central_Africa',
            'central_africa' => 'Central_Africa',
            'central africa' => 'Central_Africa',
            'east-africa' => 'East_Africa',
            'east_africa' => 'East_Africa',
            'east africa' => 'East_Africa',
            'southern-africa' => 'Southern_Africa',
            'southern_africa' => 'Southern_Africa',
            'southern africa' => 'Southern_Africa',
            'south_africa' => 'Southern_Africa',
            'south africa' => 'Southern_Africa',
            'all' => 'all',
        ];

        $key = strtolower(trim($region));
        return $map[$key] ?? $region;
    }

    /**
     * Human-friendly display label for canonical region.
     */
    public function getRegionDisplayName(string $canonical): string
    {
        $names = [
            'North_Africa' => 'North Africa',
            'West_Africa' => 'West Africa',
            'Central_Africa' => 'Central Africa',
            'East_Africa' => 'East Africa',
            'Southern_Africa' => 'Southern Africa',
            'all' => 'All Africa',
        ];

        return $names[$canonical] ?? str_replace('_', ' ', $canonical);
    }

    /**
     * Fetch supported regions and available coverage years from FastAPI backend.
     */
    public function getRegions(): array
    {
        try {
            $response = Http::timeout(5)->get("{$this->baseUrl}/regions");

            if ($response->successful()) {
                $data = $response->json();
                $regions = [];
                foreach ($data['regions'] ?? [] as $canonical) {
                    $regions[] = [
                        'id' => strtolower(str_replace('_', '-', $canonical)),
                        'canonical' => $canonical,
                        'name' => $this->getRegionDisplayName($canonical),
                    ];
                }
                return [
                    'regions' => $regions,
                    'available_years' => $data['available_years'] ?? ['start_year' => 2004, 'end_year' => 2024],
                ];
            }

            throw new RuntimeException("API error ({$response->status()}): {$response->body()}");
        } catch (ConnectionException $e) {
            Log::warning("FastAPI backend unreachable at {$this->baseUrl}: {$e->getMessage()}");
            // Return fallback region metadata matching the clean dataset
            return [
                'regions' => [
                    ['id' => 'north-africa', 'canonical' => 'North_Africa', 'name' => 'North Africa'],
                    ['id' => 'west-africa', 'canonical' => 'West_Africa', 'name' => 'West Africa'],
                    ['id' => 'central-africa', 'canonical' => 'Central_Africa', 'name' => 'Central Africa'],
                    ['id' => 'east-africa', 'canonical' => 'East_Africa', 'name' => 'East Africa'],
                    ['id' => 'southern-africa', 'canonical' => 'Southern_Africa', 'name' => 'Southern Africa'],
                ],
                'available_years' => ['start_year' => 2004, 'end_year' => 2024],
                'warning' => 'Analysis microservice is starting up.',
            ];
        }
    }

    /**
     * Execute full statistical analysis and retrieve chart series.
     */
    public function analyze(string $region, string $variable = 'temperature_anomaly', ?int $startYear = null, ?int $endYear = null): array
    {
        $canonicalRegion = $this->normalizeRegion($region);
        
        $params = [
            'region' => $canonicalRegion,
        ];
        if ($startYear !== null) {
            $params['start_year'] = $startYear;
        }
        if ($endYear !== null) {
            $params['end_year'] = $endYear;
        }

        try {
            // Call /analysis
            $analysisResponse = Http::timeout(10)->get("{$this->baseUrl}/analysis", $params);
            if (!$analysisResponse->successful()) {
                throw new RuntimeException("Analysis API returned {$analysisResponse->status()}: " . $analysisResponse->body());
            }

            // Call /charts
            $chartsResponse = Http::timeout(10)->get("{$this->baseUrl}/charts", $params);
            if (!$chartsResponse->successful()) {
                throw new RuntimeException("Charts API returned {$chartsResponse->status()}: " . $chartsResponse->body());
            }

            $analysisData = $analysisResponse->json();
            $chartsData = $chartsResponse->json();

            // Find variable metadata
            $variables = collect($this->getVariables())->keyBy('id');
            $varMeta = $variables->get($variable, $variables->get('temperature_anomaly'));

            // Extract the specific variable trend
            $trendData = $analysisData['trends'][$variable] ?? null;
            if (!$trendData) {
                throw new RuntimeException("Variable '{$variable}' trend not found in analysis output.");
            }

            // Calculate per-decade slope and formatted rates
            $slopePerYear = (float) ($trendData['sens_slope_per_year'] ?? $trendData['slope'] ?? 0);
            $slopePerDecade = $slopePerYear * 10;
            $pValue = (float) $trendData['p_value'];
            $isSignificant = $pValue < 0.05;

            // Generate plain language interpretation
            $direction = $trendData['direction'];
            $regionName = $this->getRegionDisplayName($canonicalRegion);
            $varName = $varMeta['name'];
            $unit = $varMeta['unit'];

            $interpretation = $this->generatePlainLanguageVerdict(
                $direction,
                $isSignificant,
                $pValue,
                $slopePerDecade,
                $unit,
                $varName,
                $regionName,
                $analysisData['requested_years']['start_year'],
                $analysisData['requested_years']['end_year']
            );

            // Time series observations for this variable
            $timeSeries = [];
            foreach ($chartsData['time_series'] ?? [] as $pt) {
                $timeSeries[] = [
                    'date' => $pt['date'],
                    'value' => $pt[$variable] ?? null,
                ];
            }

            // Annual trend points and Sen's slope line
            $trendSeries = $chartsData['trends'][$variable] ?? [];

            return [
                'success' => true,
                'region' => [
                    'id' => strtolower(str_replace('_', '-', $canonicalRegion)),
                    'canonical' => $canonicalRegion,
                    'name' => $regionName,
                ],
                'variable' => $varMeta,
                'period' => $analysisData['requested_years'],
                'metrics' => [
                    'direction' => $direction,
                    'slope_per_year' => round($slopePerYear, 4),
                    'slope_per_decade' => round($slopePerDecade, 4),
                    'p_value' => round($pValue, 5),
                    'kendall_tau' => round((float) ($trendData['kendall_tau'] ?? 0), 4),
                    'sample_size' => (int) ($trendData['sample_size'] ?? 0),
                    'test_name' => "Mann-Kendall Trend Test with Sen's Slope Estimator",
                    'significance_threshold' => 0.05,
                    'is_significant' => $isSignificant,
                    'verdict' => $isSignificant ? 'Statistically Significant' : 'Not Statistically Significant',
                    'interpretation' => $interpretation,
                ],
                'time_series' => $timeSeries,
                'annual_trend' => $trendSeries,
                'correlation' => $analysisData['correlation'] ?? null,
                'regression' => $analysisData['regression'] ?? null,
                'caveats' => $analysisData['assumptions'] ?? [
                    "Trend tests use annual aggregated means to reduce monthly seasonality.",
                    "Regional averages smooth localized climate extremes across macro-geographic zones.",
                    "Mann-Kendall p-values do not correct for potential serial autocorrelation.",
                    "Observational record covers 2004–2024 (21 years).",
                ],
                'provenance' => [
                    'dataset' => 'africa_climate_merged_2004_2024.csv',
                    'temperature_source' => 'NASA GISTEMP v4 (NetCDF spatial subset)',
                    'precipitation_source' => 'NASA POWER / MERRA-2 (Precipitation Corrected)',
                    'processing_engine' => 'Python SciPy / NumPy / Pandas statistical pipeline',
                ],
            ];
        } catch (ConnectionException $e) {
            Log::error("Analysis microservice unreachable: " . $e->getMessage());
            throw new RuntimeException("The scientific analysis microservice is currently unreachable. Please ensure the backend service is running on port 8001.", 503);
        }
    }

    /**
     * Get next-month environmental risk prediction from Model 1 v6.
     */
    public function predictNextMonth(?string $region = null, ?string $variable = null): array
    {
        $params = [];
        if ($region !== null) {
            $params['region'] = $this->normalizeRegion($region);
        }
        if ($variable !== null) {
            $params['variable'] = $variable;
        }

        try {
            $response = Http::timeout(10)->get("{$this->baseUrl}/predict", $params);
            if ($response->successful()) {
                return $response->json();
            }
            throw new RuntimeException("Prediction API error ({$response->status()}): " . $response->body());
        } catch (ConnectionException $e) {
            Log::error("Prediction service unreachable: " . $e->getMessage());
            throw new RuntimeException("The predictive AI model service is currently unreachable.", 503);
        }
    }

    protected function generatePlainLanguageVerdict(
        string $direction,
        bool $isSignificant,
        float $pValue,
        float $slopePerDecade,
        string $unit,
        string $varName,
        string $regionName,
        int $startYear,
        int $endYear
    ): string {
        $changeRate = sprintf("%+.3f %s/decade", $slopePerDecade, $unit);

        if ($direction === 'increasing') {
            if ($isSignificant) {
                return "Across {$regionName} from {$startYear} to {$endYear}, {$varName} demonstrates a statistically significant upward trend of {$changeRate} (p = " . sprintf("%.4f", $pValue) . " < 0.05). This indicates a measurable, persistent increase over the 21-year satellite record.";
            } else {
                return "Across {$regionName} from {$startYear} to {$endYear}, {$varName} shows an estimated rate of {$changeRate}, but the trend is not statistically significant (p = " . sprintf("%.4f", $pValue) . " ≥ 0.05). The observed variation cannot be distinguished from natural climatic variability.";
            }
        } elseif ($direction === 'decreasing') {
            if ($isSignificant) {
                return "Across {$regionName} from {$startYear} to {$endYear}, {$varName} demonstrates a statistically significant downward trend of {$changeRate} (p = " . sprintf("%.4f", $pValue) . " < 0.05).";
            } else {
                return "Across {$regionName} from {$startYear} to {$endYear}, {$varName} shows an estimated decrease of {$changeRate}, but the trend is not statistically significant (p = " . sprintf("%.4f", $pValue) . " ≥ 0.05).";
            }
        } else {
            return "Across {$regionName} from {$startYear} to {$endYear}, no clear directional trend was detected in {$varName} (p = " . sprintf("%.4f", $pValue) . ").";
        }
    }
}
