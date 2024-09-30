import BaseHTMLElement from "./BaseHTMLElement.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class RegisterPage extends BaseHTMLElement {
  constructor() {
    super("registerpage");
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the login page ...
    this.switchToLoginPage();
    this.register();
    this.Oauth42Login();
  }


  switchToLoginPage() {
    const loginButton = document.getElementById("to-login");

    loginButton.addEventListener("click", (event) => {
      event.preventDefault();
      app.router.go("/login");
    });
  }

  register() {
    const registerForm = this.querySelector(".register-form");
    
    registerForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const username = event.target.querySelector("input[placeholder='Username']");
      const firstname = event.target.querySelector("input[placeholder='First name']");
      const lastname = event.target.querySelector("input[placeholder='Last name']");
      const password = event.target.querySelector("input[placeholder='Password']");
      const confirmPassword = event.target.querySelector("input[placeholder='Confirm Password']");

      const message = { username: username.value, first_name: firstname.value, last_name: lastname.value, password: password.value, password_confirm: confirmPassword.value };

      app.api.post("/api/register/", message).then((response) => {
        if (response.status === 201) {
          displayRequestStatus("success", "Account created successfully. Please login.");
          app.router.go("/login");
          return;
        }
        password.value = "";
        confirmPassword.value = "";
        
        // Display the first error message
        for (let field in response.data) {
          for (let error of response.data[field]) {
            displayRequestStatus("error", error);
            return;
          }
        }
      })
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

customElements.define("register-page", RegisterPage);
