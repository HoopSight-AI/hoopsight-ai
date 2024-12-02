<?php
echo '<link rel="stylesheet" href="CSS/tableStyles.css">
	 <script src="JS/PredictionMuscle.js"></script>'; // Link the relevant stylesheet

/**
 * TeamManager Class
 * Manages team name mappings and provides utility methods.
 */
class TeamManager
{
	/**
	 * @var array Map of short team names to full team names.
	 */
	private $teamNameMap;

	/**
	 * Constructor initializes the team name map.
	 */
	public function __construct()
	{
		$this->teamNameMap = [
			"Golden State" => "Golden State Warriors",
			"LA Clippers" => "Los Angeles Clippers",
			"Milwaukee" => "Milwaukee Bucks",
			"Detroit" => "Detroit Pistons",
			"Charlotte" => "Charlotte Hornets",
			"Portland" => "Portland Trail Blazers",
			"Indiana" => "Indiana Pacers",
			"LA Lakers" => "Los Angeles Lakers",
			"Brooklyn" => "Brooklyn Nets",
			"Cleveland" => "Cleveland Cavaliers",
			"Washington" => "Washington Wizards",
			"Utah" => "Utah Jazz",
			"Atlanta" => "Atlanta Hawks",
			"Phoenix" => "Phoenix Suns",
			"New Orleans" => "New Orleans Pelicans",
			"Memphis" => "Memphis Grizzlies",
			"Denver" => "Denver Nuggets",
			"Okla City" => "Oklahoma City Thunder",
			"Dallas" => "Dallas Mavericks",
			"Boston" => "Boston Celtics",
			"New York" => "New York Knicks",
			"Sacramento" => "Sacramento Kings",
			"San Antonio" => "San Antonio Spurs",
			"Chicago" => "Chicago Bulls",
			"Minnesota" => "Minnesota Timberwolves",
			"Miami" => "Miami Heat",
			"Orlando" => "Orlando Magic",
			"Philadelphia" => "Philadelphia 76ers",
			"Toronto" => "Toronto Raptors",
			"Houston" => "Houston Rockets",
		];
	}

	/**
	 * Gets the full team name for a given short name.
	 *
	 * @param string $shortName The short team name.
	 * @return string The full team name, or the short name if not found.
	 */
	public function getFullTeamName(string $shortName): string
	{
		return $this->teamNameMap[$shortName] ?? $shortName;
	}

	/**
	 * Gets the team name map.
	 *
	 * @return array The team name map.
	 */
	public function getTeamNameMap(): array
	{
		return $this->teamNameMap;
	}
}

/**
 * PredictionTable Class
 * Generates HTML tables for predictions from CSV data.
 */
class PredictionTable
{
	/**
	 * @var TeamManager Instance of TeamManager.
	 */
	private $teamManager;

	/**
	 * Constructor initializes the PredictionTable.
	 *
	 * @param TeamManager $teamManager An instance of TeamManager.
	 */
	public function __construct(TeamManager $teamManager)
	{
		$this->teamManager = $teamManager;
	}

	/**
	 * Generates an HTML table from a CSV file.
	 *
	 * @param string $csvFilePath The path to the CSV file.
	 * @return string The generated HTML table.
	 */
	public function generateTable(string $csvFilePath): string
	{
		if (!file_exists($csvFilePath)) {
			return "<p>Error: CSV file not found.</p>";
		}

		// Load CSV file and parse it
		$rows = array_map('str_getcsv', file($csvFilePath));
		$header = array_shift($rows); // Extract header
		$header[3] = "HoopSight Score"; // Rename the last column

		// Sort rows by the last column (HoopSight Strength Score) in descending order
		usort($rows, function ($a, $b) {
			return $b[3] <=> $a[3]; // Descending sort
		});

		// Start table HTML
		$tableHTML = "<div class='table-container'>";
		$tableHTML .= "<h2>2024-25 NBA Season Predictions</h2>";
		$tableHTML .= "<table>";
		$tableHTML .= "<thead><tr>";
		foreach ($header as $col) {
			$tableHTML .= "<th>" . htmlspecialchars($col) . "</th>";
		}
		$tableHTML .= "</tr></thead><tbody>";

		// Add rows with full team names
		foreach ($rows as $row) {
			$tableHTML .= "<tr>";

			// Map the team name (first column)
			$teamShortName = $row[0];
			$teamFullName = $this->teamManager->getFullTeamName($teamShortName);
			$tableHTML .= "<td class='table-team-title'>
				<img src='Assets/Logos/{$teamShortName}.png' alt='{$teamFullName} Logo' />
				<div>" . htmlspecialchars($teamFullName) . "</div>
			</td>";
			// Add the rest of the columns
			for ($i = 1; $i < count($row); $i++) {
				if ($i == 3) $row[$i] = substr($row[$i], 0, -2); // Cut off the last two digits since its always 00
				$tableHTML .= "<td>" . htmlspecialchars($row[$i]) . "</td>";
			}

			$tableHTML .= "</tr>";
		}
		$tableHTML .= "</tbody></table></div>";

		return $tableHTML;
	}

	/**
	 * Generates HTML for the prediction dropdown and includes team data.
	 *
	 * @return string The generated HTML content.
	 */
	public function generatePredictionDropdown(): string
	{
		// Get the team data for JavaScript
		$teamData = [];
		foreach ($this->teamManager->getTeamNameMap() as $shortName => $fullName) {
			$teamData[] = ['shortName' => $shortName, 'fullName' => $fullName];
		}
		$teamDataJSON = json_encode($teamData);

		$html = <<<HTML
        <div class="dropdown-container">
            <h2>View Predictions for a Team</h2>
            <div class="slot-machine-container">
                <select id="team-dropdown">
                    <option value="" disabled selected>Select a Team</option>
                </select>
            </div>
            <button id="fetch-predictions">Show Predictions</button>
        </div>
    
        <div id="prediction-table"></div>
    
        <script>
            // Team data provided by PHP. TODO: This data does not transfer over to the javascript
            const teams = $teamDataJSON;
        </script>
    HTML;

		return $html;
	}
}
