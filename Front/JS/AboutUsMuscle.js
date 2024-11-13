// Initialize Parallax instances when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
	const parallaxInstances = [];
	const containers = document.querySelectorAll(".parallax-container");

	// Create a Parallax instance for each container
	containers.forEach((container, index) => {
		parallaxInstances.push(new Parallax(index));
	});

	// Throttling variables for scroll event
	let ticking = false;

	// Scroll event listener with throttling
	document.addEventListener("scroll", () => {
		if (!ticking) {
			window.requestAnimationFrame(() => {
				const scrollPosition = window.scrollY;
				parallaxInstances.forEach((instance) => {
					instance.update(scrollPosition);
				});
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
	 */
	constructor(index) {
		// Reference to the main container
		this.container = document.getElementById(`parallax-container-${index}`);
		if (!this.container) {
			console.error(
				`Container with ID 'parallax-container-${index}' not found.`
			);
			return;
		}

		// Reference to the background and overlay content elements
		this.background = document.getElementById(`parallax-background-${index}`);
		this.overlayContent = document.getElementById(`overlay-content-${index}`);

		this.speedFactor = 0.5;
	}

	/**
	 * Updates the parallax effect based on the current scroll position.
	 * Only updates when the container is within the viewport.
	 * @param {number} scrollPosition - The current vertical scroll position of the window.
	 */
	update(scrollPosition) {
		// Get the bounding rectangle of the container relative to the viewport
		// NOTE TO SELF: getBoundingClientRect() retrieves information about a component's position relative to the viewport
		const rect = this.container.getBoundingClientRect();
		const opacityValue = window.getComputedStyle(this.overlayContent).opacity;


		// Check if the container is in the viewport
		if (rect.bottom >= 0 && rect.top <= window.innerHeight) {
			// The container is at least partially in the viewport

			// Adjust the background position for parallax effect
			if (this.background) {
				// Calculate the offset based on the container's position
				const offset = -rect.top * this.speedFactor;
				this.background.style.transform = `translateY(${offset}px)`;

				// The condition on the right 
				if (this.overlayContent && opacityValue == '0' && (rect.bottom >= rect.height/2 && rect.top <= window.innerHeight/2)) {
					this.overlayContent.style.opacity = '1';
					this.overlayContent.style.transform = 'translateY(0)';
					this.overlayContent.style.transition = '';

				}
			}
		} else {
			if(rect.top < 0){ //
				this.overlayContent.style.opacity = '';
				this.overlayContent.style.transform = 'translateY(-50px)';
				this.overlayContent.style.transition = 'transform 0s ease, opacity 0s ease';
			} else {
				this.overlayContent.style.opacity = '';
				this.overlayContent.style.transform = '';
				this.overlayContent.style.transition = 'transform 0s ease, opacity 0s ease';
			}
		}

		
	}
}