<?php
include_once "Content/HTMLhead.php";
include_once "Content/HTMLheader.php";

echo greetUser();
echo createVideoParallax($videoSrc = 'Assets/Lebone.mp4', $index = 1);

// Include the necessary classes
include_once "TableGenerator.php";


$teamManager = new TeamManager(); // Instantiate the TeamManager
$predictionTable = new PredictionTable($teamManager); // Instantiate the PredictionTable with the TeamManager
$dataFile = "CSVFiles/win_loss_records.csv"; // Define the data file path

echo $predictionTable->generateTable($dataFile); // Generate and display the main prediction table
echo "<div class='dashboard-cta'>"
    . "<p>Want game-by-game breakdowns and accuracy analytics?</p>"
    . "<a class='cta-button' href='PredictionsPage.php'>Open the Predictions Dashboard</a>"
    . "</div>";


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

function createVideoParallax($videoSrc, $index)
{
    return <<<HTML
<link rel="stylesheet" href="CSS/VideoStyle.css">
<div class='video-container' id='parallax-container-{$index}'>
    <video class='video-background' id='parallax-background-{$index}' autoplay muted loop>
        <source src='{$videoSrc}' type='video/mp4'>
        Your browser does not support the video tag.
    </video>
</div>
<div class='overlay-content' id='overlay-content-{$index}'>
        <h1>Have the foresight... use HoopSight!</h1>
    </div>

<div class='divider' id='divider-{$index}'></div>
HTML;
}
