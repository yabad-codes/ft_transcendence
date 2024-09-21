const api = {
	baseUrl: 'http://localhost:8081/api',

	async request(endpoint, method = 'GET', data = null) {
		const URL = `${this.baseUrl}/${endpoint}`;
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

		const response = await fetch(URL, options);
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return response.json();
	},
	// get all players
	getPlayers() {
		return this.request('players/');
	}
}

export { api }