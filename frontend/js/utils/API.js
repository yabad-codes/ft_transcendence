import Cookies from "./Cookies.js";

const API = {
	get: async (url) => {
		const response = await fetch(url);
		return response.json();
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
		return text ? JSON.parse(text) : {};
	},
}

export default API;