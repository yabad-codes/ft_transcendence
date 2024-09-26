import BaseHTMLElement from "./BaseHTMLElement.js";

export class GameScreen extends BaseHTMLElement {
  constructor() {
    super();
    this.gameId = null;
    this.gameSocket = null;
    this.gameState = null;
    this.playerRole = null;
    this.paddle1 = null;
    this.paddle2 = null;
    this.ball = null;
    this.board = null;
    console.log("GameScreen constructor");
  }

  connectedCallback() {
    console.log("GameScreen connectedCallback");
    this.render();
    this.initializeGame();
  }

  render() {
    this.innerHTML = `
      <div class="game-board">
        <div class="paddle player1-paddle" id="paddle1"></div>
        <div class="paddle player2-paddle" id="paddle2"></div>
        <div class="ball" id="ball"></div>
      </div>
    `;
  }

  initializeGame() {
    this.board = this.querySelector(".game-board");
    this.paddle1 = document.getElementById("paddle1");
    this.paddle2 = document.getElementById("paddle2");
    this.ball = document.getElementById("ball");

    this.initializePaddlePositions();
    this.initializeBallPosition();
    this.connectToGameServer();
    this.addEventListeners();
  }

  getTopPosition(paddle) {
    return parseFloat(paddle.style.top) || 0;
  }

  movePaddle(paddle, direction) {
    const step = 10; // pixels to move the paddle
    const currentTop = this.getTopPosition(paddle);
    const boardHeight = this.board.clientHeight;
    const paddleHeight = paddle.clientHeight;

    let newTop = currentTop + direction * step;

    // Ensure the paddle stays within the game board
    newTop = Math.max(0, Math.min(newTop, boardHeight - paddleHeight));

    this.setPaddlePosition(paddle, newTop);
  }

  initializePaddlePositions() {
    const boardHeight = this.board.clientHeight;
    const paddleHeight = this.paddle1.clientHeight;
    const initialTop = (boardHeight - paddleHeight) / 2;
    console.log(initialTop);

    this.setPaddlePosition(this.paddle1, initialTop);
    this.setPaddlePosition(this.paddle2, initialTop);
  }

  setPaddlePosition(paddle, y) {
    paddle.style.top = `${y}px`;
  }

  initializeBallPosition() {
    const boardWidth = this.board.clientWidth;
    const boardHeight = this.board.clientHeight;
    const ballSize = this.ball.clientWidth;
    const ballX = (boardWidth - ballSize) / 2;
    const ballY = (boardHeight - ballSize) / 2;

    this.setBallPosition(ballX, ballY);
  }

  setBallPosition(x, y) {
    this.ball.style.left = `${x}px`;
    this.ball.style.top = `${y}px`;
  }

  addEventListeners() {
    document.addEventListener("keydown", this.handleKeyDown.bind(this));
  }

  handleKeyDown(e) {
    switch (e.key) {
      case "w":
      case "s":
        if (this.playerRole === "player1") {
          this.handlePaddleMove(e.key, this.paddle1);
        } else if (this.playerRole === "player2") {
          this.handlePaddleMove(e.key, this.paddle2);
        }
        break;
    }
  }

  handlePaddleMove(key, paddle) {
    switch (key) {
      case "w":
        this.movePaddle(paddle, -1);
        break;
      case "s":
        this.movePaddle(paddle, 1);
        break;
    }
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
          console.log(this.gameState);
          this.updateGame();
        });
      } else if (e.data instanceof ArrayBuffer) {
        this.decodeGameState(e.data);
        console.log(this.gameState);
      } else {
        try {
          const jsonData = JSON.parse(e.data);
          if (jsonData.status === "player-role") {
            this.setPlayerRole(jsonData.role);
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

  updateGame() {
    this.setBallPosition(this.gameState.ballX, this.gameState.ballY);
    this.setPaddlePosition(this.paddle1, this.gameState.player1Y);
    this.setPaddlePosition(this.paddle2, this.gameState.player2Y);
  }

  setPlayerRole(role) {
    this.playerRole = role;
  }
}

customElements.define("game-screen", GameScreen);
