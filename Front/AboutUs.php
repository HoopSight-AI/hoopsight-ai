<?php
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
                        <h1 id='member-name-{$index}'>{$name}</h1>
                        <h2 id='member-role-{$index}'>-- {$role}</h2>
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