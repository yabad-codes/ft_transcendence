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
		return text ? JSON.parse(text) : {};
	},
	delete: async (url) => {
		const response = await fetch(url, {
			method: "DELETE",
			headers: {
				"X-CSRFToken": Cookies.get("csrftoken"),
			},
		});
		return response;
	},
}

export default API;