<?php
include_once "Content/HTMLhead.php";
include_once "Content/HTMLheader.php";

echo greetUser();

// Include the necessary classes
include_once "TableGenerator.php";


$teamManager = new TeamManager(); // Instantiate the TeamManager
$predictionTable = new PredictionTable($teamManager); // Instantiate the PredictionTable with the TeamManager
$dataFile = "CSVFiles/win_loss_records.csv"; // Define the data file path

echo $predictionTable->generateTable($dataFile); // Generate and display the main prediction table
echo $predictionTable->generatePredictionDropdown(); // Generate and display the prediction dropdown


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
