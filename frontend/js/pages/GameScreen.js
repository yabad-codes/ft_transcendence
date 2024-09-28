import BaseHTMLElement from "./BaseHTMLElement.js";

export class GameScreen extends BaseHTMLElement {
  constructor() {
    super();
    this.gameId = null;
    this.gameSocket = null;
    this.gameState = null;
    this.playerRole = null;
    this.playerUsername = null;
    this.canvas = null;
    this.ctx = null;
    this.gameOver = false;
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
        <div id="gameOverOverlay" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); color: white; display: flex; flex-direction: column; justify-content: center; align-items: center;">
          <h2 id="gameOverMessage" style="font-size: 32px; margin-bottom: 20px;"></h2>
          <button id="newGameButton" style="font-size: 18px; padding: 10px 20px; margin: 10px;">New Game</button>
        </div>
      </div>
    `;
    this.canvas = this.querySelector("#game");
    this.ctx = this.canvas.getContext("2d");
    this.gameOverOverlay = this.querySelector("#gameOverOverlay");
    this.gameOverMessage = this.querySelector("#gameOverMessage");
    this.newGameButton = this.querySelector("#newGameButton");

    this.newGameButton.addEventListener("click", () => this.startNewGame());
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
    this.setupEventListeners();
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
          console.log(jsonData);
          if (jsonData.status === "player-role") {
            this.setPlayerRole(jsonData.role);
            this.setPlayerUsername(jsonData.username);
            console.log(`You are player ${jsonData.role}`);
          } else if (jsonData.status === "game_over") {
            this.handleGameOver(jsonData.winner);
          } else if (jsonData.status === "game_start") {
            console.log("Game is starting!");
            this.gameOver = false;
            this.gameOverOverlay.style.display = "none";
          }
        } catch (e) {
          console.error("Unexpected message from game server:", e);
        }
      }
    };

    ws.onclose = () => {
      console.log("Disconnected from game server");
      if (!this.gameOver) {
        this.handleUnexpectedDisconnection();
      }
    };

    this.gameSocket = ws;
  }

  handleGameOver(winner) {
    this.gameOver = true;
    let message;
    if (winner) {
      message = `Game over! ${winner} wins!`;
    } else {
      message = "Game over! It's a tie!";
    }
    this.gameOverMessage.textContent = message;
    this.gameOverOverlay.style.display = "flex";
    console.log(message);
    // close the connection
    this.gameSocket.close();
  }

  handleUnexpectedDisconnection() {
    this.gameOverMessage.textContent =
      "Connection lost. The game ended unexpectedly.";
    this.gameOverOverlay.style.display = "flex";
  }

  startNewGame() {
    // Implement logic to start a new game, e.g., redirect to game setup page
    window.location.href = "/";
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

  setPlayerUsername(username) {
    this.playerUsername = username;
  }

  setupEventListeners() {
    window.addEventListener("keydown", (e) => this.handleKeyPress(e));
  }

  handleKeyPress(e) {
    if (this.gameOver) return;
    if (e.key === "w" || e.key === "s") {
      this.sendPaddleMove(e.key);
    }
  }

  sendPaddleMove(key) {
    this.gameSocket.send(key);
  }

  drawGame() {
    if (!this.gameState || this.gameOver) return;
    this.drawInitialGame();
  }

  drawInitialGame() {
    // Set canvas size
    this.canvas.width = 800;
    this.canvas.height = 600;

    // Clear the canvas
    this.ctx.fillStyle = "white";
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw the border
    this.ctx.strokeStyle = "black";
    this.ctx.lineWidth = 2;
    this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw the center line
    this.ctx.setLineDash([5, 15]);
    this.ctx.beginPath();
    this.ctx.moveTo(this.canvas.width / 2, 0);
    this.ctx.lineTo(this.canvas.width / 2, this.canvas.height);
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    // Draw the paddles
    this.ctx.fillStyle = "#117a8b"; // Blue for left paddle
    this.ctx.fillRect(20, this.gameState.player1Y, 10, 80); // Left paddle
    this.ctx.fillStyle = "#dc3545"; // Red for right paddle
    this.ctx.fillRect(this.canvas.width - 30, this.gameState.player2Y, 10, 80); // Right paddle

    // Draw the ball
    this.ctx.beginPath();
    this.ctx.arc(
      this.gameState.ballX,
      this.gameState.ballY,
      10,
      0,
      Math.PI * 2
    );
    this.ctx.fillStyle = "#FFA726"; // Orange for the ball
    this.ctx.fill();
    this.ctx.closePath();

    // Draw the scores
    this.ctx.font = "48px Arial";
    this.ctx.fillStyle = "#117a8b"; // Blue for left score
    this.ctx.fillText(this.gameState.score1, this.canvas.width / 4, 50);
    this.ctx.fillStyle = "#dc3545"; // Red for right score
    this.ctx.fillText(this.gameState.score2, (3 * this.canvas.width) / 4, 50);
  }
}

customElements.define("game-screen", GameScreen);
