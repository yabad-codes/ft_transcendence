import Router from "../utils/router.js";
import BaseHTMLElement from './BaseHTMLElement.js';
import { MessageHandler }  from './MessageHandler.js';
import { api } from '../utils/api_service.js';
/**
 * TwoFactorAuthPage Class
 * 
 * The TwoFactorAuthPage class is a custom web component that facilitates 
 * the two-factor authentication (2FA) process for users. It captures user 
 * input for a 6-digit verification code, validates this input, and 
 * provides feedback through success or error messages.
 * 
 * Key Responsibilities:
 * - Capture user input for a 6-digit verification code.
 * - Validate the verification code against the server.
 * - Display success or error messages based on the validation result.
 * 
 * This component enhances security by adding an additional layer of 
 * verification, ensuring that only authorized users can access their 
 * accounts.
 */
export class TwoFactorAuthPage extends BaseHTMLElement {
    constructor() {
		super('_2fapage');

        this.inputRefs = [];
        this.submitButton = null;
		this.messageHandler = null;
		this.alertElement = null;
        this.messageElement = null;

		this.isBackupMode = false;
		this.codeInputGroup = null;
		this.instructions = null;
		this.backupCodeInput = null;
    }

	/**
     * Lifecycle method called when the element is added to the DOM.
     * Initializes UI elements and sets up event listeners.
     */
	connectedCallback() {
		super.connectedCallback();

        this.initializeElements();
        this.setupEventListeners();
    }

	/**
     * Initializes the input fields, submit button, alert element, 
     * and message element for the 2FA process.
     */
    initializeElements() {
        this.inputRefs = Array.from(document.querySelectorAll('input[aria-label="2fa"]'));
        this.submitButton = document.getElementById('submitBtn');
		this.alertElement = document.getElementById('messageAlert');
		this.messageElement = document.getElementById('messageText');
		this.messageHandler = new MessageHandler(this.alertElement, this.messageElement);

		this.toggleBackup = document.getElementById('toggleBackup');
		this.codeInputGroup = document.getElementById('codeInputGroup');
		this.instructions = document.getElementById('instructions');
		this.backupCodeInput = document.getElementById('backupCodeInput');
    }

	/**
     * Sets up event listeners for user interactions with the input fields 
     * and the submit button.
     */
    setupEventListeners() {
        this.inputRefs[0].focus();

        this.inputRefs.forEach((input, index) => {
            input.addEventListener('input', (event) => this.handleInput(event, index));
            input.addEventListener('keydown', (event) => this.handleKeyDown(event, index));
        });

        this.submitButton.addEventListener('click', () => this.submitCode());

		this.toggleBackup.addEventListener('click', (e) => {
			e.preventDefault();
			this.isBackupMode = !this.isBackupMode;
			if (this.isBackupMode) {
				this.codeInputGroup.classList.add('d-none');
				this.backupCodeInput.classList.remove('d-none');
				this.instructions.textContent = 'Enter your 10-character backup code.';
				toggleBackup.textContent = 'Use authenticator app instead';
			} else {
				this.codeInputGroup.classList.remove('d-none');
				this.backupCodeInput.classList.add('d-none');
				this.instructions.textContent = 'Enter 6-digit code from your authenticator app.';
				toggleBackup.textContent = "Don't have access to your authenticator app?";
			}
		});
    }

	/**
     * Handles input events for the verification code fields.
     * Moves focus to the next input field when a digit is entered.
     * 
     * @param {Event} event - The input event triggered by the user.
     * @param {number} index - The index of the current input field.
     */
    handleInput(event, index) {
        const input = event.target;
        input.value = input.value.replace(/[^0-9]/g, '');

        if (input.value.length === 1 && index < this.inputRefs.length - 1) {
            this.inputRefs[index + 1].focus();
        }

        this.checkCodeCompletion();
    }

	/**
     * Handles keydown events for the verification code fields.
     * Allows navigation back to the previous input field when 
     * the Backspace key is pressed.
     * 
     * @param {Event} event - The keydown event triggered by the user.
     * @param {number} index - The index of the current input field.
     */
    handleKeyDown(event, index) {
        if (event.key === 'Backspace' && event.target.value === '' && index > 0) {
            this.inputRefs[index - 1].focus();
        }
    }

	/**
     * Checks if the verification code is complete (6 digits) 
     * and submits it if it is.
     */
    checkCodeCompletion() {
        const code = this.getCode();
        if (code.length === 6) {
            this.submitCode();
        }
    }

	/**
     * Retrieves the complete verification code from the input fields.
     * 
     * @returns {string} - The concatenated verification code.
     */
    getCode() {
		return this.isBackupMode ? 
				this.backupCodeInput.value : 
				this.inputRefs.map(input => input.value).join('');
    }

	/**
     * Submits the verification code for validation.
     * If successful, redirects the user; otherwise, displays an error message.
     */
    async submitCode() {
        const code = this.getCode();
        if (!this.isBackupMode && code.length !== 6) {
			this.messageHandler.showError('Please enter the 6-digit code');
            return;
        }

        const success = await this.verifyCode(code);
        if (success) {
            this.messageHandler.showSuccess('Two-factor authentication successful. Redirecting...');
            setTimeout(() => Router.go('/'), 2000);
        } else {
			this.messageHandler.showError('Two-factor authentication failed.');
		}
    }

	/**
     * Validates the verification code with the server.
     * 
     * @param {string} code - The verification code to validate.
     * @returns {Promise<boolean>} - Returns true if validation is successful; otherwise, false.
     */
	async verifyCode(code) {
		let response = null;
        try {
			if (this.isBackupMode)
				response = await api.verifyBackupCode(code);
			else
            	response = await api.verifyTwoFactor(code);
            if (response.success)
                return true;
			return false;
        } catch (error) {
            this.messageHandler.showError('Two-factor authentication failed.');
            return false;
        }
    }

}

customElements.define('twofa-page', TwoFactorAuthPage);
