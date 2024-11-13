<?php
include_once "Content/HTMLhead.php";
include_once "Content/HTMLheader.php";


echo "<span>Hello. Welcome to the development version of the HoopSight AI websight!</span>";
?>

<?php

// Define team members' data
$teamMembers = [
	["Aditya Rao", "Assets/Baskimg_Ball.png", "Project Lead/Machine-Learning Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AR.png"],
	["Alexander Adams", "Assets/Advanced_Court.png", "Full-Stack Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AA.jpg"],
	["Bushra Naveed", "Assets/Baskimg_Ball.png", "Machine-Learning Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/BN.jpg"],
	["Alex Navarro", "Assets/Advanced_Court.png", "Machine-Learning Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AN.jpeg"],
	["Adarsh Mallya", "Assets/Baskimg_Ball.png", "Full-Stack Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AM.png"],
];

// Generate HTML for each team member
include_once "AboutUs.php";
foreach ($teamMembers as $index => $member) {
	echo createTeamMember($member[0], $member[1], $member[2], $member[3], $member[4], $index);
}
?>

<ul>
	<h3>TODO:</h3>
	<li>Website map</li>
	<li>Get a basic outline of what the inerface should look like</li>
	<li>Decide on a color scheme</li>
</ul>



<?php include_once "Content/HTMLfooter.php"; ?>