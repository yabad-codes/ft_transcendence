import BaseHTMLElement from "./BaseHTMLElement.js";

export class GamePage extends BaseHTMLElement {
  constructor() {
    super("gamepage");
    this.matchmakingSocket = null;
  }

  connectedCallback() {
    super.connectedCallback();
    this.createShadowRoot();
    this.setupEventListeners();
  }

  createShadowRoot() {
    const template = document.getElementById("gamepage");
    const templateContent = template.content;

    this.attachShadow({ mode: "open" });
    this.shadowRoot.appendChild(templateContent.cloneNode(true));
  }

  setupEventListeners() {
    const requestGameBtn = this.shadowRoot.getElementById("requestGameBtn");
    const cancelMatchmakingBtn = this.shadowRoot.getElementById(
      "cancelMatchmakingBtn"
    );

    requestGameBtn.addEventListener("click", () => this.requestGame());
    cancelMatchmakingBtn.addEventListener("click", () =>
      this.cancelMatchmaking()
    );
  }

  async requestGame() {
    try {
      const response = await fetch(
        "http://localhost:8081/api/play/request-game/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            // Include authentication headers if required
            // 'Authorization': 'Bearer YOUR_TOKEN_HERE'
          },
          credentials: "include",
          mode: "cors",
        }
      );
      const data = await response.json();

      if (response.ok) {
        this.updateStatus("Connecting to matchmaking...");
        this.connectToMatchmaking(data.websocket_url);
      } else {
        this.updateStatus(`Error: ${data.message}`);
      }
    } catch (error) {
      this.updateStatus(`Error: ${error.message}`);
    }
  }

  connectToMatchmaking(websocketUrl) {
    websocketUrl = websocketUrl.replace(/\/$/, "");
    this.matchmakingSocket = new WebSocket(
      `ws://localhost:8081${websocketUrl}/`
    );

    this.matchmakingSocket.onopen = (e) => {
      this.updateStatus("Connected to matchmaking. Waiting for opponent...");
      this.toggleButtons(true);
    };

    this.matchmakingSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status === "matched") {
        this.updateStatus(`Matched! Game ID: ${data.game_id}`);
        // Here you would typically start the game or redirect to a game page
        console.log(`Starting game with ID: ${data.game_id}`);
      }
    };

    this.matchmakingSocket.onclose = (e) => {
      this.updateStatus("Disconnected from matchmaking");
      this.toggleButtons(false);
    };
  }

  cancelMatchmaking() {
    if (
      this.matchmakingSocket &&
      this.matchmakingSocket.readyState === WebSocket.OPEN
    ) {
      this.matchmakingSocket.send(
        JSON.stringify({ action: "cancel_matchmaking" })
      );
      this.matchmakingSocket.close();
    }
    this.updateStatus("Matchmaking cancelled");
    this.toggleButtons(false);
  }

  updateStatus(message) {
    const statusElement = this.shadowRoot.getElementById("matchmakingStatus");
    statusElement.textContent = message;
  }

  toggleButtons(isMatchmaking) {
    const requestGameBtn = this.shadowRoot.getElementById("requestGameBtn");
    const cancelMatchmakingBtn = this.shadowRoot.getElementById(
      "cancelMatchmakingBtn"
    );
    requestGameBtn.disabled = isMatchmaking;
    cancelMatchmakingBtn.disabled = !isMatchmaking;
  }
}

customElements.define("game-page", GamePage);
