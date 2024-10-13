import { api } from '../utils/api_service.js';
import { MessageHandler } from './MessageHandler.js';

/**
 * PasswordManager Class
 * 
 */

export class PasswordManager {
	constructor() {

		this.currentPassword = document.getElementById('currentPassword');
		this.new_password = document.getElementById('newPassword');
		this.confirm_password = document.getElementById('confirmPassword');

		this.alertElement = document.getElementById('messageAlert');
		this.messageElement = document.getElementById('messageText');
		this.messageHandler = new MessageHandler(this.alertElement, this.messageElement);
	}

	validator(data) {
		if (data.old_password === '' || data.new_password === '' || data.confirm_new_password === '') {
			this.messageHandler.showError('All fields are required.');
			return false;
		}
		if (data.new_password !== data.confirm_new_password) {
			this.messageHandler.showError('Passwords do not match.');
			return false;
		}
		return true;
	}

	async saveChanges() {
		const data = {
			old_password: this.currentPassword.value,
			new_password: this.new_password.value,
			confirm_new_password: this.confirm_password.value
		};
		
		if (!this.validator(data))
			return;

		try {
			const response = await api.updatePassword(data);
			if (response.success) {
				this.messageHandler.showSuccess('Password updated successfully.');
			} else {
				this.messageHandler.showError('Failed to update password.');
			}
		} catch (error) {
			this.messageHandler.showError(error);
		}
	}
	
}