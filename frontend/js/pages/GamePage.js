import BaseHTMLElement from "./BaseHTMLElement.js";

export class GamePage extends BaseHTMLElement {
  constructor() {
    super("gamepage");
    this.matchmakingSocket = null;
    this.gameState = "matchmaking";
  }

  connectedCallback() {
    super.connectedCallback();
    this.setupEventListeners();
  }

  setupEventListeners() {
    const requestGameBtn = document.getElementById("requestGameBtn");
    const cancelMatchmakingBtn = document.getElementById(
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
        "https://localhost:8081/api/play/request-game/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
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
      `wss://localhost:8081${websocketUrl}/`
    );

    this.matchmakingSocket.onopen = () => {
      this.updateStatus("Waiting for opponent...");
      this.toggleButtons(true);
    };

    this.matchmakingSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status === "matched") {
        this.updateStatus(`Matched! Game ID: ${data.game_id}`);
        this.matchmakingSocket.close();
        // render the game screen
        const gameScreen = document.createElement("game-screen");
        gameScreen.gameId = data.game_id;
        document.body.innerHTML = "";
        document.body.appendChild(gameScreen);
      }
    };

    this.matchmakingSocket.onclose = () => {
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
    const statusElement = document.getElementById("matchmakingStatus");
    statusElement.textContent = message;
  }

  toggleButtons(isMatchmaking) {
    const requestGameBtn = document.getElementById("requestGameBtn");
    const cancelMatchmakingBtn = document.getElementById(
      "cancelMatchmakingBtn"
    );
    requestGameBtn.disabled = isMatchmaking;
    cancelMatchmakingBtn.disabled = !isMatchmaking;
  }
}

customElements.define("game-page", GamePage);
