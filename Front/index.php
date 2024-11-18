<?php
include_once "Content/HTMLhead.php";
include_once "Content/HTMLheader.php";

echo greetUser();


include_once "Content/HTMLfooter.php";


/**
 * Generates a greeting HTML snippet for the user.
 *
 * @param Customer $customerData The customer's data.
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
