import BaseHTMLElement from "./BaseHTMLElement.js";

export class LeaderboardPage extends BaseHTMLElement {
  constructor() {
	// The templateId is the id of the HTML template element in the DOM, for example: <template id="login-page">...</template>
	// super
    super("leaderboardpage");
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the login page ...
  }
}

// Define the new custom element in the customElements registry so it can be used in the DOM later
customElements.define("leaderboard-page", LeaderboardPage);
