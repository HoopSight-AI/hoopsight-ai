<?php
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

    // Read the CSV file
    $rows = array_map('str_getcsv', file($csvFilePath));
    error_log("CSV file loaded. Total rows (including header): " . count($rows));

    $header = array_shift($rows);
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

    // Build the table
    $tableHTML = "<div class='table-container'>";
    $tableHTML .= "<h2>Predictions for $team</h2>";
    $tableHTML .= "<table>";
    $tableHTML .= "<thead><tr>";
    foreach ($header as $col) {
        $tableHTML .= "<th>" . htmlspecialchars($col) . "</th>";
    }
    $tableHTML .= "</tr></thead><tbody>";

    foreach ($filteredRows as $row) {
        $tableHTML .= "<tr>";
        foreach ($row as $i => $cell) {
            if ($i === 4) { // Highlight Win Percentage
                $tableHTML .= "<td style='color: #00ff00; font-weight: bold;'>" . htmlspecialchars($cell) . "%</td>";
            } elseif ($i === 2 || $i === 3) { // HSS Home/Away
                $tableHTML .= "<td style='color: #0076b7;'>" . htmlspecialchars($cell) . "</td>";
            } else {
                $tableHTML .= "<td>" . htmlspecialchars($cell) . "</td>";
            }
        }
        $tableHTML .= "</tr>";
    }

    $tableHTML .= "</tbody></table></div>";
    error_log("Table for team '$team' successfully generated.");
    return $tableHTML;
}


echo fetchPredictionsForTeam($team, $dataFile);
