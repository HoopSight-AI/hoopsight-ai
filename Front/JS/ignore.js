function handleNavBarAnimation() {
	let lastScrollTop = 0; // This will keep track of how far the user has scrolled to the top

	const navbar = document.querySelector('#nav-bar'); // Get reference to the main <nav> element

	const currNavbarHeight = navbar.offsetHeight; // Get the height of the navbar

	window.addEventListener('scroll', function() { // This line creates the event listener that will help track the user's scrolling
		const scrollTop = window.pageYOffset || document.documentElement.scrollTop; // Retrieves the amount of pixels that have been scrolled up. 

		//If the user scrolls up, then nothing is changed because 0 is returned. If the user scrolls down, a positive value is returned, resulting in change in the nav bar
		const newTop = Math.min(0, -scrollTop + currNavbarHeight); //My ultra high IQ Math.min() function avoids having to use an if statement to perform this
		navbar.style.top = newTop + "px"; // Make changes to the 'top' CSS style of the navbar 
	});
}

function adjustTopSpacing() {
	const navBarElement = document.getElementById('nav-bar');
	const navBarComputedStyle = window.getComputedStyle(navBarElement); // Leverage nav-bar reference to retrieve a reference to its CSS
	const navBarHeight = navBarComputedStyle.getPropertyValue('height'); // Retrieve 'height' styling data

	const spacingElement = document.getElementById('top-spacing'); // Get reference to the top-spacing element
	spacingElement.style.marginTop = navBarHeight; // Set the margin-top of the top-spacing element to the height of the nav-bar
}

// Add event listeners for DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
	handleNavBarAnimation();
	adjustTopSpacing();
});
