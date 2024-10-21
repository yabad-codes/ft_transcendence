import BaseHTMLElement from "./BaseHTMLElement.js";
import { displayRequestStatus } from "../utils/errorManagement.js";
import { connectToNotificationServer } from "../utils/NotificationSocket.js";

export class LoginPage extends BaseHTMLElement {
  constructor() {
    super("loginpage");
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the login page ...
    this.login();
    this.switchToSignUpPage();
    this.Oauth42Login();
  }

  login() {
    const form = this.querySelector(".login-form");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const username = event.target.querySelector(
        "input[placeholder='Username']"
      );
      const password = event.target.querySelector(
        "input[placeholder='Password']"
      );

      const message = { username: username.value, password: password.value };

      app.api.post("/api/login/", message).then(async (response) => {
        if (response.status === 200) {
          app.isLoggedIn = true;
          connectToNotificationServer();
          app.profile = await app.api.getProfile();
          app.profile.online = true;
          displayRequestStatus("success", "Login successful");
          app.router.go("/");
          return;
        } else if (response.status === 202) {
          console.log("status: ", response.status);
          app.router.go("/2fa");
          return;
        }
        console.log("status: ", response.status);
        username.value = "";
        password.value = "";

        displayRequestStatus("error", "Username or password is incorrect");
      });
    });
  }

  switchToSignUpPage() {
    const signUpButton = document.getElementById("to-register");

    signUpButton.addEventListener("click", (event) => {
      event.preventDefault();
      app.router.go("/register");
    });
  }

  Oauth42Login() {
    const oauth42Button = this.querySelector(".oauth42");

    oauth42Button.addEventListener("click", (event) => {
      event.preventDefault();
      app.api.get("/api/oauth/login/").then((response) => {
        if (response.status === 200 && response.data.auth_url) {
          window.location.replace(response.data.auth_url);
        } else {
          displayRequestStatus("error", "Failed to initiate OAuth login");
        }
      });
    });
  }
}

customElements.define("login-page", LoginPage);
