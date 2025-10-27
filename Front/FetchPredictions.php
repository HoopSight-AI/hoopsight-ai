<?php
require_once 'InjuryReport.php';

if (!isset($_GET['team'])) {
    error_log("Error: No team selected.");
    echo "<p>Error: No team selected.</p>";
    exit;
}

$team = $_GET['team'];
$dataFile = "CSVFiles/prediction_results.csv"; //make sure file paths are right if u are ediitng this

error_log("Selected team: $team");

// Check if the predictions file exists
if (!file_exists($dataFile)) {
    error_log("Error: Predictions file not found at $dataFile.");
    echo "<p>Error: Predictions file not found.</p>";
    exit;
}

// Generate table for the selected team
function fetchPredictionsForTeam(string $team, string $csvFilePath): string
{
    error_log("Opening CSV file: $csvFilePath");

    // Initialize injury report
    $injuryReport = new InjuryReport();

    // Read the CSV file
    $rows = array_map('str_getcsv', file($csvFilePath));
    error_log("CSV file loaded. Total rows (including header): " . count($rows));

    $header = array_shift($rows);
    if (!is_array($header)) {
        error_log("Error: Unexpected header format in $csvFilePath");
        return "<p>Predictions file is missing a readable header.</p>";
    }
    error_log("Header extracted: " . implode(", ", $header));

    // Filter rows for the selected team
    $filteredRows = array_filter($rows, function ($row) use ($team) {
        return $row[0] === $team;
    });

    error_log("Filtered rows for team '$team': " . count($filteredRows));

    if (empty($filteredRows)) {
        error_log("No predictions found for team: $team");
        return "<p>No predictions available for $team.</p>";
    }

    // Get team manager for full team name
    require_once 'TableGenerator.php';
    $teamManager = new TeamManager();
    $fullTeamName = $teamManager->getFullTeamName($team);

    // Build the injury report section
    $injuryHTML = $injuryReport->generateInjuryReport($fullTeamName);

    // Build the table
    $tableHTML = "<div class='table-container'>";
    $tableHTML .= "
    <div class='table-header'>
        <h2>Predictions for " . htmlspecialchars($team) . "</h2>
        <img src='Assets/Logos/{$team}.png' alt='{$team} Logo'/>
    </div>";
    
    // Add injury report before predictions table
    $tableHTML .= $injuryHTML;
    
    $tableHTML .= "<h3 style='margin-top: 30px;'>Game-by-Game Predictions</h3>";
    $tableHTML .= "<p class='info-text'>📊 HSS values shown below are <strong>injury-adjusted</strong></p>";
    $displayColumns = array_values(array_filter($header, static function ($col) {
        return $col !== 'Team';
    }));

    $tableHTML .= "<table>";
    $tableHTML .= "<thead><tr>";
    foreach ($displayColumns as $col) {
        $label = $col;
        if ($col === 'Projected Margin (pts)') {
            $label = 'Projected Margin';
        }
        if ($col === 'Confidence Gap %') {
            $label = 'Confidence Gap';
        }
        $tableHTML .= "<th>" . htmlspecialchars($label) . "</th>";
    }
    $tableHTML .= "</tr></thead><tbody>";

    $locationIndex = array_search('Location', $header, true);
    $winnerIndex = array_search('Predicted Winner', $header, true);

    foreach ($filteredRows as $row) {
        $rowAssoc = [];
        foreach ($header as $index => $colName) {
            $rowAssoc[$colName] = $row[$index] ?? '';
        }

        $tableHTML .= "<tr>";
        foreach ($displayColumns as $columnName) {
            $rawValue = $rowAssoc[$columnName] ?? '';

            switch ($columnName) {
                case 'Opponent':
                    $locationValue = ($locationIndex !== false && isset($row[$locationIndex])) ? trim((string)$row[$locationIndex]) : '';
                    $opponentShort = (string) $rawValue;
                    $opponentFull = $teamManager->getFullTeamName($opponentShort);
                    $prefix = 'vs. ';
                    if ($locationValue === 'A') {
                        $prefix = '@ ';
                    } elseif ($locationValue !== 'H') {
                        $prefix = '';
                    }
                    $display = $prefix . $opponentFull;
                    $tableHTML .= "<td class='opponent-cell'>" . htmlspecialchars($display) . "</td>";
                    break;

                case 'Location':
                    $mapping = ['H' => 'Home', 'A' => 'Away', 'N' => 'Neutral'];
                    $display = $mapping[$rawValue] ?? (is_string($rawValue) ? $rawValue : '');
                    $tableHTML .= "<td>" . htmlspecialchars($display) . "</td>";
                    break;

                case 'Team HSS (Adj)':
                case 'Opponent HSS (Adj)':
                    $tableHTML .= "<td class='hss-cell'>" . htmlspecialchars((string) $rawValue) . "</td>";
                    break;

                case 'Team Win %':
                case 'Opponent Win %':
                case 'Team ESPN Win %':
                case 'Opponent ESPN Win %':
                    if (is_numeric($rawValue)) {
                        $display = number_format((float) $rawValue, 2) . '%';
                    } else {
                        $display = strtoupper((string) $rawValue) === 'N/A' ? '—' : (string) $rawValue;
                    }
                    $colorClass = (strpos($columnName, 'Team') !== false) ? 'pct-team' : 'pct-opponent';
                    $tableHTML .= "<td class='pct-cell {$colorClass}'>" . htmlspecialchars($display) . "</td>";
                    break;

                case 'Predicted Winner':
                    $winnerFull = $teamManager->getFullTeamName((string) $rawValue);
                    $tableHTML .= "<td class='predicted-cell'>" . htmlspecialchars($winnerFull) . "</td>";
                    break;

                case 'Projected Margin (pts)':
                    $predictedWinner = $rowAssoc['Predicted Winner'] ?? '';
                    if (is_numeric($rawValue)) {
                        $margin = (float) $rawValue;
                        $signed = strcasecmp((string) $predictedWinner, $team) === 0 ? $margin : -$margin;
                        $marginClass = $signed > 0 ? 'margin-positive' : ($signed < 0 ? 'margin-negative' : 'margin-neutral');
                        $display = number_format($signed, 2) . ' pts';
                        $tableHTML .= "<td class='margin-cell {$marginClass}'>" . htmlspecialchars($display) . "</td>";
                    } else {
                        $tableHTML .= "<td class='margin-cell'>" . htmlspecialchars((string) $rawValue) . "</td>";
                    }
                    break;

                case 'Confidence Gap %':
                    if (is_numeric($rawValue)) {
                        $gap = (float) $rawValue;
                        if ($gap < 0) {
                            $gap = 0.0;
                        }
                        $bucket = 'Low';
                        if ($gap >= 20) {
                            $bucket = 'High';
                        } elseif ($gap >= 10) {
                            $bucket = 'Medium';
                        }
                        $display = number_format($gap, 1) . '%';
                        $display .= ' (' . $bucket . ')';
                        $tableHTML .= "<td class='confidence-cell'>" . htmlspecialchars($display) . "</td>";
                    } else {
                        $tableHTML .= "<td class='confidence-cell'>" . htmlspecialchars((string) $rawValue) . "</td>";
                    }
                    break;

                case 'Date':
                case 'Tipoff (ET)':
                    $tableHTML .= "<td>" . htmlspecialchars((string) $rawValue) . "</td>";
                    break;

                default:
                    $tableHTML .= "<td>" . htmlspecialchars((string) $rawValue) . "</td>";
                    break;
            }
        }
        $tableHTML .= "</tr>";
    }

    $tableHTML .= "</tbody></table></div>";
    error_log("Table for team '$team' successfully generated.");
    return $tableHTML;
}


echo fetchPredictionsForTeam($team, $dataFile);
