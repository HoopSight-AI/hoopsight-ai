function toggleVisibility(button) {
	// Get the parent element of the button
	let petName = button.id;
	let petContainer = document.getElementById(petName + '-container');


	// Get the content wrapper element within the pet container
	let contentWrapper = petContainer.querySelector('.' + petName + '-tests-container');

	// Check if contentWrapper exists
	if (!contentWrapper) {
		console.error("No element with class 'pet-content-container' found inside the pet container.");
		return;
	}

	// Check the current display style and toggle it
	if (button.innerText.includes('View')) {
		// Calculate and set the new height and width of the pet container
		let contentHeight = contentWrapper.scrollHeight;
		let contentWidth = contentWrapper.scrollWidth;
		petContainer.style.height = (button.offsetHeight + contentHeight) + 'px';
		petContainer.style.width = '80%';

		button.innerText = 'Hide tests for:\n' + button.id;
	} else {
		// Reset the height of the pet container to fit only the button
		button.style.width = 'fit-content';
		petContainer.style.height = (button.offsetHeight * 1.4) + 'px';
		petContainer.style.width = (button.offsetWidth * 1.2) + 'px';

		button.innerText = 'View tests for:\n' + button.id;
	}
}
