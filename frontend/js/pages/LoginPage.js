import BaseHTMLElement from "./BaseHTMLElement.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class LoginPage extends BaseHTMLElement {
  constructor() {
    super("loginpage");
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the login page ...
    this.login();
    this.switchToSignUpPage();
  }

  login() {
    const form = this.querySelector(".login-form");

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const username = event.target.querySelector("input[placeholder='Username']");
      const password = event.target.querySelector("input[placeholder='Password']");

      console.log("username: ", username.value);
      console.log("password: ", password.value);

      const message = { username:username, password:password };

      app.api.post("/api/token/", message).then((response) => {
        if (response.status === 200) {
          app.isLoggedIn = true;
          app.profile = app.api.getProfile();
          app.router.go("/");
          return;
        }
        username.value = "";
        password.value = "";
        
        displayRequestStatus("error", response.data);
      });
    });
  }

  switchToSignUpPage() {
    const signUpButton = document.getElementById("to-signup");

    signUpButton.addEventListener("click", (event) => {
      event.preventDefault();
      app.router.go("/signup");
    });
  }

  Oauth42Login() {
    const oauth42Button = this.querySelector(".oauth42");

    oauth42Button.addEventListener("click", (event) => {
      event.preventDefault();
      app.api.get("/api/oauth42").then((response) => {
        if (response.status === 200) {
          window.location.href = response.data;
        }
      });
    });
  }
}

customElements.define("login-page", LoginPage);
