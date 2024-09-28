const api = {
	baseUrl: 'https://localhost:8081/api',

	async request(endpoint, method = 'GET', data = null) {
		const url = `${this.baseUrl}/${endpoint}`;
		const options = {
			method,
			headers : {
				'Content-Type': 'application/json',
			},
			credential : 'include',
		};
		
		if (data) {
			options.body = JSON.stringify(data);
		}

		const response = await fetch(url, options);

		if (response.status >= 500) {
			throw new Error('500 Internal Server Error');
		}

		if (response.status === 204)
			return null;
		
		return response.json();
	},
	// verify two factor authentication
	verifyTwoFactor(code) {
		return this.request('verify-2fa/', 'POST', { code });
	},
	// check if user already has two factor authentication enabled
	checkTwoFactor() {
		return this.request('check-2fa/');
	},
	// setup two factor authentication
	setupTwoFactor(code) {
		return this.request('setup-2fa/', 'POST', { code });
	},
	// disable two factor authentication
	disableTwoFactor() {
		return this.request('disable-2fa/', 'POST');
	},
	// verify backup code
	verifyBackupCode(code) {
		return this.request('use-backup-code/', 'POST', { code });
	},
	// update account information
	updateAccount(data) {
		return this.request('update-info/', 'POST', data);
	},
	// get user details
	getUserDetails() {
		return this.request('user-details/');
	},
	// update password
	updatePassword(data) {
		return this.request('update-password/', 'POST', data);
	},
	// get all players
	getPlayers() {
		return this.request('players/');
	},
	// get blocked users
	getBlockedUsers() {
		return this.request('blocked/');
	},
	// unblock user
	unblockUser(username) {
		return this.request(`profile/${username}/unblock`, 'DELETE');
	},
}

export { api }
