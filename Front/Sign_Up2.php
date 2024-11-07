<?php require_once 'Content/HTMLhead.php'; ?>
<div class='sign-up-wrapper'>
	<div class='account-fields-container'>
		<h1>Create Account</h1>
		<div class='field-group-header'>User Info</div>
		<form name='sign-up' method='post' action='sign-up/sign-up-processing.php' enctype="multipart/form-data">
			<div class='fields-container'>
				<div class='individual-text-field-wrapper horizontal-fields'>
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
			<div class='individual-text-field-wrapper'>
				<input class='text-field' type='text' name='password' placeholder='Password' required />
				<div class='input-placeholder'>Create password</div>
			</div>
			<div class='individual-text-field-wrapper'>
				<input class='text-field' type='text' name='password-confirmation' placeholder='Confirm pasword' required />
				<div class='input-placeholder'>Re-type password</div>
			</div>
			<div><input class='submit-button' type='submit' name='sign-up' value='Sign up' /></div>
	</div>
	</form>
</div>

<script src='JS/addDogV2.js'></script>