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
        this.renderGameScreen(data.game_id);
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

  renderGameScreen(gameId) {
    const gameScreenTemplate = document
      .getElementById("gamescreen")
      .content.cloneNode(true);
    const gameIdElement = gameScreenTemplate.querySelector("#gameId");
    gameIdElement.textContent = gameId;

    const gameContainer = document.querySelector(".game-container");
    gameContainer.innerHTML = ""; // Clear the existing content
    gameContainer.appendChild(gameScreenTemplate); // Load the new game screen
    this.initGameWebSocket(gameId);
  }

  initGameWebSocket(gameId) {
    const ws = new WebSocket(`wss://localhost:8081/ws/pong/${gameId}/`);

    ws.onopen = () => {
      console.log("Connected to game websocket");
    };

    ws.onmessage = (e) => {
      this.handleWebSocketMessage(e);
    };

    ws.onclose = () => {
      console.log("Disconnected from game websocket");
    };

    ws.onerror = (error) => {
      console.error("Game websocket error", error);
    };
  }

  async handleWebSocketMessage(event) {
    if (typeof event.data === "string") {
      console.log("Received string message : ", event.data);
      try {
        const jsonData = JSON.parse(event.data);
        if (jsonData.type === "game_start") {
          console.log("Game started", jsonData);
        }
      } catch (error) {
        console.error("Error parsing message", error);
      }
    } else if (event.data instanceof Blob) {
      console.log("Received binary message : ", event.data);
      try {
        const arrayBuffer = await event.data.arrayBuffer();
        console.log("Received binary data : ", new Uint8Array(arrayBuffer));
        this.decodeGameState(arrayBuffer);
        console.log("Decoded game state : ", this.gameState);
        console.log("rendering game state");
      } catch (error) {
        console.error("Error parsing binary message", error);
      }
    }
  }

  decodeGameState(arrayBuffer) {
    const view = new DataView(arrayBuffer);
    this.gameState = {
      ballX: view.getFloat32(0),
      ballY: view.getFloat32(4),
      player1Y: view.getFloat32(8),
      player2Y: view.getFloat32(12),
      score1: view.getUint32(16),
      score2: view.getUint32(20),
    };
  }
}

customElements.define("game-page", GamePage);
