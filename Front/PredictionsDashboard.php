<?php
/**
 * Predictions Dashboard
 * Shows overall accuracy, team-by-team analysis, and ESPN comparison
 */

require_once 'TableGenerator.php';
require_once 'InjuryReport.php';

class PredictionsDashboard
{
    private const MARGIN_THRESHOLD = 5.0;

    private $predictionHistoryFile;
    private $teamManager;
    private $injuryReport;

    public function __construct()
    {
        $this->predictionHistoryFile = 'CSVFiles/prediction_history.json';
        $this->teamManager = new TeamManager();
        $this->injuryReport = new InjuryReport();
    }

    /**
     * Load prediction history from JSON
     */
    private function loadPredictionHistory(): array
    {
        if (!file_exists($this->predictionHistoryFile)) {
            return [];
        }

        $json = file_get_contents($this->predictionHistoryFile);
        $data = json_decode($json, true);
        
        return $data ?? [];
    }

    /**
     * Calculate overall accuracy statistics
     */
    private function calculateOverallStats(array $predictions, array $teamStats): array
    {
        $total = 0;
        $correct = 0;
        $hoopsightCorrect = 0;
        $espnCorrect = 0;
        $bothCorrect = 0;
        $totalMarginError = 0;
        $completedGames = 0;

        foreach ($predictions as $pred) {
            if (!isset($pred['actual_winner']) || empty($pred['actual_winner'])) {
                continue;
            }

            $completedGames++;
            $total++;

            // HoopSight accuracy
            if ($pred['predicted_winner'] === $pred['actual_winner']) {
                $correct++;
                $hoopsightCorrect++;
            }

            // ESPN accuracy
            if (isset($pred['espn_favorite_full']) && !empty($pred['espn_favorite_full'])) {
                if ($pred['espn_favorite_full'] === $pred['actual_winner']) {
                    $espnCorrect++;
                }

                // Both correct
                if ($pred['predicted_winner'] === $pred['actual_winner'] && 
                    $pred['espn_favorite_full'] === $pred['actual_winner']) {
                    $bothCorrect++;
                }
            }

            // Margin error
            if (isset($pred['margin_error'])) {
                $totalMarginError += abs($pred['margin_error']);
            }
        }

        $hoopsightAccuracy = $total > 0 ? ($hoopsightCorrect / $total) * 100 : 0;
        $espnAccuracy = $total > 0 ? ($espnCorrect / $total) * 100 : 0;
        $avgMarginError = $completedGames > 0 ? $totalMarginError / $completedGames : 0;

        $teamCount = 0;
        $teamAccuracySum = 0.0;
        $teamEspnAccuracySum = 0.0;

        foreach ($teamStats as $stats) {
            $gamesPlayed = $stats['total'] ?? 0;
            if ($gamesPlayed > 0) {
                $teamCount++;
                $teamAccuracySum += $stats['accuracy'] ?? 0;
                $teamEspnAccuracySum += $stats['espn_accuracy'] ?? 0;
            }
        }

        $teamAvgAccuracy = $teamCount > 0 ? $teamAccuracySum / $teamCount : 0;
        $teamAvgEspnAccuracy = $teamCount > 0 ? $teamEspnAccuracySum / $teamCount : 0;

        return [
            'total_predictions' => count($predictions),
            'completed_games' => $completedGames,
            'hoopsight_correct' => $hoopsightCorrect,
            'hoopsight_accuracy' => $hoopsightAccuracy,
            'espn_correct' => $espnCorrect,
            'espn_accuracy' => $espnAccuracy,
            'both_correct' => $bothCorrect,
            'avg_margin_error' => $avgMarginError,
            'advantage' => $hoopsightAccuracy - $espnAccuracy,
            'team_avg_accuracy' => $teamAvgAccuracy,
            'team_avg_espn_accuracy' => $teamAvgEspnAccuracy,
            'team_avg_advantage' => $teamAvgAccuracy - $teamAvgEspnAccuracy,
        ];
    }

    /**
     * Group predictions by team
     */
    private function groupByTeam(array $predictions): array
    {
        $teamStats = [];

        foreach ($predictions as $pred) {
            // Process for home team
            $homeTeam = $pred['home_team'] ?? '';
            if (!isset($teamStats[$homeTeam])) {
                $teamStats[$homeTeam] = [
                    'team' => $homeTeam,
                    'games' => [],
                    'total' => 0,
                    'correct' => 0,
                    'espn_correct' => 0,
                    'injury_impact' => 0,
                    'total_margin_error' => 0.0,
                    'margin_samples' => 0,
                    'within_margin_threshold' => 0
                ];
            }
            $teamStats[$homeTeam]['games'][] = $pred;
            
            if (isset($pred['actual_winner']) && !empty($pred['actual_winner'])) {
                $teamStats[$homeTeam]['total']++;
                if ($pred['predicted_winner'] === $pred['actual_winner']) {
                    $teamStats[$homeTeam]['correct']++;
                }
                if (isset($pred['espn_favorite_full']) && 
                    $pred['espn_favorite_full'] === $pred['actual_winner']) {
                    $teamStats[$homeTeam]['espn_correct']++;
                }
                if (isset($pred['margin_error']) && is_numeric($pred['margin_error'])) {
                    $error = abs((float)$pred['margin_error']);
                    $teamStats[$homeTeam]['total_margin_error'] += $error;
                    $teamStats[$homeTeam]['margin_samples']++;
                    if ($error <= self::MARGIN_THRESHOLD) {
                        $teamStats[$homeTeam]['within_margin_threshold']++;
                    }
                }
            }

            // Process for away team
            $awayTeam = $pred['away_team'] ?? '';
            if (!isset($teamStats[$awayTeam])) {
                $teamStats[$awayTeam] = [
                    'team' => $awayTeam,
                    'games' => [],
                    'total' => 0,
                    'correct' => 0,
                    'espn_correct' => 0,
                    'injury_impact' => 0,
                    'total_margin_error' => 0.0,
                    'margin_samples' => 0,
                    'within_margin_threshold' => 0
                ];
            }
            $teamStats[$awayTeam]['games'][] = $pred;
            
            if (isset($pred['actual_winner']) && !empty($pred['actual_winner'])) {
                $teamStats[$awayTeam]['total']++;
                if ($pred['predicted_winner'] === $pred['actual_winner']) {
                    $teamStats[$awayTeam]['correct']++;
                }
                if (isset($pred['espn_favorite_full']) && 
                    $pred['espn_favorite_full'] === $pred['actual_winner']) {
                    $teamStats[$awayTeam]['espn_correct']++;
                }
                if (isset($pred['margin_error']) && is_numeric($pred['margin_error'])) {
                    $error = abs((float)$pred['margin_error']);
                    $teamStats[$awayTeam]['total_margin_error'] += $error;
                    $teamStats[$awayTeam]['margin_samples']++;
                    if ($error <= self::MARGIN_THRESHOLD) {
                        $teamStats[$awayTeam]['within_margin_threshold']++;
                    }
                }
            }
        }

        // Calculate percentages and injury impact
        foreach ($teamStats as $team => &$stats) {
            $stats['accuracy'] = $stats['total'] > 0 ? 
                ($stats['correct'] / $stats['total']) * 100 : 0;
            $stats['espn_accuracy'] = $stats['total'] > 0 ? 
                ($stats['espn_correct'] / $stats['total']) * 100 : 0;
            $marginSamples = $stats['margin_samples'] ?? 0;
            $stats['avg_margin_error'] = $marginSamples > 0 ?
                $stats['total_margin_error'] / $marginSamples : null;
            $stats['margin_within_pct'] = $marginSamples > 0 ?
                ($stats['within_margin_threshold'] / $marginSamples) * 100 : null;
            
            // Get injury impact
            $fullTeamName = $this->teamManager->getFullTeamName($team);
            $stats['injury_impact'] = $this->injuryReport->getTeamInjuryImpact($fullTeamName);
        }

        // Sort by accuracy descending
        uasort($teamStats, function($a, $b) {
            return $b['accuracy'] <=> $a['accuracy'];
        });

        return $teamStats;
    }

    /**
     * Generate overall statistics card
     */
    public function generateOverallStatsCard(array $stats): string
    {
        $hoopsightClass = $stats['advantage'] > 0 ? 'winning' : 'losing';
        $advantageText = $stats['advantage'] > 0 ? '+' . number_format($stats['advantage'], 1) : number_format($stats['advantage'], 1);
        $teamAdvantage = $stats['team_avg_advantage'] ?? 0;
        $teamAdvantageClass = $teamAdvantage > 0 ? 'winning' : 'losing';
        $teamAdvantageText = $teamAdvantage > 0 ? '+' . number_format($teamAdvantage, 1) : number_format($teamAdvantage, 1);

        $completedGames = (int) ($stats['completed_games'] ?? 0);
        $hoopsightSummary = $completedGames > 0
            ? $stats['hoopsight_correct'] . ' of ' . $completedGames . ' games correct'
            : 'No completed games yet';
        $espnSummary = $completedGames > 0
            ? $stats['espn_correct'] . ' of ' . $completedGames . ' games correct'
            : 'No completed games yet';

        $avgMarginValue = $stats['avg_margin_error'] ?? null;
        $avgMarginText = ($avgMarginValue !== null)
            ? $this->formatMargin((float) $avgMarginValue) . ' pts'
            : '—';

        $hoopsightPercent = $this->formatPercent($stats['hoopsight_accuracy'] ?? 0.0);
        $espnPercent = $this->formatPercent($stats['espn_accuracy'] ?? 0.0);
        $teamAvgHoopsight = $this->formatPercent($stats['team_avg_accuracy'] ?? 0.0);
        $teamAvgEspn = $this->formatPercent($stats['team_avg_espn_accuracy'] ?? 0.0);

        return <<<HTML
        <div class="stats-card">
            <h2>🏀 HoopSight Advantage Story</h2>
            <div class="stats-hero">
                <div class="hero-block primary">
                    <span class="hero-label">HoopSight Accuracy</span>
                    <span class="hero-value">{$hoopsightPercent}</span>
                    <span class="hero-sub">{$hoopsightSummary}</span>
                </div>
                <div class="hero-divider">vs</div>
                <div class="hero-block secondary">
                    <span class="hero-label">ESPN Accuracy</span>
                    <span class="hero-value">{$espnPercent}</span>
                    <span class="hero-sub">{$espnSummary}</span>
                </div>
                <div class="hero-badge {$hoopsightClass}">
                    <span class="hero-badge-label">HoopSight Edge</span>
                    <span class="hero-badge-value">{$advantageText}%</span>
                    <span class="hero-badge-note">{$this->getAdvantageText($stats['advantage'])}</span>
                </div>
            </div>
            <div class="stats-story">
                <div class="story-grid">
                    <div class="story-item">
                        <span class="story-icon">📦</span>
                        <div>
                            <span class="story-label">Forecasts Published</span>
                            <span class="story-value">{$stats['total_predictions']}</span>
                        </div>
                    </div>
                    <div class="story-item">
                        <span class="story-icon">✅</span>
                        <div>
                            <span class="story-label">Final Games Scored</span>
                            <span class="story-value">{$stats['completed_games']}</span>
                        </div>
                    </div>
                    <div class="story-item">
                        <span class="story-icon">📊</span>
                        <div>
                            <span class="story-label">Avg Margin Error</span>
                            <span class="story-value">{$avgMarginText}</span>
                        </div>
                    </div>
                    <div class="story-item">
                        <span class="story-icon">🧮</span>
                        <div>
                            <span class="story-label">Team Avg Accuracy</span>
                            <span class="story-value">HoopSight {$teamAvgHoopsight} · ESPN {$teamAvgEspn}</span>
                        </div>
                    </div>
                    <div class="story-item {$teamAdvantageClass}">
                        <span class="story-icon">🚀</span>
                        <div>
                            <span class="story-label">Team-Weighted Edge</span>
                            <span class="story-value">{$teamAdvantageText}%</span>
                            <span class="story-note">Balances schedule volume</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        HTML;
    }

    /**
     * Generate team-by-team analysis table
     */
    public function generateTeamAnalysisTable(array $teamStats): string
    {
        $html = '<div class="team-analysis">';
        $html .= '<h2>📊 Team-by-Team Prediction Analysis</h2>';
        $html .= '<table class="analysis-table">';
    $html .= '<thead><tr>';
    $html .= '<th>Team</th>';
    $html .= '<th>Games</th>';
    $html .= '<th>HoopSight<br>Correct</th>';
    $html .= '<th>HoopSight<br>Accuracy</th>';
    $html .= '<th>ESPN<br>Accuracy</th>';
    $html .= '<th>Advantage</th>';
    $html .= '<th>Avg Margin Error</th>';
    $html .= '<th>Within 5 pts</th>';
    $html .= '</tr></thead><tbody>';

        foreach ($teamStats as $team => $stats) {
            $advantage = $stats['accuracy'] - $stats['espn_accuracy'];
            $advantageClass = $advantage > 0 ? 'positive' : ($advantage < 0 ? 'negative' : 'neutral');
            $advantageText = $advantage > 0 ? '+' . number_format($advantage, 1) : number_format($advantage, 1);
            
            $fullTeamName = $this->teamManager->getFullTeamName($team);

            $html .= '<tr>';
            $html .= "<td class='team-cell'>";
            $html .= "<img src='Assets/Logos/{$team}.png' alt='{$fullTeamName}' class='team-logo-small' onerror='this.style.display=\"none\"'/>";
            $html .= "<strong>{$fullTeamName}</strong></td>";
            $html .= "<td>{$stats['total']}</td>";
            $html .= "<td>{$stats['correct']}</td>";
            $html .= "<td class='accuracy-cell'>" . $this->formatPercent($stats['accuracy']) . "</td>";
            $html .= "<td class='accuracy-cell'>" . $this->formatPercent($stats['espn_accuracy']) . "</td>";
            $html .= "<td class='advantage-cell {$advantageClass}'>{$advantageText}%</td>";
            $avgMargin = isset($stats['avg_margin_error']) && $stats['avg_margin_error'] !== null ? $this->formatMargin($stats['avg_margin_error']) . ' pts' : '—';
            $withinPct = isset($stats['margin_within_pct']) && $stats['margin_within_pct'] !== null ? $this->formatPercent($stats['margin_within_pct']) : '—';
            $html .= "<td>{$avgMargin}</td>";
            $html .= "<td>{$withinPct}</td>";
            $html .= '</tr>';
        }

        $html .= '</tbody></table>';
        $html .= '</div>';

        return $html;
    }

    /**
     * Generate game-by-game results table for a specific team
     */
    public function generateTeamGamesTable(string $teamName, array $games): string
    {
        $fullTeamName = $this->teamManager->getFullTeamName($teamName);
        $chartLabels = [];
        $chartHoopsightEdge = [];
        $chartEspnEdge = [];
        $chartActualMargin = [];
        $rowsHtml = '';

        foreach ($games as $game) {
            $displayDate = $game['display_date'] ?? $game['game_date'] ?? '';
            $chartLabels[] = $displayDate;

            $homeShort = $game['home_team'] ?? '';
            $awayShort = $game['away_team'] ?? '';
            $isHome = $homeShort === $teamName;
            $opponentShort = $isHome ? ($awayShort ?: 'TBD') : ($homeShort ?: 'TBD');
            $opponentFull = $this->teamManager->getFullTeamName($opponentShort);
            $opponentLabel = $isHome ? 'vs. ' . $opponentFull : '@ ' . $opponentFull;

            $hoopsightCell = $this->formatHoopSightCell($game);
            $espnCell = $this->formatEspnCell($game);

            $confidenceValue = isset($game['confidence_gap_pct']) && is_numeric($game['confidence_gap_pct'])
                ? (float) $game['confidence_gap_pct']
                : null;
            $confidenceBucket = $game['confidence_bucket'] ?? null;
            $confidenceDisplay = '—';
            if ($confidenceValue !== null) {
                $confidenceDisplay = number_format($confidenceValue, 1) . '%';
                if (!empty($confidenceBucket)) {
                    $confidenceDisplay .= ' (' . htmlspecialchars($confidenceBucket) . ')';
                }
            }

            $predictedWinner = $game['predicted_winner'] ?? '';
            $espnPick = $game['espn_favorite_full'] ?? 'N/A';
            $actualWinner = $game['actual_winner'] ?? 'Pending';
            $actualLabel = (!empty($actualWinner) && $actualWinner !== 'Pending') ? htmlspecialchars($actualWinner) : 'Pending';

            $projectedMarginValue = null;
            if (isset($game['expected_margin']) && is_numeric($game['expected_margin'])) {
                $marginValue = (float) $game['expected_margin'];
                $projectedMarginValue = ($predictedWinner === $teamName) ? $marginValue : -$marginValue;
            }
            $projectedClass = '';
            $projectedDisplay = '—';
            if ($projectedMarginValue !== null) {
                if ($projectedMarginValue > 0) {
                    $projectedClass = 'margin-positive';
                } elseif ($projectedMarginValue < 0) {
                    $projectedClass = 'margin-negative';
                } else {
                    $projectedClass = 'margin-neutral';
                }
                $projectedDisplay = number_format($projectedMarginValue, 1) . ' pts';
            }

            $actualMarginValue = null;
            if (isset($game['actual_margin']) && is_numeric($game['actual_margin']) && $actualWinner !== 'Pending') {
                $marginValue = (float) $game['actual_margin'];
                $actualMarginValue = ($actualWinner === $teamName) ? $marginValue : -$marginValue;
            }
            $actualMarginDisplay = '—';
            $actualMarginClass = '';
            if ($actualMarginValue !== null) {
                if ($actualMarginValue > 0) {
                    $actualMarginClass = 'margin-positive';
                } elseif ($actualMarginValue < 0) {
                    $actualMarginClass = 'margin-negative';
                } else {
                    $actualMarginClass = 'margin-neutral';
                }
                $actualMarginDisplay = number_format($actualMarginValue, 1) . ' pts';
            }

            $modelHomePct = isset($game['model_home_pct']) && is_numeric($game['model_home_pct'])
                ? (float) $game['model_home_pct']
                : null;
            $modelAwayPct = isset($game['model_away_pct']) && is_numeric($game['model_away_pct'])
                ? (float) $game['model_away_pct']
                : null;
            $teamModelPct = $isHome ? $modelHomePct : $modelAwayPct;
            $chartHoopsightEdge[] = $teamModelPct !== null ? round($teamModelPct - 50.0, 1) : null;

            $espnHomePct = isset($game['espn_home_pct']) && is_numeric($game['espn_home_pct'])
                ? (float) $game['espn_home_pct']
                : null;
            $espnAwayPct = isset($game['espn_away_pct']) && is_numeric($game['espn_away_pct'])
                ? (float) $game['espn_away_pct']
                : null;
            $teamEspnPct = $isHome ? $espnHomePct : $espnAwayPct;
            $chartEspnEdge[] = $teamEspnPct !== null ? round($teamEspnPct - 50.0, 1) : null;

            $chartActualMargin[] = $actualMarginValue;

            $resultClass = '';
            $resultText = '-';

            if ($actualWinner !== 'Pending' && !empty($actualWinner)) {
                $hoopsightCorrect = ($predictedWinner === $actualWinner);
                $espnCorrect = ($espnPick === $actualWinner);

                if ($hoopsightCorrect && $espnCorrect) {
                    $resultClass = 'both-correct';
                    $resultText = '✓ Both';
                } elseif ($hoopsightCorrect) {
                    $resultClass = 'hoopsight-correct';
                    $resultText = '✓ HoopSight';
                } elseif ($espnCorrect) {
                    $resultClass = 'espn-correct';
                    $resultText = '✓ ESPN';
                } else {
                    $resultClass = 'both-wrong';
                    $resultText = '✗ Both';
                }
            }

            $rowsHtml .= "<tr>";
            $rowsHtml .= "<td>" . htmlspecialchars($displayDate) . "</td>";
            $rowsHtml .= "<td>" . htmlspecialchars($opponentLabel) . "</td>";
            $rowsHtml .= "<td>{$hoopsightCell}</td>";
            $rowsHtml .= "<td>{$espnCell}</td>";
            $rowsHtml .= "<td>{$confidenceDisplay}</td>";
            $rowsHtml .= "<td class='margin-cell {$projectedClass}'>{$projectedDisplay}</td>";
            $rowsHtml .= "<td><strong>{$actualLabel}</strong></td>";
            $rowsHtml .= "<td class='result-cell {$resultClass}'>{$resultText}</td>";
            $rowsHtml .= "<td class='margin-cell {$actualMarginClass}'>{$actualMarginDisplay}</td>";
            $rowsHtml .= "</tr>";
        }

        $maxChartPoints = 30;
        if (count($chartLabels) > $maxChartPoints) {
            $offset = count($chartLabels) - $maxChartPoints;
            $chartLabels = array_slice($chartLabels, $offset);
            $chartHoopsightEdge = array_slice($chartHoopsightEdge, $offset);
            $chartEspnEdge = array_slice($chartEspnEdge, $offset);
            $chartActualMargin = array_slice($chartActualMargin, $offset);
        }

        $seriesHasData = false;
        foreach ([$chartHoopsightEdge, $chartEspnEdge, $chartActualMargin] as $series) {
            if (count(array_filter($series, static function ($value) { return $value !== null; })) > 0) {
                $seriesHasData = true;
                break;
            }
        }

        $chartMarkup = '';
        if ($seriesHasData) {
            $chartSlug = strtolower(preg_replace('/[^a-z0-9]+/i', '-', $teamName));
            $chartId = 'team-chart-' . $chartSlug;
            $chartData = [
                'labels' => $chartLabels,
                'hoopsightEdge' => $chartHoopsightEdge,
                'espnEdge' => $chartEspnEdge,
                'actualMargin' => $chartActualMargin,
            ];
            $chartJson = json_encode($chartData, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
            if ($chartJson === false) {
                $chartJson = '{}';
            }

            $chartMarkup .= "<div class='team-chart-container'><h4>Confidence vs Outcome</h4><canvas id='{$chartId}'></canvas></div>";
            $chartMarkup .= "<script>window.__hsTeamCharts = window.__hsTeamCharts || [];window.__hsTeamCharts.push({id:'{$chartId}',data:{$chartJson}});</script>";
        }

        $html = "<div class='team-games'>";
        $html .= "<h3>Game Results: {$fullTeamName}</h3>";
        $html .= "<p class='games-note'>Win probabilities reflect model output at prediction time. Positive projected/actual margins favor " . htmlspecialchars($fullTeamName) . ".</p>";

        if ($chartMarkup !== '') {
            $html .= $chartMarkup;
        }

        $html .= "<table class='games-table'>";
        $html .= "<thead><tr>";
        $html .= "<th>Date</th>";
        $html .= "<th>Opponent</th>";
        $html .= "<th>HoopSight</th>";
        $html .= "<th>ESPN</th>";
        $html .= "<th>Confidence Gap (HS)</th>";
        $html .= "<th>Projected Margin</th>";
        $html .= "<th>Actual Winner</th>";
        $html .= "<th>Result</th>";
        $html .= "<th>Actual Margin</th>";
        $html .= "</tr></thead><tbody>";
        $html .= $rowsHtml;
        $html .= "</tbody></table>";
        $html .= "</div>";

        return $html;
    }

    /**
     * Generate complete dashboard
     */
    public function generateDashboard(): string
    {
        $predictions = $this->loadPredictionHistory();
        
        if (empty($predictions)) {
            return "<div class='no-data'>
                        <h2>No Prediction Data Available</h2>
                        <p>Run the prediction model to generate data.</p>
                    </div>";
        }

    $teamStats = $this->groupByTeam($predictions);
    $overallStats = $this->calculateOverallStats($predictions, $teamStats);

        $html = '<div class="predictions-dashboard">';
        
        // Overall stats
        $html .= $this->generateOverallStatsCard($overallStats);
        
        // Team analysis
        $html .= $this->generateTeamAnalysisTable($teamStats);
        
        // Team dropdown for detailed view
        $html .= '<div class="team-selector">';
        $html .= '<h3>View Team Details</h3>';
        $html .= '<select id="team-detail-select" onchange="showTeamDetails(this.value)">';
        $html .= '<option value="">Select a team...</option>';
        
        foreach ($teamStats as $team => $stats) {
            $fullName = $this->teamManager->getFullTeamName($team);
            $html .= "<option value='{$team}'>{$fullName} ({$stats['total']} games)</option>";
        }
        
        $html .= '</select>';
        $html .= '</div>';
        
        // Hidden team details sections
        $html .= '<div id="team-details-container">';
        foreach ($teamStats as $team => $stats) {
            $html .= "<div id='team-{$team}' class='team-detail' style='display:none;'>";
            $html .= $this->generateTeamGamesTable($team, $stats['games']);
            $html .= '</div>';
        }
        $html .= '</div>';
        
        $html .= '</div>';

                    $html .= '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>';
                $html .= <<<HTML
<script>
(function() {
    if (window.__hsChartsInit) { return; }
    window.__hsChartsInit = true;

    function hasSeriesData(series) {
        if (!Array.isArray(series)) { return false; }
        for (var i = 0; i < series.length; i += 1) {
            if (series[i] !== null && series[i] !== undefined) {
                return true;
            }
        }
        return false;
    }

    function renderCharts() {
        if (!window.__hsTeamCharts || !Array.isArray(window.__hsTeamCharts)) {
            return;
        }
        window.__hsTeamCharts.forEach(function(entry) {
            var canvas = document.getElementById(entry.id);
            if (!canvas || canvas.dataset.rendered === 'true') {
                return;
            }
            var isVisible = canvas.offsetParent !== null && canvas.clientWidth > 0 && canvas.clientHeight > 0;
            if (!isVisible) {
                return;
            }
            var ctx = canvas.getContext('2d');
            if (!ctx) {
                canvas.dataset.rendered = 'true';
                return;
            }

            var data = entry.data || {};
            var labels = data.labels || [];
            var hsEdge = data.hoopsightEdge || [];
            var espnEdge = data.espnEdge || [];
            var actualMargin = data.actualMargin || [];

            var datasets = [];
            if (hasSeriesData(hsEdge)) {
                datasets.push({
                    type: 'line',
                    label: 'HoopSight Edge (%)',
                    data: hsEdge,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    tension: 0.35,
                    spanGaps: true,
                    yAxisID: 'y'
                });
            }
            if (hasSeriesData(espnEdge)) {
                datasets.push({
                    type: 'line',
                    label: 'ESPN Edge (%)',
                    data: espnEdge,
                    borderColor: '#fbbf24',
                    backgroundColor: 'rgba(251, 191, 36, 0.12)',
                    borderDash: [6, 4],
                    tension: 0.35,
                    spanGaps: true,
                    yAxisID: 'y'
                });
            }
            if (hasSeriesData(actualMargin)) {
                datasets.push({
                    type: 'bar',
                    label: 'Actual Margin (pts)',
                    data: actualMargin,
                    backgroundColor: 'rgba(129, 140, 248, 0.35)',
                    borderColor: '#818cf8',
                    borderWidth: 1,
                    yAxisID: 'y1'
                });
            }

            canvas.dataset.rendered = 'true';
            if (datasets.length === 0) {
                return;
            }

            new Chart(ctx, {
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    scales: {
                        y: {
                            position: 'left',
                            title: { display: true, text: 'Win Edge (%)', color: '#dbeafe' },
                            grid: { color: 'rgba(148, 163, 184, 0.2)' },
                            ticks: {
                                color: '#e5e7eb',
                                callback: function(value) { return value + '%'; }
                            }
                        },
                        y1: {
                            position: 'right',
                            title: { display: true, text: 'Margin (pts)', color: '#dbeafe' },
                            grid: { drawOnChartArea: false },
                            ticks: {
                                color: '#e5e7eb',
                                callback: function(value) { return value + ' pts'; }
                            }
                        },
                        x: {
                            grid: { color: 'rgba(148, 163, 184, 0.15)' },
                            ticks: { color: '#e5e7eb' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#f3f4f6' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    var label = context.dataset.label || '';
                                    if (context.parsed.y === null) {
                                        return label;
                                    }
                                    if (context.dataset.yAxisID === 'y') {
                                        return label + ': ' + context.parsed.y + '%';
                                    }
                                    return label + ': ' + context.parsed.y + ' pts';
                                }
                            }
                        }
                    }
                }
            });
        });
    }

    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        renderCharts();
    } else {
        document.addEventListener('DOMContentLoaded', renderCharts);
    }

        window.renderHoopSightCharts = renderCharts;
})();
</script>
HTML;

        return $html;
    }

    // Helper functions
    private function formatHoopSightCell(array $game): string
    {
        $homeShort = $game['home_team'] ?? '';
        $awayShort = $game['away_team'] ?? '';
        $homeName = $game['home_team_full'] ?? $this->teamManager->getFullTeamName($homeShort);
        $awayName = $game['away_team_full'] ?? $this->teamManager->getFullTeamName($awayShort);

        $homePct = isset($game['model_home_pct']) ? number_format((float)$game['model_home_pct'], 1) : null;
        $awayPct = isset($game['model_away_pct']) ? number_format((float)$game['model_away_pct'], 1) : null;

        if ($homePct === null && $awayPct === null) {
            return "<div class='prediction-cell'><span class='source-label'>HoopSight</span><span class='no-data'>No probability data</span></div>";
        }

        $favoriteShort = $game['predicted_winner'] ?? '';
        $homeFavorite = $favoriteShort === $homeShort;
        $awayFavorite = $favoriteShort === $awayShort;

        $html = "<div class='prediction-cell'>";
        $html .= "<span class='source-label'>HoopSight</span>";
        $html .= "<div class='prediction-row'><span class='prediction-team" . ($homeFavorite ? " favorite" : "") . "'>" . htmlspecialchars($homeName) . "</span>";
        if ($homePct !== null) {
            $html .= "<span class='prediction-pct'>{$homePct}%</span>";
        }
        $html .= "</div>";
        $html .= "<div class='prediction-row'><span class='prediction-team" . ($awayFavorite ? " favorite" : "") . "'>" . htmlspecialchars($awayName) . "</span>";
        if ($awayPct !== null) {
            $html .= "<span class='prediction-pct'>{$awayPct}%</span>";
        }
        $html .= "</div>";
        $html .= "</div>";

        return $html;
    }

    private function formatEspnCell(array $game): string
    {
        $homeShort = $game['home_team'] ?? '';
        $awayShort = $game['away_team'] ?? '';
        $homeName = $game['home_team_full'] ?? $this->teamManager->getFullTeamName($homeShort);
        $awayName = $game['away_team_full'] ?? $this->teamManager->getFullTeamName($awayShort);

        $homePct = isset($game['espn_home_pct']) && $game['espn_home_pct'] !== null
            ? number_format((float)$game['espn_home_pct'], 1)
            : null;
        $awayPct = isset($game['espn_away_pct']) && $game['espn_away_pct'] !== null
            ? number_format((float)$game['espn_away_pct'], 1)
            : null;

        if ($homePct === null && $awayPct === null) {
            return "<div class='prediction-cell'><span class='source-label'>ESPN</span><span class='no-data'>No ESPN data</span></div>";
        }

        $favoriteAbbr = $game['espn_favorite_abbr'] ?? '';
        $homeAbbr = $game['home_team_abbr'] ?? '';
        $awayAbbr = $game['away_team_abbr'] ?? '';
        $homeFavorite = $favoriteAbbr !== '' && $favoriteAbbr === $homeAbbr;
        $awayFavorite = $favoriteAbbr !== '' && $favoriteAbbr === $awayAbbr;

        $confidenceGap = isset($game['espn_confidence_gap']) && $game['espn_confidence_gap'] !== null
            ? number_format((float)$game['espn_confidence_gap'], 1) . '%'
            : null;
        $alignment = $game['espn_alignment'] ?? null;
        $delta = isset($game['espn_model_delta_pct']) && $game['espn_model_delta_pct'] !== null
            ? number_format((float)$game['espn_model_delta_pct'], 1) . '%'
            : null;

        $html = "<div class='prediction-cell'>";
        $html .= "<span class='source-label'>ESPN</span>";
        $html .= "<div class='prediction-row'><span class='prediction-team" . ($homeFavorite ? " favorite" : "") . "'>" . htmlspecialchars($homeName) . "</span>";
        if ($homePct !== null) {
            $html .= "<span class='prediction-pct'>{$homePct}%</span>";
        }
        $html .= "</div>";
        $html .= "<div class='prediction-row'><span class='prediction-team" . ($awayFavorite ? " favorite" : "") . "'>" . htmlspecialchars($awayName) . "</span>";
        if ($awayPct !== null) {
            $html .= "<span class='prediction-pct'>{$awayPct}%</span>";
        }
        $html .= "</div>";

        if ($alignment) {
            $html .= "<div class='prediction-gap'>Alignment: " . htmlspecialchars($alignment) . '</div>';
        }
        if ($confidenceGap !== null) {
            $html .= "<div class='prediction-gap'>Confidence Gap: {$confidenceGap}</div>";
        }
        if ($delta !== null) {
            $html .= "<div class='prediction-gap'>Delta vs HoopSight: {$delta}</div>";
        }

        $html .= "</div>";

        return $html;
    }

    private function formatPercent(float $value): string
    {
        return number_format($value, 1) . '%';
    }

    private function formatMargin(float $value): string
    {
        return number_format($value, 1);
    }

    private function getAdvantageText(float $advantage): string
    {
        if ($advantage > 5) return '🔥 Significantly Better';
        if ($advantage > 0) return '✓ Better';
        if ($advantage < -5) return '❌ Significantly Worse';
        if ($advantage < 0) return '↓ Worse';
        return '= Equal';
    }

}

