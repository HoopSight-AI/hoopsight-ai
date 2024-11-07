document.addEventListener('DOMContentLoaded', function() {
	let index = 1;

	// Loop through forms while either form1 or form2 exist
	while (document.getElementById('kit-assign-' + index) || document.getElementById('submit-' + index)) {

		// Attach event listener to 'kit-assign' form
		attachSubmissionListener('kit-assign', index, ajaxCall);

		// Attach event listener to 'pet-registration' form (TODO: Implement on pop-up version)
		attachSubmissionListener('pet-registration', index, ajaxCall);

		/* Handle the registration button for toggling display */

		// Attach listener to activate the popup
		attatchPopListener('call-pet-form-' + index, 'pet-reg-background-' + index);

		// Attach listener to deactivate the popup (toggle close)
		attatchPopListener('pet-reg-background-' + index, 'pet-reg-background-' + index);

		index++;
	}
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
 * Attaches a submission event listener to a form element and triggers the associated AJAX call.
 * This function is designed to handle the form submission events by passing both the event and the
 * form element to the AJAX function for processing. Ensures proper handling of form scope and event binding.
 *
 * @param {string} formId - The ID of the form to attach the event listener to. Must be unique for each form.
 * @param {number} index - The index used to dynamically construct the form's ID.
 * @param {function} ajaxFunction - The function that handles the form submission via AJAX. It requires two parameters: the event and the form element.
 */
function attachSubmissionListener(formId, index, ajaxFunction) {
	const form = document.getElementById(formId + '-' + index); // Retrieve the form element by ID
	if (form) {
		form.addEventListener('submit', function(event) { // Attach the submit event listener
			// Pass both the event and the form reference to the AJAX call
			ajaxFunction(event, form);
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

// Usage of the function for form1 (kit assignment) and form2 (pet registration)

document.addEventListener('input', function(event) {
	handleEvent(event);  /* Call your handler function directly */
});

document.querySelectorAll('.form-pet-image').forEach(imageInputElement => { /* Select all elements with the class 'form-pet-image' (presumably file input elements for pet images) */
	imageInputElement.addEventListener('change', function(event) { /* Add an event listener for the 'change' event, which fires when the user selects a file */
		const selectedFile = event.target.files[0]; /* Get the first file from the input element (only one file should be selected) */
		const inputElementId = event.target.id; /* Extract the ID of the input element that triggered the event */
		const labelElementId = `pet-image-background-${inputElementId.slice(-1)}`; /* Generate the ID of the corresponding label element by extracting the last character (index number) from the input element's ID */

		if (selectedFile) { /* Check if a file has been selected */
			const fileReader = new FileReader(); /* Create a new FileReader object to read the content of the selected file */
			fileReader.onload = function(loadEvent) { /* Define the onload event handler for the FileReader */
				const labelElement = document.getElementById(labelElementId); /* Get the label element corresponding to the generated ID */
				labelElement.style.backgroundImage = `url(${loadEvent.target.result})`; /* Set the background image of the label to the result of the FileReader (the file's data URL) */
				labelElement.style.display = 'block'; /* Ensure the label is visible */
				labelElement.style.boxShadow = '0 0 15px 2px green';
			};

			fileReader.readAsDataURL(selectedFile); /* Start reading the file as a data URL, which can be used as the background image */
		} 
	});
});

function handleEvent(event) {
	const target = event.target;

	/* Your logic for handling the event */
	if (target.id.startsWith('measurement-type')) {
		const cellId = target.id.slice(-1);  /* Update this logic based on your requirements */
		handleMeasurementTypeChange(target.value, cellId);
	}

	/*
		if (target.id.startsWith('pet-age-') || target.id.startsWith('pet-weight-')) {
		const regex = /^\d{1,3}(\.\d{1,10})?$/;  // Regex: 0-999 with up to 10 decimal places
		validateField(target, regex);
		}
		*/
}

function validateField(target, regex) {
	if (target.value === '') {
		target.style.boxShadow = '0 0 12px 3px black';
	} else {
		validateInput(target, regex);
	}
}

function validateInput(element, regex) {
	const value = element.value;

	if (regex.test(value)) {
		toggleSubmission(element, false);
		element.style.boxShadow = '0 0 15px 2px green';
	} else {
		toggleSubmission(element, true);
		element.style.boxShadow = '0 0 15px 2px red';
	}
}

/**
 * Toggles the enabled/disabled state of a submission button associated with the provided element.
 * The function targets the submit button based on a unique identifier extracted from the element's ID.
 * 
 * @param {HTMLElement} element - The HTML element whose ID is used to identify the target submit button.
 * The ID of this element should end with a unique identifier (e.g., '-1', '-2') 
 * that corresponds to the associated submit button.
 * @param {boolean} disable - A boolean value that determines whether the submit button should be disabled or enabled.
 * - `true`: Disables the submit button and applies the 'add-pet-button-disabled' class.
 *
 * - `false`: Enables the submit button and applies the 'add-pet-button' class (or the class 
 *specified for the enabled state).
 * 
 * @returns {void} - This function does not return a value. It directly modifies the DOM to enable or disable the button.
 */
function toggleSubmission(element, disable) {
	const cellId = element.id.slice(-1); // Extract cellId
	const submit = document.getElementById(`submit-${cellId}`);

	if (disable) {
		submit.disabled = true;
		submit.className = 'add-pet-button-disabled';
	} else {
		submit.disabled = false;
		submit.className = 'add-pet-button'; // Replace with the original class
	}
}


function ajaxCall(event, form) {
	event.preventDefault(); // Prevent the default form submission

	const formData = new FormData(form); // Create a FormData object from the form

	// Send an AJAX request using the Fetch API
	fetch('formCatch.php', {
		method: 'POST',
		body: formData
	})
	.then(response => response.text())
		.then(data => {
			console.log(data); // Optional: handle response data
			window.location.reload(); // Refresh the page
		})
	.catch(error => {
		console.error('Error:', error);
	});
}
