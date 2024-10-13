import BaseHTMLElement from "./BaseHTMLElement.js";

export class GamePage extends BaseHTMLElement {
  constructor() {
    super("gamepage");
    this.matchmakingSocket = null;
    this.gameState = "idle";
  }

  connectedCallback() {
    super.connectedCallback();
    this.render();
    this.setupEventListeners();
  }

  render() {
    this.innerHTML = `
      <div class="game-container">
        <h1 class="game-title">Pong Game</h1>
        <div class="game-options">
          <button id="requestGameBtn" class="btn btn-primary">Find Match</button>
          <button id="cancelMatchmakingBtn" class="btn btn-danger" disabled>Cancel</button>
        </div>
        <div id="matchmakingStatus" class="status-message"></div>
        <div class="game-instructions">
          <h2>How to Play</h2>
          <ul>
            <li>Use 'W' key to move paddle up</li>
            <li>Use 'S' key to move paddle down</li>
            <li>First player to score 11 points wins</li>
          </ul>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    const requestGameBtn = this.querySelector("#requestGameBtn");
    const cancelMatchmakingBtn = this.querySelector("#cancelMatchmakingBtn");

    requestGameBtn.addEventListener("click", () => this.requestGame());
    cancelMatchmakingBtn.addEventListener("click", () =>
      this.cancelMatchmaking()
    );
  }

  async requestGame() {
    try {
      const response = await fetch("/api/play/request-game/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        mode: "cors",
      });

      const data = await response.json();
      console.log(data);

      if (response.ok) {
        this.updateStatus("Connecting to matchmaking...");
        this.connectToMatchmaking(data.websocket_url);
      } else {
        this.updateStatus(`Error: ${data.message}`, "error");
      }
    } catch (error) {
      this.updateStatus(`Error: ${error.message}`, "error");
    }
  }

  connectToMatchmaking(websocketUrl) {
    websocketUrl = websocketUrl.replace(/\/$/, "");
    this.matchmakingSocket = new WebSocket(
      `wss://${window.location.host}${websocketUrl}/`
    );

    this.matchmakingSocket.onopen = () => {
      this.updateStatus("Waiting for opponent...", "waiting");
      this.toggleButtons(true);
    };

    this.matchmakingSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.status === "matched") {
        this.updateStatus(`Matched! Preparing game...`, "success");
        this.matchmakingSocket.close();
        this.startGame(data.game_id);
      }
    };

    this.matchmakingSocket.onclose = () => {
      if (this.gameState === "matchmaking") {
        this.updateStatus("Disconnected from matchmaking", "error");
        this.toggleButtons(false);
      }
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
    this.updateStatus("Matchmaking cancelled", "info");
    this.toggleButtons(false);
  }

  updateStatus(message, type = "info") {
    const statusElement = this.querySelector("#matchmakingStatus");
    statusElement.textContent = message;
    statusElement.className = `status-message ${type}`;
  }

  toggleButtons(isMatchmaking) {
    const requestGameBtn = this.querySelector("#requestGameBtn");
    const cancelMatchmakingBtn = this.querySelector("#cancelMatchmakingBtn");
    requestGameBtn.disabled = isMatchmaking;
    cancelMatchmakingBtn.disabled = !isMatchmaking;
    this.gameState = isMatchmaking ? "matchmaking" : "idle";
  }

  startGame(gameId) {
    // Create and render the GameScreen component
    const gameScreen = document.createElement("game-screen");
    gameScreen.gameId = gameId;
    document.body.innerHTML = "";
    document.body.appendChild(gameScreen);
  }
}

customElements.define("game-page", GamePage);
