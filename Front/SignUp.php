<?php
require_once 'Content/HTMLhead.php';
require_once 'Content/HTMLheader.php';
?>

<body>
	<div class='sign-up-wrapper'>
		<h1 style='align-text: center;'>Create Account</h1>
		<div class='field-group-header'>Pet Parent Info</div>
		<form name='sign-up' method='post' action='sign-up/sign-up-processing.php' enctype="multipart/form-data">
			<div class='fields-container'>
				<div class='individual-text-field-wrapper'>
					<input class='text-field' type='text' name='f-name' placeholder='First name' required />
					<div class='input-placeholder'>First name</div>
				</div>
				<div class='individual-text-field-wrapper'>
					<input class='text-field' type='text' name='l-name' placeholder='Last name' required />
					<div class='input-placeholder'>Last name</div>
				</div>
			</div>
			<div class='individual-text-field-wrapper'>
				<input class='text-field' type='text' name='email' placeholder='Email' required />
				<div class='input-placeholder'>Email</div>
			</div>
			<div class='fields-container'>
				<div class='individual-text-field-wrapper'>
					<input class='text-field' type='text' name='password' placeholder='Password' required />
					<div class='input-placeholder'>Create password</div>
				</div>
				<div class='individual-text-field-wrapper'>
					<input class='text-field' type='text' name='password-confirmation' placeholder='Confirm pasword' required />
					<div class='input-placeholder'>Re-type password</div>
				</div>
			</div>

			<hr style='height: 5px; background-color: black; margin: 15px 0 0 0' />

			<div id='pet-fields-container' class='pet-fields-container'>
				<!-- Note to self. Elements that are specifically meant for text should be aligned using text-align CSS styling -->
				<div class='field-group-header'>Pet Information</div>
				<div class='fields-container'>
					<div class='individual-text-field-wrapper'>
						<input class='text-field' type='text' name='pet-name[]' placeholder='pet name' required />
						<div class='input-placeholder'>Pet name</div>
					</div>

					<div class='individual-text-field-wrapper'>
						<input class='image-field' type='file' name='pet-image[]' placeholder='Pet image' required />
					</div>
				</div>
			</div>
			<button type="button" id="add-pet-button" class='field-button'>Add pet +</button>
			<div><input class='submit-button' type='submit' name='sign-up' value='Sign up' /></div>
		</form>
	</div>


	<!-- Notes for people reviewing the page -->
	<ul style='font-size: 1.1em; font-weight: 400; margin: 20px; padding: 5px;'>
		<li><b><i>Notes:</i></b></li>
		<li><b>Box shadow:</b> Previous shadow was a plain dark shadow. I am trying out the light blue color.</li>
		<li><b>Field Name:</b> What should we call the field for the human data and then the pet? Since this is pet oriented product, maybe we should consider something along the lines of <b>Pet Parent</b></li>
	</ul>

	<?php require 'Content/HTMLfooter.php'; ?>
	<script src='JS/addDog.js'></script>
</body>