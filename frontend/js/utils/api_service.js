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
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return response.json();
	},
	// verify two factor authentication
	verifyTwoFactor(code) {
		return this.request('verify-2fa/', 'POST', { code });
	},
	// verify backup code
	verifyBackupCode(code) {
		return this.request('use-backup-code/', 'POST', { code });
	},
}

export { api }

