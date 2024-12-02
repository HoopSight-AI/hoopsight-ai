<?php

include_once "Content/HTMLhead.php";
include_once "Content/HTMLheader.php";

$teamMembers = [
    ["Aditya Rao", "Assets/Baskimg_Ball.png", "Project Lead", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AR.png"],
    ["Alexander Adams", "Assets/Advanced_Court.png", "Full-Stack Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AA.jpg"],
    ["Bushra Naveed", "Assets/Baskimg_Ball.png", "Machine-Learning Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/BN.jpg"],
    ["Alex Navarro", "Assets/Advanced_Court.png", "Machine-Learning Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AN.jpeg"],
    ["Adarsh Mallya", "Assets/Baskimg_Ball.png", "Full-Stack Engineer", "As an aspiring leader and computer scientist, I have a passion for innovation which I fuel through my programming skills and dreams.", "Assets/TeamMembers/AM.jpg"],
];

foreach ($teamMembers as $index => $member) {
    // Render the HTML
    echo createTeamMember($member[0], $member[1], $member[2], $member[3], $member[4], $index);
}

include_once "Content/HTMLfooter.php"; ?>


<?php
// Helper functions 

function createTeamMember($name, $src, $role, $description, $imagePath, $index)
{
    return "
<div class='parallax-container' id='parallax-container-{$index}'>
    <img class='parallax-background' src='{$src}' id='parallax-background-{$index}'></img>
    <div class='overlay-content' id='overlay-content-{$index}'>
        <div class='member' id='member-{$index}'>
            <img src='{$imagePath}' alt='Member Photo' id='member-image-{$index}'>
            <div class='member-text' id='member-text-{$index}'>
                <div class='title' id='title-{$index}'>
                    <h1 id='member-name-{$index}'>{$name} </h1>
                    <h4>-</h4>
                    <h2 id='member-role-{$index}'>{$role}</h2>
                </div>
                <span id='member-description-{$index}'>{$description}</span>
            </div>
        </div>
    </div>
</div>
<div class='divider' id='divider-{$index}'></div>
";
}
?>

<link rel="stylesheet" href="CSS/AboutUsStyle.css">
<script src="JS/AboutUsMuscle.js"></script>