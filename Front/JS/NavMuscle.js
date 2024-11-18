function handleNavBarAnimation() {
	console.log("Running");
	console.log("");
	let lastScrollTop = 0; // This will keep track of how far the user has scrolled to the top

	const navbar = document.querySelector("#nav-bar"); // Get reference to the main <nav> element

	const codedNavBarHeight = navbar.offsetHeight; // Get the height of the navbar

	navbar.style.top = 0;

	window.addEventListener("scroll", function () {
		// This line creates the event listener that will help track the user's scrolling
		const scrollTop = window.scrollY || document.documentElement.scrollTop; // Retrieves the amount of pixels that have been scrolled up.

		// Get the current position of the navbar relative to the viewport
		const navBarRect = navbar.getBoundingClientRect();
		const navBarTopPx = navBarRect.top;
		const navBarTop = parseFloat(navBarTopPx);

		const isHidden = navBarTop <= -codedNavBarHeight; //The script should reset the bar location if it goes to far!!!!!!!!!!!!!!!!1
		const partiallyVisible = navBarTop < 0 && navBarTop > -codedNavBarHeight;
		const isFullyVisible = navBarTop >= 0; //Come bakc to this later!!!!!!!!!!!!!!!!

		const isScrollUp = scrollTop < lastScrollTop;

		/* DEBUGGING INFO	
		console.log("Nav bar height = " + codedNavBarHeight);
		console.log("Nav top loc " + navBarTop);
		console.log("");
		console.log("Is hidden: " + isHidden);
		console.log("Partial: " + partiallyVisible);
		console.log("Is fully visible: " + isFullyVisible);
		console.log("Scrolling up: " + isScrollUp);
		console.log("Curr scroll loc: " + scrollTop);	
		console.log("Last scroll loc: " + lastScrollTop);	
		console.log("");
		console.log("");
		*/

		if (isHidden && isScrollUp) {
			// Can only move back down
			navbar.style.top = `${navBarTop + (lastScrollTop - scrollTop)}px`;
		} else if (partiallyVisible) {
			// Move in any direction
			navbar.style.top = `${navBarTop + (lastScrollTop - scrollTop)}px`;
		} else if (isFullyVisible && !isScrollUp) {
			// Can only move back up
			navbar.style.top = `${navBarTop + Math.min(0, lastScrollTop - scrollTop)}px`;
		}

		// Correct Navbar placement if it goes out of bounds
		if (navBarTop < -codedNavBarHeight - 5) {
			navbar.style.top = `${-codedNavBarHeight - 5}px`;
		} else if (navBarTop > 0) {
			navbar.style.top = "0px";
		}

		//Edge case where the user has scrolled to the top of the screen
		if (scrollTop == 0) navbar.style.top = 0;

		lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
	});
}

function adjustTopSpacing() {
	const navBarElement = document.getElementById("nav-bar");
	const navBarComputedStyle = window.getComputedStyle(navBarElement); // Leverage nav-bar reference to retrieve a reference to its CSS
	const navBarHeight = navBarComputedStyle.getPropertyValue("height"); // Retrieve 'height' styling data
	const spacingElement = document.getElementById("top-spacing"); // Get reference to the top-spacing element
	spacingElement.style.height = (parseFloat(navBarHeight) + 20) + "px"; // Set the margin-top of the top-spacing element to the height of the nav-bar. This line will style using px
}

// Add event listeners for DOMContentLoaded
document.addEventListener("DOMContentLoaded", function () {
	handleNavBarAnimation();
	adjustTopSpacing();
});
