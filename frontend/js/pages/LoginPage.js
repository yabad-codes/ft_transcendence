import BaseHTMLElement from "./BaseHTMLElement.js";

export class LoginPage extends BaseHTMLElement {
  constructor() {
    super("loginpage");
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the login page ...
  }
}

customElements.define("login-page", LoginPage);
