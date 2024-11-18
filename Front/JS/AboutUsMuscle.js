// Initialize Parallax instances when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
	const parallaxInstances = [];
	const containers = document.querySelectorAll(".parallax-container");

	// Create a Parallax instance for each container
	containers.forEach((container, index) => {
		parallaxInstances.push(new Parallax(index, 0.3));
	});

	// Throttling variables for scroll event
	let ticking = false;

	// Scroll event listener with throttling
	document.addEventListener("scroll", () => {
		if (!ticking) {
			window.requestAnimationFrame(() => {
				const scrollPosition = window.scrollY;
				parallaxInstances.forEach(instance => instance.update(scrollPosition));
				ticking = false; // Allow further updates
			});
			ticking = true; // Prevent further updates until the next animation frame
		}
	});
});

class Parallax {
	/**
	 * Constructs a Parallax instance for a specific container index.
	 * @param {number} index - The index number corresponding to the parallax container.
	 * @param {number} speedFactor - The speed at which the background will move relative to scrolling
	 */
	constructor(index, speedFactor) {
		// Reference to the main container
		this.container = document.getElementById(`parallax-container-${index}`);
		if (!this.container) {
			console.error(`Container with ID 'parallax-container-${index}' not found.`);
			return;
		}

		// Reference to the background and overlay content elements
		this.background = document.getElementById(`parallax-background-${index}`);
		this.overlayContent = document.getElementById(`overlay-content-${index}`);
		this.speedFactor = speedFactor;
		this.hasFadedIn = false; // Track if overlayContent has been faded in - Apparently this is faster than a style query
	}

	/**
	 * Updates the parallax effect based on the current scroll position.
	 * Only updates when the container is within the viewport.
	 * @param {number} scrollPosition - The current vertical scroll position of the window.
	 */
	update(scrollPosition) {
		// Get the bounding rectangle of the container relative to the viewport
		const rect = this.container.getBoundingClientRect();

		// Adjust the background position for the parallax effect
		if (this.background) {
			const offset = -rect.top * this.speedFactor;
			this.background.style.transform = `translateY(${offset}px)`;
		}

		// Reset the overlay to a position opposite the scroll direction once the container is out of frame
		if (rect.top > window.innerHeight) {
			this.resetOverlay(false);
			return;
		} else if (rect.bottom < 0){ // Reset overlayContent if scrolled above the viewport
			this.resetOverlay(true);
			return;
		}

		// Fade in overlayContent if it is within view
		const halfwayInView = rect.bottom >= rect.height / 2 && rect.top <= window.innerHeight / 2;
		if (this.overlayContent && halfwayInView && !this.hasFadedIn) {
			this.overlayContent.style.opacity = '1';
			this.overlayContent.style.transform = 'translateY(0)';
			this.overlayContent.style.transition = '';
			this.hasFadedIn = true; // Mark as faded in
		}
	}

	/**
	 * Resets the overlay content to its initial state if outside the viewport.
	 * 
	 * @param {boolean} up - A boolean indicating if the content is above or below the viewport
	 */
	resetOverlay(up) {
		//console.log(this.overlayContent.id);
		if (this.overlayContent && this.hasFadedIn) {
			this.overlayContent.style.opacity = '';
			this.overlayContent.style.transform = (up) ? 'translateY(-100px)' :  '';
			this.overlayContent.style.transition = 'transform 0s ease, opacity 0s ease';
			this.hasFadedIn = false;
		}
	}
}