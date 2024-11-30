<?php
//HTMLheader.php
?>
<div id="nav-bar" class='nav-container'>
	<nav class="nav">
		<a class="home-link" href='index.php'>
			<img class="nav-logo" src='Assets/ball-icon.png' alt='HoopSight AI logo' />
		</a>

		<ul class="nav-text">
			<li><a href='AboutUs.php'>About Us</a></li>
		</ul>

		<a id='sign-in' class="account-button">
			<img class="profile-picture" src='Assets/Empty-Profile.png' alt='Log-in image' />
			<span>Log-In</span>
		</a>
	</nav>
</div>

<!-- The styling for the header is currently dynamically set to whatever the height of the nav-bar is styled as. This will ensure that the rest of the page will show -->
<div id='top-spacing'></div>
<script src="JS/NavMuscle.js"></script>

<?php include_once "Sign_Up2.php"; ?>