/**
 * MessageHandler Class
 * 
 * The MessageHandler class is responsible for managing the display 
 * of alert messages within the user interface. It provides methods 
 * to show success and error messages, handle the closing of alerts, 
 * and manage animations for alert visibility.
 * 
 * Key Responsibilities:
 * - Display alert messages with appropriate styling based on success or error status.
 * - Handle the closing of alert messages and trigger animations.
 * - Provide feedback to users through visual cues.
 * 
 * This class enhances user experience by ensuring that important 
 * messages are communicated effectively and can be dismissed easily.
 */
export class MessageHandler {
	/**
     * Constructor for the MessageHandler class.
     * 
     * @param {HTMLElement} alertElement - The element that contains the alert message.
     * @param {HTMLElement} messageElement - The element where the message text will be displayed.
     */
    constructor(alertElement, messageElement) {
        this.alertElement = alertElement;
        this.messageElement = messageElement;
        this.closeBtn = this.alertElement.querySelector('.btn-close');
		this.setupEventListeners();
    }

	/**
     * Sets up event listeners for the close button and animation events.
     */
    setupEventListeners() {
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', (e) => this.handleCloseMessage(e));
        }
        if (this.alertElement) {
            this.alertElement.addEventListener('animationend', (e) => this.handleAnimationEnd(e));
        }
    }

	/**
     * Displays a message in the alert element with appropriate styling.
     * 
     * @param {string} message - The message to display.
     * @param {boolean} [isError=true] - Indicates whether the message is an error (true) or success (false).
     */
    showMessage(message, isError = true) {
        if (this.messageElement && this.alertElement) {
            this.messageElement.textContent = message;
            this.alertElement.classList.remove('alert-success', 'alert-danger');
            this.alertElement.classList.add(isError ? 'alert-danger' : 'alert-success');
            this.alertElement.classList.add('show');
            this.alertElement.classList.remove('d-none');
        }
    }

	/**
     * Displays an error message in the alert element.
     * 
     * @param {string} message - The error message to display.
     */
    showError(message) {
        this.showMessage(message, true);
    }

	/**
     * Displays a success message in the alert element.
     * 
     * @param {string} message - The success message to display.
     */
    showSuccess(message) {
        this.showMessage(message, false);
    }

	/**
     * Handles the closing of the alert message when the close button is clicked.
     * 
     * @param {Event} e - The click event triggered by the close button.
     */
    handleCloseMessage(e) {
        e.preventDefault();
        this.shakeAlert();
    }
    
	/**
     * Triggers a shake animation on the alert element.
     */
    shakeAlert() {
        if (this.alertElement) {
            this.alertElement.classList.add('shake');
            setTimeout(() => {
                this.alertElement.classList.remove('shake');
            }, 820);
        }
    }

	/**
     * Handles the end of CSS animations on the alert element.
     * 
     * @param {AnimationEvent} e - The animationend event triggered.
     */
    handleAnimationEnd(e) {
        if (e.animationName === 'shake' && this.alertElement) {
            this.alertElement.classList.remove('show');
            this.alertElement.classList.add('d-none');
        }
    }
}