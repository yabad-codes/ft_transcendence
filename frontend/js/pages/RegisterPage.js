import BaseHTMLElement from "./BaseHTMLElement.js";

export class RegisterPage extends BaseHTMLElement {
  constructor() {
    super("registerpage");
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the login page ...
  }
}

customElements.define("register-page", RegisterPage);
