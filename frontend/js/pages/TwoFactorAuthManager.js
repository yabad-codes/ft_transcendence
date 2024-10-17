import { api } from '../utils/api_service.js';
import { MessageHandler } from './MessageHandler.js';
/**
 * TwoFactorAuthManager Class
 * 
 * The TwoFactorAuthManager class is responsible for managing the 
 * two-factor authentication (2FA) process within the application. 
 * It provides an interface for users to enable or disable 2FA, 
 * input authentication codes, and manage QR codes for setup.
 * 
 * Key Responsibilities:
 * - Initializes the UI elements related to 2FA.
 * - Handles user input for the 6-digit authentication code.
 * - Provides feedback to users through the MessageHandler class.
 * - Manages the enabling and disabling of 2FA, including fetching 
 *   QR codes and backup codes.
 */
export class TwoFactorAuthManager {
	/** 
	 * Constructor:
	 * @param {boolean} initialStatus - Indicates the initial status of 2FA (enabled or disabled).
	 */
    constructor(initialStatus) {
		// Initializes UI elements and event listeners
        this.setup2faSection = document.getElementById('setup2fa');
        this.enable2faToggle = document.getElementById('enable2fa');
        this.authCodeInput = document.getElementById('authCode');
        this.stepTitle = document.getElementById('stepTitle');
        this.guide = document.getElementById('guide');
        this.saveChangesBtn = document.getElementById('saveChanges');

		this.alertElement = document.getElementById('messageAlert');
		this.messageElement = document.getElementById('messageText');
		this.messageHandler = new MessageHandler(this.alertElement, this.messageElement);

        this.twoFactorEnabled = initialStatus;
        this.tfa = initialStatus;
        this.updateUIBasedOnStatus(this.twoFactorEnabled);
        this.setupEventListeners();
    }

	/**
     * Sets up event listeners for user interactions.
     * Listens for input changes in the authentication code field 
     * and enables the save button when a valid code is entered.
     */
    setupEventListeners() {
        this.authCodeInput.addEventListener('input', (event) => {
            event.target.value = event.target.value.replace(/[^0-9]/g, '');
            if (this.authCodeInput.value.length === 6) {
                this.saveChangesBtn.disabled = false;
            }
        });
    }

	/**
     * Updates the UI based on the current status of 2FA.
     * 
     * @param {boolean} enabled - Indicates whether 2FA is enabled or disabled.
     */
    updateUIBasedOnStatus(enabled) {
        this.enable2faToggle.checked = enabled;
        this.setup2faSection.style.display = enabled ? 'block' : 'none';
    }

	/**
	 * Updates the inner HTML of UI elements based on the 2FA status.
	 * 
	 * @param {boolean} enabled - Indicates whether 2FA is enabled.
	 */
    updateInnerHTML(enabled) {
        this.stepTitle.innerText = enabled ? 'Disable 2FA' : 'Enable 2FA';
        this.guide.innerText = enabled ? 'Toggle the switch to disable 2FA.' : 'Toggle the switch to begin setting up Two-Factor Authentication.';
    }

	/**
     * Toggles the 2FA status based on user interaction.
     * If enabling 2FA, fetches the QR code; if disabling, sends 
     * a request to disable 2FA.
     */
    async toggle2FA() {
        this.twoFactorEnabled = this.enable2faToggle.checked;
        this.updateUIBasedOnStatus(this.twoFactorEnabled);
        this.updateInnerHTML(true);
    
        if (this.twoFactorEnabled) {
            await this.getQrCode();
        } else if (this.tfa) {
            await api.request('disable-2fa/', 'POST');
			this.messageHandler.showSuccess('Two-factor authentication disabled successfully.');
        }
    }
  
	/**
     * Fetches the QR code for setting up 2FA and displays it in the UI.
     * Handles errors by displaying an appropriate message.
     */
    async getQrCode() {
        try {
            const qrCodeDiv = document.getElementById('qrCode');
            const response = await api.request('setup-2fa/', 'GET');
    
            if (response.qr_code) {
                const img = document.createElement('img');
                img.style.width = '200px';
                img.style.height = '200px';
                img.src = response.qr_code;
				if (qrCodeDiv.firstChild && qrCodeDiv.firstChild.tagName === 'IMG')
					qrCodeDiv.removeChild(qrCodeDiv.firstChild);
				qrCodeDiv.insertAdjacentElement('afterbegin', img);
            }
        } catch (error) {
            this.messageHandler.showError('Error setting up 2FA');
        }
    }
  
	/**
     * Saves the changes made to the 2FA settings by verifying the 
     * provided authentication code and enabling 2FA if successful.
     */
    async saveChanges() {
        try {
            const code = this.authCodeInput.value;
            const response = await api.setupTwoFactor(code);
    
            if (response.success) {
                if (response.backup_codes) {
                    this.displayBackupCodes(response.backup_codes);
                    this.messageHandler.showSuccess('Two-factor authentication enabled successfully.');
                }
            } else {
                this.messageHandler.showError('Two-factor code verification failed. Please try again.');
            }
        } catch (error) {
            this.messageHandler.showError('Two-factor code verification failed. Please try again.');
        }
    }

	/**
     * Displays the backup codes in the UI after enabling 2FA.
     * 
     * @param {Array<string>} codes - The backup codes to display.
     */
    displayBackupCodes(codes) {
        const backupCodesHTML = this.getBackupCodesHTML(codes);
        const modalBody = document.querySelector('.modal-body');
		modalBody.removeChild(document.getElementById('switch'));
		modalBody.removeChild(document.getElementById('setup2fa'));
		modalBody.insertAdjacentHTML('afterbegin', backupCodesHTML);

        const enable2faToggle = document.getElementById('enable2fa');
        const modalFooter = document.querySelector('.modal-footer');

        enable2faToggle.checked = true;
        modalFooter.style.display = 'none';
    }

	/**
     * Generates HTML for displaying backup codes.
     * 
     * @param {Array<string>} code_list - The list of backup codes.
     * @returns {string} - The generated HTML string for backup codes.
     */
    getBackupCodesHTML(code_list) {
        const switchEle = document.getElementById('switch');
        const switchInput = switchEle.querySelector('input');
        switchInput.checked = true;

        return `
        ${switchEle ? switchEle.outerHTML : ''}
        <div class="mb-3">
            <h4 class="mt-4">Backup Codes</h4>
            <p class="text-muted small">Store these codes safely. You can use them if you lose access to your authenticator app.</p>
            <div class="backup-codes">
                <ul class="list-group">
                    ${code_list.map(code => `<li class="list-group-item">${code}</li>`).join('')}
                </ul>
            </div>
        </div>
        `;
    }
}