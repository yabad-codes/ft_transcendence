import BaseHTMLElement from "./BaseHTMLElement.js";

export class GameScreen extends BaseHTMLElement {
  constructor() {
    super();
    this.gameId = null;
    this.gameSocket = null;
    this.gameState = null;
    this.currentPlayer = null;
    this.opponent = null;
    this.canvas = null;
    this.ctx = null;
    this.gameOver = false;
  }

  connectedCallback() {
    this.render();
  }

  render() {
    this.innerHTML = `
      <div id="gameScreen" class="flex flex-col items-center justify-center h-screen bg-gray-100">
        <div class="mb-4 text-2xl font-bold">Pong Game</div>
        <div class="flex items-center justify-between w-full max-w-4xl mb-4">
          <div id="leftPlayer" class="flex flex-col items-center">
            <img src="/api/placeholder/100/100" alt="Player 1" class="w-16 h-16 rounded-full mb-2">
            <h3 class="text-lg font-semibold"></h3>
            <div class="score text-3xl font-bold"></div>
          </div>
          <div id="rightPlayer" class="flex flex-col items-center">
            <img src="/api/placeholder/100/100" alt="Player 2" class="w-16 h-16 rounded-full mb-2">
            <h3 class="text-lg font-semibold"></h3>
            <div class="score text-3xl font-bold"></div>
          </div>
        </div>
        <canvas id="game" width="1000" height="600" class="border-4 border-gray-800"></canvas>
        <div id="gameOverOverlay" class="hidden fixed top-0 left-0 w-full h-full bg-black bg-opacity-70 flex flex-col justify-center items-center">
          <h2 id="gameOverMessage" class="text-4xl font-bold text-white mb-8"></h2>
          <button id="newGameButton" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            New Game
          </button>
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

  set _setGameId(gameId) {
    this.gameId = gameId;
    this.initializeGame();
    this.drawInitialGame();
    this.connectToGameServer();
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
    const ws = new WebSocket(
      `wss://${window.location.host}/ws/pong/${this.gameId}/`
    );

    ws.onopen = () => {
      console.log("Connected to game server");
    };

    ws.onmessage = (e) => {
      if (e.data instanceof Blob || e.data instanceof ArrayBuffer) {
        this.handleBinaryMessage(e.data);
      } else {
        this.handleJsonMessage(e.data);
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

  handleJsonMessage(data) {
    try {
      const jsonData = JSON.parse(data);
      console.log(jsonData);
      if (jsonData.status === "player_info") {
        this.setPlayerInfo(jsonData.data);
      } else if (jsonData.status === "game_start") {
        console.log("Game is starting!");
        this.gameOver = false;
        this.gameOverOverlay.classList.add("hidden");
        this.updateMatchInfo();
      } else if (jsonData.status === "game_over") {
        this.handleGameOver(jsonData.winner);
      }
    } catch (e) {
      console.error("Unexpected message from game server:", e);
    }
  }

  handleBinaryMessage(data) {
    if (data instanceof Blob) {
      data.arrayBuffer().then((buffer) => {
        this.decodeGameState(buffer);
        this.drawGame();
      });
    } else if (data instanceof ArrayBuffer) {
      this.decodeGameState(data);
      this.drawGame();
    }
  }

  setPlayerInfo(data) {
    this.currentPlayer = data.currentPlayer;
    this.opponent = data.opponent;
    this.updatePlayerInfo();
  }

  updatePlayerInfo() {
    const leftPlayer = this.querySelector("#leftPlayer");
    const rightPlayer = this.querySelector("#rightPlayer");

    if (this.currentPlayer.role === "player1") {
      leftPlayer.querySelector("h3").textContent = this.currentPlayer.username;
      leftPlayer.querySelector("img").src = this.currentPlayer.avatar;
      rightPlayer.querySelector("h3").textContent = this.opponent.username;
      rightPlayer.querySelector("img").src = this.opponent.avatar;
    } else {
      leftPlayer.querySelector("h3").textContent = this.opponent.username;
      leftPlayer.querySelector("img").src = this.opponent.avatar;
      rightPlayer.querySelector("h3").textContent = this.currentPlayer.username;
      rightPlayer.querySelector("img").src = this.currentPlayer.avatar;
    }
  }

  updateScores() {
    const leftPlayer = this.querySelector("#leftPlayer");
    const rightPlayer = this.querySelector("#rightPlayer");

    if (this.currentPlayer.role === "player1") {
      leftPlayer.querySelector(".score").textContent = this.gameState.score1;
      rightPlayer.querySelector(".score").textContent = this.gameState.score2;
    } else {
      leftPlayer.querySelector(".score").textContent = this.gameState.score2;
      rightPlayer.querySelector(".score").textContent = this.gameState.score1;
    }
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
    this.gameOverOverlay.classList.remove("hidden");
    console.log(message);
    this.gameSocket.close();
  }

  handleUnexpectedDisconnection() {
    this.gameOverMessage.textContent =
      "Connection lost. The game ended unexpectedly.";
    this.gameOverOverlay.classList.remove("hidden");
  }

  startNewGame() {
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
    this.updateScores();
  }

  setPlayerUsername(username) {
    this.playerUsername = username;
    if (this.playerRole === "player1") {
      this.player1.username = username;
    } else {
      this.player2.username = username;
    }
    this.updatePlayerInfo();
  }

  updateMatchInfo() {
    this.querySelector("#currentRound").textContent = "Game";
    this.querySelector("#currentMatch").textContent = `Match ${this.gameId}`;
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
  }
}

customElements.define("game-screen", GameScreen);
