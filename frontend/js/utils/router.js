import { connectToNotificationServer } from "./NotificationSocket.js";
import { displayRequestStatus } from "./errorManagement.js";

const Router = {
  init: async () => {
    app.isLoggedIn = await Router.checkIsLoggedIn();

    // console.log("Location: ", location.pathname);
    Router.go(location.pathname + location.search);

    window.addEventListener("popstate", (event) => {
      Router.go(event.state ? event.state.router : "/", false);
    });
  },

  go: (router, addToHistory = true) => {
    if (addToHistory && location.pathname !== router) {
      if (window.history.length > 1) {
        window.history.pushState({ router }, null, router);
      } else {
        window.history.replaceState({ router }, null, router);
      }
    }

    // render the pages
    // this could be refactored and scaled later
    if (router === "/") {
      Router.loadMainHomeContent("game-page");
    } else if (router === "/profile") {
      Router.loadMainHomeContent("profile-page");
    } else if (router === "/chat") {
      Router.loadMainHomeContent("chat-page");
    } else if (router === "/leaderboard") {
      Router.loadMainHomeContent("leaderboard-page");
    } else if (router === "/settings") {
      Router.loadMainHomeContent("settings-page");
    } else if (router === "/login") {
      Router.loadSignAndLoginPage("login-page");
    } else if (router === "/register") {
      Router.loadSignAndLoginPage("register-page");
    } else if (router.includes("/oauth-callback")) {
      Router.handleOAuthCallback();
    } else if (router === "/2fa") {
      Router.loadMainHomeContent("twofa-page");
    } else {
      Router.loadNotFoundPage("not-found-page");
    }
  },

  checkIsLoggedIn: async () => {
    // Check if the user is logged in
    app.profile = await app.api.getProfile();

    if (app.profile) {
      app.profile.online = true;
      return true;
    }

    return false;
  },

  loadMainHomeContent: (pageName) => {
    // If the user is not logged in go to login page
    if (!app.isLoggedIn) {
      console.log("User is not logged in");
      app.router.go("/login");
      return;
    }

    // If the home page doesn't exist in the DOM then render the home page first
    if (!document.querySelector("home-page")) {
      Router.loadHomePage();
    }

    const mainElement = document.querySelector("main");

    // If the page content already exists, no need to render it again (for performance reasons)
    if (mainElement.querySelector(pageName)) return;

    // Load the new page on the main content
    const mainContent = document.createElement(pageName);
    mainElement.innerHTML = "";
    mainElement.appendChild(mainContent);
  },

  loadHomePage: () => {
    // Delete home, login, sign up or 404 pages if they exist then load the home page
    Router.removeOldPages();
    Router.insertPage("home-page");
  },

  loadSignAndLoginPage: (pageName) => {
    // Delete home, login, sign up or 404 pages if they exist then load the sign up or login page
    Router.removeOldPages();

    if (app.isLoggedIn) {
      app.router.go("/");
      return;
    }

    Router.insertPage(pageName);
  },

  loadNotFoundPage: () => {
    // Delete home, login, sign up or 404 pages if they exist then load the 404 page
    Router.removeOldPages();
    Router.insertPage("not-found-page");
  },

  // Insert the page to the body
  insertPage: (pageName) => {
    const newElement = document.createElement(pageName);
    const bootstrapScript = document.querySelector(
      "body > script:last-of-type"
    ); // Insert the pages before bootstrap js bundle script

    if (bootstrapScript) {
      document.body.insertBefore(newElement, bootstrapScript);
    } else {
      document.body.appendChild(newElement);
    }
  },

  removeOldPages: () => {
    // Remove old pages if they exist
    const oldPages = [
      "home-page",
      "login-page",
      "signup-page",
      "register-page",
      "not-found-page",
    ];

    oldPages.forEach((page) => {
      const pageElement = document.querySelector(page);
      if (pageElement) pageElement.remove();
    });
  },

  async handleOAuthCallback() {
    const urlParams = new URLSearchParams(window.location.search);

    const status = urlParams.get("status");
    const message = urlParams.get("message");

    if (status === "success") {
      app.isLoggedIn = true;
      app.profile = await app.api.getProfile();
      window.history.replaceState(null, null, "/");
      app.router.go("/");
      connectToNotificationServer();
      displayRequestStatus("success", message);
      return;
    }

    displayRequestStatus("error", message || "OAuth login failed");
    window.history.replaceState(null, null, "/login");
    app.router.go("/login");
  },
};

export default Router;
