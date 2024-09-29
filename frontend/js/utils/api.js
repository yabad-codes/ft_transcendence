import Cookies from "./Cookies.js";
const api = {
  baseUrl: "https://localhost:8081/api",

  get: async (url) => {
    const response = await fetch(url);
    const data = await response.json();
    return { status: response.status, data };
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
    return { status: response.status, data: text ? JSON.parse(text) : {} };
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
    return { status: response.status, data: text ? JSON.parse(text) : {} };
  },
  delete: async (url) => {
    const response = await fetch(url, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
      },
    });
    return { status: response.status, data: await response.text() };
  },

  getProfile: async () => {
    // Get the user profile
    return await app.api.get("/api/me/").then((response) => {
      if (response.status !== 200) {
        return null;
      }
      return response.data;
    });
  },

  async request(endpoint, method = "GET", data = null) {
    const URL = `${this.baseUrl}/${endpoint}`;
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
      credential: "include",
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
    return this.request("players/");
  },
};

export { api };
