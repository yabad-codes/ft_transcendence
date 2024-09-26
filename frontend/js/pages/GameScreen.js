import BaseHTMLElement from "./BaseHTMLElement.js";

export class GameScreen extends BaseHTMLElement {
  constructor() {
    super();
    this.gameId = null;
    this.gameSocket = null;
    this.gameState = null;
    this.playerRole = null;
    this.canvas = null;
    this.ctx = null;
  }

  connectedCallback() {
    this.render();
    this.initializeGame();
    this.drawInitialGame();
    this.connectToGameServer();
  }

  render() {
    this.innerHTML = `
      <div id="gameScreen">
        <canvas id="game" width="800" height="600"></canvas>
      </div>
    `;
    this.canvas = this.querySelector("#game");
    this.ctx = this.canvas.getContext("2d");
  }

  initializeGame() {
    this.gameState = {
      ballX: 400,
      ballY: 300,
      player1Y: 250,
      player2Y: 250,
      score1: 0,
      score2: 0,
    };
    // this.setupEventListeners();
  }

  drawInitialGame() {
    // Clear the canvas
    this.ctx.fillStyle = "black";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw the paddles
    this.ctx.fillStyle = "white";
    this.ctx.fillRect(10, this.gameState.player1Y, 10, 100); // Left paddle
    this.ctx.fillRect(780, this.gameState.player2Y, 10, 100); // Right paddle

    // Draw the ball
    this.ctx.beginPath();
    this.ctx.arc(
      this.gameState.ballX,
      this.gameState.ballY,
      10,
      0,
      Math.PI * 2
    );
    this.ctx.fillStyle = "white";
    this.ctx.fill();
    this.ctx.closePath();

    // Draw the scores
    this.ctx.font = "32px Arial";
    this.ctx.fillText(this.gameState.score1, this.canvas.width / 4, 50);
    this.ctx.fillText(this.gameState.score2, (3 * this.canvas.width) / 4, 50);
  }

  connectToGameServer() {
    const ws = new WebSocket(`wss://localhost:8081/ws/pong/${this.gameId}/`);

    ws.onopen = () => {
      console.log("Connected to game server");
    };

    ws.onmessage = (e) => {
      if (e.data instanceof Blob) {
        e.data.arrayBuffer().then((buffer) => {
          this.decodeGameState(buffer);
          this.drawGame();
        });
      } else if (e.data instanceof ArrayBuffer) {
        this.decodeGameState(e.data);
        this.drawGame();
      } else {
        try {
          const jsonData = JSON.parse(e.data);
          if (jsonData.status === "player-role") {
            this.setPlayerRole(jsonData.role);
            console.log(`You are player ${jsonData.role}`);
          }
        } catch (e) {
          console.error("Unexpected message from game server");
        }
      }
    };

    ws.onclose = () => {
      console.log("Disconnected from game server");
    };

    this.gameSocket = ws;
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

  setPlayerRole(role) {
    this.playerRole = role;
  }

  setupEventListeners() {
    window.addEventListener("keydown", (e) => this.handleKeyPress(e));
  }

  handleKeyPress(e) {
    if (e.key === "w" || e.key === "s") {
      this.sendPaddleMove(e.key);
    }
  }

  sendPaddleMove(key) {
    if (this.gameSocket && this.gameSocket.readyState === WebSocket.OPEN) {
      this.gameSocket.send(`${key}${this.playerRole}`);
      console.log(`Sent ${key}${this.playerRole}`);
    }
  }

  drawGame() {
    if (!this.gameState) return;

    // Clear the canvas
    this.ctx.fillStyle = "black";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw the paddles
    this.ctx.fillStyle = "white";
    this.ctx.fillRect(10, this.gameState.player1Y, 10, 100); // Left paddle
    this.ctx.fillRect(780, this.gameState.player2Y, 10, 100); // Right paddle

    // Draw the ball
    this.ctx.beginPath();
    this.ctx.arc(
      this.gameState.ballX,
      this.gameState.ballY,
      10,
      0,
      Math.PI * 2
    );
    this.ctx.fillStyle = "white";
    this.ctx.fill();
    this.ctx.closePath();

    // Draw the scores
    this.ctx.font = "32px Arial";
    this.ctx.fillText(this.gameState.score1, this.canvas.width / 4, 50);
    this.ctx.fillText(this.gameState.score2, (3 * this.canvas.width) / 4, 50);
  }
}

customElements.define("game-screen", GameScreen);
