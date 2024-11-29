<?php
include_once "Content/HTMLhead.php";
include_once "Content/HTMLheader.php";

echo greetUser();

// Display the table
$dataFile = "./win_loss_records.csv";
echo generateTable($dataFile);

echo generatePredictionDropdown();


include_once "Content/HTMLfooter.php";


/**
 * Generates a greeting HTML snippet for the user.
 *
 * @return string The generated HTML content.
 */
function greetUser(): string
{
	return <<<HTML
	<div class='welcome-message-container'>
		<h1>Welcome to the HoopSight AI prototype website</h1>
	</div>
HTML;
}

/**
 * Reads a CSV file and generates an HTML table.
 *
 * @param string $csvFilePath The path to the CSV file.
 * @return string The generated HTML table.
 */
function generateTableFromCSV(string $csvFilePath): string
{
	if (!file_exists($csvFilePath)) {
		return "<p>Error: CSV file not found.</p>";
	}

	$tableHTML = "<div class='table-container'><h2>2024-25 NBA Season Predictions</h2><table border='1'>";
	$tableHTML .= "<thead><tr><th>Team</th><th>Wins</th><th>Losses</th><th>HSS</th></tr></thead><tbody>";

	// Read the CSV file and generate table rows
	if (($handle = fopen($csvFilePath, "r")) !== false) {
		$isHeader = true;
		while (($data = fgetcsv($handle, 1000, ",")) !== false) {
			// Skip the header row for table body
			if ($isHeader) {
				$isHeader = false;
				continue;
			}
			$tableHTML .= "<tr>";
			foreach ($data as $cell) {
				$tableHTML .= "<td>" . htmlspecialchars($cell) . "</td>";
			}
			$tableHTML .= "</tr>";
		}
		fclose($handle);
	}

	$tableHTML .= "</tbody></table></div>";
	return $tableHTML;
}

function generateTable($dataFile): string {
    // Map of short team names to full team names
	$teamNameMap = [
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

    // Load CSV file and parse it
    $rows = array_map('str_getcsv', file($dataFile));
    $header = array_shift($rows); // Extract header
    $header[3] = "HoopSight Strength Score"; // Rename the last column

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
        $teamFullName = $teamNameMap[$teamShortName] ?? $teamShortName; // Default to short name if no mapping exists
        $tableHTML .= "<td>" . htmlspecialchars($teamFullName) . "</td>";

        // Add the rest of the columns
        for ($i = 1; $i < count($row); $i++) {
            $tableHTML .= "<td>" . htmlspecialchars($row[$i]) . "</td>";
        }

        $tableHTML .= "</tr>";
    }
    $tableHTML .= "</tbody></table></div>";

    return $tableHTML;
}


//add dropdown selection to show other predictions
function generatePredictionDropdown(): string {
    // Map for team names
	$teamNameMap = [
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

    // Generate JavaScript team list for slot machine effect
    $teamsJSArray = json_encode(array_keys($teamNameMap));

    $html = <<<HTML
	<div class="dropdown-container">
		<h2>View Predictions for a Team</h2>
		<div class="slot-machine-container">
			<select id="team-dropdown">
				<option value="" disabled selected>Loading...</option>
			</select>
		</div>
		<button id="fetch-predictions">Show Predictions</button>
	</div>

	<div id="prediction-table"></div>

    <script>
        const teams = $teamsJSArray; // List of team names
        const dropdown = document.getElementById('team-dropdown');
        let cyclingInterval;

        // Populate dropdown with cycling team names
        function populateDropdown() {
            dropdown.innerHTML = '';
            for (let team of teams) {
                let option = document.createElement('option');
                option.value = team;
                option.textContent = team;
                dropdown.appendChild(option);
            }
        }

        // Cycle team names in the dropdown every 2 seconds
        function startCycling() {
            cyclingInterval = setInterval(() => {
                teams.push(teams.shift()); // Rotate team names
                populateDropdown();
            }, 2500);
        }

        // Handle button click to fetch predictions
        document.getElementById('fetch-predictions').addEventListener('click', () => {
            const selectedTeam = dropdown.value;
            if (!selectedTeam) {
                alert('Please select a team!');
                return;
            }

		   // Fetch predictions for the selected team
		   fetch('FetchPredictions.php?team=' + encodeURIComponent(selectedTeam))
			   .then(response => response.text())
			   .then(data => {
				   document.getElementById('prediction-table').innerHTML = data;
			   })
			   .catch(err => console.error('Error fetching predictions:', err));
	   });

        // Stop cycling when dropdown is clicked
        dropdown.addEventListener('click', () => {
            clearInterval(cyclingInterval);
        });

	   // Initial populate
	   populateDropdown();
	   startCycling();
   </script>
HTML;

   return $html;
}