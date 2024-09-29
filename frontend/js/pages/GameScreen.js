import BaseHTMLElement from "./BaseHTMLElement.js";

export class GameScreen extends BaseHTMLElement {
  constructor() {
    super();
    this.gameId = null;
    this.ballDirectionX = 1;
    this.ballDirectionY = 1;
    this.ballSpeed = 2;
    this.player1Score = 0;
    this.player2Score = 0;
  }

  connectedCallback() {
    const gameIdElement = this.querySelector("#gameId");
    this.gameId = this.getAttribute("gameId");
    gameIdElement.textContent = this.gameId;

    this.initGame();
    this.startGame();
  }

  initGame() {
    this.gameBoard = this.querySelector(".game-board");
    this.ball = this.querySelector(".ball");
    this.paddle1 = this.querySelector(".player1-paddle");
    this.paddle2 = this.querySelector(".player2-paddle");
    this.player1ScoreElement = this.querySelector("#player1-score");
    this.player2ScoreElement = this.querySelector("#player2-score");

    // Set initial scores
    this.updateScores();

    // Place ball in center
    this.resetBall();

    // Set paddle positions
    this.paddle1.style.top = "50%";
    this.paddle2.style.top = "50%";

    // Add keyboard event listeners for paddle movement
    document.addEventListener("keydown", (e) => this.handlePaddleMove(e));
  }

  resetBall() {
    this.ball.style.left = "50%";
    this.ball.style.top = "50%";
    this.ballDirectionX = Math.random() > 0.5 ? 1 : -1;
    this.ballDirectionY = Math.random() > 0.5 ? 1 : -1;
  }

  startGame() {
    const gameLoop = () => {
      this.moveBall();
      requestAnimationFrame(gameLoop);
    };
    gameLoop();
  }

  moveBall() {
    const ballRect = this.ball.getBoundingClientRect();
    const boardRect = this.gameBoard.getBoundingClientRect();

    // Move ball based on direction
    let newX =
      ballRect.left + this.ballDirectionX * this.ballSpeed - boardRect.left;
    let newY =
      ballRect.top + this.ballDirectionY * this.ballSpeed - boardRect.top;

    // Check for collision with top/bottom walls
    if (newY <= 0 || newY >= boardRect.height - ballRect.height) {
      this.ballDirectionY *= -1;
    }

    // Check for collision with paddles
    const paddle1Rect = this.paddle1.getBoundingClientRect();
    const paddle2Rect = this.paddle2.getBoundingClientRect();

    if (
      (newX <= paddle1Rect.width &&
        newY + ballRect.height >= paddle1Rect.top - boardRect.top &&
        newY <= paddle1Rect.bottom - boardRect.top) ||
      (newX + ballRect.width >= boardRect.width - paddle2Rect.width &&
        newY + ballRect.height >= paddle2Rect.top - boardRect.top &&
        newY <= paddle2Rect.bottom - boardRect.top)
    ) {
      this.ballDirectionX *= -1;
    }

    // Check if ball goes out of bounds (left or right)
    if (newX <= 0) {
      this.player2Score++;
      this.updateScores();
      this.resetBall();
    } else if (newX + ballRect.width >= boardRect.width) {
      this.player1Score++;
      this.updateScores();
      this.resetBall();
    }

    // Update ball position
    this.ball.style.left = `${newX}px`;
    this.ball.style.top = `${newY}px`;
  }

  handlePaddleMove(e) {
    const step = 20;
    const boardRect = this.gameBoard.getBoundingClientRect();

    if (e.key === "w" || e.key === "s") {
      const paddle1Rect = this.paddle1.getBoundingClientRect();
      let newTop = paddle1Rect.top - boardRect.top;

      if (e.key === "w" && newTop > 0) {
        newTop -= step;
      } else if (
        e.key === "s" &&
        newTop < boardRect.height - paddle1Rect.height
      ) {
        newTop += step;
      }

      this.paddle1.style.top = `${newTop}px`;
    } else if (e.key === "ArrowUp" || e.key === "ArrowDown") {
      const paddle2Rect = this.paddle2.getBoundingClientRect();
      let newTop = paddle2Rect.top - boardRect.top;

      if (e.key === "ArrowUp" && newTop > 0) {
        newTop -= step;
      } else if (
        e.key === "ArrowDown" &&
        newTop < boardRect.height - paddle2Rect.height
      ) {
        newTop += step;
      }

      this.paddle2.style.top = `${newTop}px`;
    }
  }

  updateScores() {
    this.player1ScoreElement.textContent = this.player1Score;
    this.player2ScoreElement.textContent = this.player2Score;
  }
}

customElements.define("game-screen", GameScreen);
