document.addEventListener('DOMContentLoaded', function() {
	
	/* Listener for toggling 'on' the sign-up pop-up */
	attatchPopListener('sign-in', 'sign-up-background');

	/* Listener for toggling 'off' the sign-up pop-up */
	attatchPopListener('sign-up-background', 'sign-up-background');
});

/**
 * Attaches a click event listener to toggle display for the given element.
 *
 * @param {string} triggerId - The ID of the element that triggers the toggle action.
 * @param {string} targetId - The ID of the element whose display will be toggled.
 */
function attatchPopListener(triggerId, targetId) {
	const element = document.getElementById(triggerId);
	const formElement = document.querySelector('.pet-reg-container');
	if (element) {  // Ensure the element exists
		element.addEventListener('click', function() {
			togglePopDisplay(targetId);  // Toggle the display for the target element
		});
	}

	// Add click listener to the form to stop event propagation (prevent background click)
	if (formElement) {
		formElement.addEventListener('click', function(event) {
			event.stopPropagation(); // Note to self: Without this, the form will disappear even if the user clicks on what is overlayed on the background. This will stop the click from bubbling up to the background
		});
	}
}

/**
 * Toggles the display of an HTML element between 'none' and 'flex' (or another desired display type).
 * Additionally, toggles the container's width and height animations.
 *
 * @param {String} elementId - The element you want to toggle.
 */
function togglePopDisplay(elementId) {
	const element = document.getElementById(elementId); // Get the container inside the popup
	if (element) {
		const container = document.getElementById('pet-reg-container-' + elementId.slice(-1)); // Get the container inside the popup

		if (element.style.display === 'none' || element.style.display === '') {
			// Show the element and expand the container
			element.style.display = 'flex'; // You can change this to 'block', 'inline-block', or other as needed
			document.body.classList.add('no-scroll');  // Disable scrolling
		} else {
			// Collapse the container before hiding the element
			element.style.display = 'none';
			document.body.classList.remove('no-scroll');  // Enable scrolling
		}
	}
}