document.addEventListener('DOMContentLoaded', function() {
    // Listener to toggle 'on' the sign-up pop-up
    attachPopListener('sign-in', 'sign-up-background');

    // Listener to toggle 'off' the sign-up pop-up, with form propagation stopped
    attachPopListener('sign-up-background', 'sign-up-background', 'account-fields-container');

    const passwordField = document.getElementById('password-1');
    const confirmPasswordField = document.getElementById('password-2');
    new PasswordValidator(passwordField, confirmPasswordField, 'submit');  // Initialize the PasswordValidator
});

/**
 * Attaches a click event listener to toggle display for the given element.
 *
 * @param {string} triggerId - The ID of the element that triggers the toggle action.
 * @param {string} targetId - The ID of the element whose display will be toggled.
 * @param {string} [formElementId] - Optional. The ID of the element to stop event propagation on.
 */
function attachPopListener(triggerId, targetId, formElementId) {
    const triggerElement = document.getElementById(triggerId);
    const formElement = formElementId ? document.getElementById(formElementId) : null;

    if (triggerElement) {
        triggerElement.addEventListener('click', function() {
            togglePopDisplay(targetId);  // Toggle the display for the target element
        });
    }

    // Stop event propagation if formElementId is provided
    if (formElement) {
        formElement.addEventListener('click', function(event) {
            event.stopPropagation();  // Prevent background click from hiding the form
        });
    }
}

/**
 * Toggles the display of an HTML element between 'none' and 'flex'.
 * Controls the scrolling behavior on the body element when the pop-up is displayed.
 *
 * @param {string} elementId - The ID of the element to toggle.
 */
function togglePopDisplay(elementId) {
    const element = document.getElementById(elementId);
    
    if (element) {
        const containerId = 'pet-reg-container-' + elementId.slice(-1);
        const container = document.getElementById(containerId);

        if (element.style.display === 'none' || element.style.display === '') {
            element.style.display = 'flex';  // Show element
            document.body.classList.add('no-scroll');  // Disable scrolling
        } else {
            element.style.display = 'none';  // Hide element
            document.body.classList.remove('no-scroll');  // Enable scrolling
        }
    }
}

/**
 * Class to validate password confirmation by checking if the password fields match.
 * Manages styling and the enabling/disabling of the submit button.
 */
class PasswordValidator {
    /**
     * Creates a PasswordValidator instance.
     *
     * @param {HTMLElement} passwordField - The primary password input field.
     * @param {HTMLElement} confirmPasswordField - The confirmation password input field.
     * @param {string} submitButtonId - The ID of the submit button to be enabled/disabled.
     */
    constructor(passwordField, confirmPasswordField, submitButtonId) {
        this.passwordField = passwordField;
        this.confirmPasswordField = confirmPasswordField;
        this.submitButton = document.getElementById(submitButtonId);

        // Validate whenever the confirm password field changes
        this.confirmPasswordField.addEventListener('input', () => this.validate());
    }

    /**
     * Validates the password confirmation. Changes the styling and submit button state
     * based on the matching or mismatching state of the password fields.
     */
    validate() {
        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField.value;

        if (confirmPassword === '') {
            this.resetStyle();  // No confirmation input; reset to default style
            return;
        }

        if (confirmPassword.length !== password.length) {
            this.setStyle(confirmPassword.length > password.length ? 'red' : 'yellow');
            this.toggleSubmitButton(true);
            return;
        }

        if (confirmPassword === password) {
            this.setStyle('green');  // Passwords match
            this.toggleSubmitButton(false);
        } else {
            this.setStyle('red');  // Passwords do not match
            this.toggleSubmitButton(true);
        }
    }

    /**
     * Sets the box shadow color for the confirmation field based on the validation result.
     *
     * @param {string} color - The color indicator for the box shadow ('yellow', 'green', 'red').
     */
    setStyle(color) {
        const boxShadowColor = {
            yellow: '0 0 12px 3px yellow',
            green: '0 0 15px 2px green',
            red: '0 0 15px 2px red'
        };
        this.confirmPasswordField.style.boxShadow = boxShadowColor[color] || '';
    }

    /**
     * Resets the box shadow styling of the confirmation field to the default.
     */
    resetStyle() {
        this.confirmPasswordField.style.boxShadow = '';  // Remove inline style for default
    }

    /**
     * Toggles the enabled/disabled state of the submit button.
     *
     * @param {boolean} disable - True to disable the submit button, false to enable it.
     */
    toggleSubmitButton(disable) {
        if (this.submitButton) {
            this.submitButton.disabled = disable;
            this.submitButton.className = disable ? 'button-disabled' : 'submit-button';
        }
    }
}