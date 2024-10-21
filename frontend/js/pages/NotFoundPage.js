import BaseHTMLElement from "./BaseHTMLElement.js"

export class NotFoundPage extends BaseHTMLElement {
    constructor() {
        super('notfoundpage')
    }

    connectedCallback() {
        super.connectedCallback()
        this.render()
        this.setupPongGame()
    }

    render() {
        this.innerHTML = `
            <style>
                .page-404 {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    font-family: 'Arial', sans-serif;
                }
                .logo-404 {
                    width: 300px;
                    height: auto;
                    margin-bottom: 20px;
                }
                .title-404 {
                    font-size: 4em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
					margin-top: 0;
                }
                .message-404 {
                    font-size: 1.2em;
                    margin-bottom: 20px;
                    text-align: center;
                    max-width: 80%;
                }
                .game-container-404 {
                    background-color: #16213e;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.3);
                }
                .canvas-404 {
                    border: 2px solid #0f3460;
                    background-color: #0f3460;
                    border-radius: 5px;
                }
            </style>
            <div class="page-404">
                <img src="/images/pong-light.svg" alt="Pong Logo" class="logo-404">
                <h1 class="title-404">404</h1>
                <p class="message-404">Oops! The page you're looking for seems to have bounced away.</p>
                <p class="message-404">Why not play a quick game of Pong while you're here?</p>
                <div class="game-container-404">
                    <canvas id="pongCanvas-404" class="canvas-404" width="400" height="200"></canvas>
                </div>
            </div>
        `
    }

    setupPongGame() {
        const canvas = this.querySelector('#pongCanvas-404')
        const ctx = canvas.getContext('2d')

        // Pong game variables
        let ballX = canvas.width / 2
        let ballY = canvas.height / 2
        let ballSpeedX = 3
        let ballSpeedY = 3
        const paddleHeight = 50
        const paddleWidth = 10
        let leftPaddleY = canvas.height / 2 - paddleHeight / 2
        let rightPaddleY = canvas.height / 2 - paddleHeight / 2
        const paddleSpeed = 4

        function gameLoop() {
            // Move the ball
            ballX += ballSpeedX
            ballY += ballSpeedY

            // Ball collision with top and bottom walls
            if (ballY < 0 || ballY > canvas.height) {
                ballSpeedY = -ballSpeedY
            }

            // Ball collision with paddles
            if (
                (ballX < paddleWidth && ballY > leftPaddleY && ballY < leftPaddleY + paddleHeight) ||
                (ballX > canvas.width - paddleWidth && ballY > rightPaddleY && ballY < rightPaddleY + paddleHeight)
            ) {
                ballSpeedX = -ballSpeedX
            }

            // Ball out of bounds
            if (ballX < 0 || ballX > canvas.width) {
                ballX = canvas.width / 2
                ballY = canvas.height / 2
            }

            // Move AI paddle
            const paddleCenter = rightPaddleY + paddleHeight / 2
            if (ballY < paddleCenter - 10) {
                rightPaddleY -= paddleSpeed
            } else if (ballY > paddleCenter + 10) {
                rightPaddleY += paddleSpeed
            }

            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height)

            // Draw paddles
            ctx.fillStyle = '#e94560'
            ctx.fillRect(0, leftPaddleY, paddleWidth, paddleHeight)
            ctx.fillRect(canvas.width - paddleWidth, rightPaddleY, paddleWidth, paddleHeight)

            // Draw ball
            ctx.beginPath()
            ctx.arc(ballX, ballY, 5, 0, Math.PI * 2)
            ctx.fillStyle = '#ffffff'
            ctx.fill()

            requestAnimationFrame(gameLoop)
        }

        // Start the game loop
        gameLoop()

        // Handle user input
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect()
            const mouseY = e.clientY - rect.top
            leftPaddleY = mouseY - paddleHeight / 2
            
            // Keep paddle within canvas bounds
            leftPaddleY = Math.max(0, Math.min(canvas.height - paddleHeight, leftPaddleY))
        })
    }
}

customElements.define('not-found-page', NotFoundPage)
