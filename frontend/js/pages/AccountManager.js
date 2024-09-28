import { api } from '../utils/api_service.js';
import { MessageHandler } from './MessageHandler.js';

/**
 * AccountManager Class
 * 
 */

export class AccountManager {
	constructor() {

		this.username = document.getElementById('username');
		this.firstName = document.getElementById('firstName');
		this.lastName = document.getElementById('lastName');
		this.profilePicture = document.getElementById('profilePicture');

		this.alertElement = document.getElementById('messageAlert');
		this.messageElement = document.getElementById('messageText');
		this.messageHandler = new MessageHandler(this.alertElement, this.messageElement);

		this.profileName = document.getElementById('profileName');
		this.profileId = document.getElementById('profileId');

		this.originalValues = {};

		this.setupFieldsValues();

	}

	async setupFieldsValues() {
		try {
			const response = await api.getUserDetails();
			if (response.success) {

				this.originalValues = {
					username: response.username,
					first_name: response.first_name,
					last_name: response.last_name,
				};

				this.username.value = response.username;
				this.firstName.value = response.first_name;
				this.lastName.value = response.last_name;

				this.profileName.textContent = `${response.first_name} ${response.last_name}`;
				if (response.avatar)
					this.profilePicture.src = response.avatar;
				this.profileId.textContent = response.user_id?.substring(0, 8);
			} else {
				this.messageHandler.showError('Failed to get user details.');
			}
		} catch (error) {
			this.messageHandler.showError('Failed to get user details.');
		}
	}

	async saveChanges() {

		const data = {};

		if (this.username.value !== this.originalValues.username)
			data.username = this.username.value;

		if (this.firstName.value !== this.originalValues.first_name)
			data.first_name = this.firstName.value;

		if (this.lastName.value !== this.originalValues.last_name)
			data.last_name = this.lastName.value;

		if (Object.keys(data).length === 0) {
			this.messageHandler.showError('No changes to save.');
			return;
		}

		try {
			const response = await api.updateAccount(data);

			if (response.success) {
				this.setupFieldsValues();
				this.messageHandler.showSuccess('Account updated successfully.');
			} else {
				const errorMessages = response.errors;
				if (Object.keys(errorMessages).length > 0) {
					let errorMessage = errorMessages[Object.keys(errorMessages)[0]][0];
					this.messageHandler.showError(errorMessage);
				}
			}
		} catch (error) {
			this.messageHandler.showError(error);
		}
		
	}
	
}