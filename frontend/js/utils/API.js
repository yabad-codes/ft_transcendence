import Cookies from "./Cookies.js";

const API = {
	get: async (url) => {
		const response = await fetch(url);
		const data = await response.json();
		return {status: response.status, data};
	},
	post: async (url, data) => {
		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": Cookies.get("csrftoken"),
			},
			body: JSON.stringify(data),
		});
		const text = await response.text();
		return {status: response.status, data: text ? JSON.parse(text) : {}};
	},
	patch: async (url, data) => {
		const response = await fetch(url, {
			method: "PATCH",
			headers: {
				"Content-Type": "application/json",
				"X-CSRFToken": Cookies.get("csrftoken"),
			},
			body: JSON.stringify(data),
		});
		const text = await response.text();
		return {status: response.status, data: text ? JSON.parse(text) : {}};
	},
	delete: async (url) => {
		const response = await fetch(url, {
			method: "DELETE",
			headers: {
				"X-CSRFToken": Cookies.get("csrftoken"),
			},
		});
		return {status: response.status, data: await response.text()};
	},

	getProfile: async () => {
        // Get the user profile
        return await app.api.get('/api/me/').then(response => {
            if (response.status !== 200) {
                return null;
            }
            return response.data;
        });
    },
}

export default API;