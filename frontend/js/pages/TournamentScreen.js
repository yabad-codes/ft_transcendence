// TournamentScreen.js
import BaseHTMLElement from "./BaseHTMLElement.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class TournamentScreen extends BaseHTMLElement {
    constructor() {
        super("tournamentscreen");
        this.players = [];
        this.currentRound = 0;
        this.matches = [];
        this.currentMatch = 0;
        this.gameActive = false;
        this.tournamentResults = [];
    }

    connectedCallback() {
        super.connectedCallback();
        this.initializeGame();
    }

    initializeGame() {
        this.canvas = this.querySelector('#game');
        this.context = this.canvas.getContext("2d");
        this.grid = 15;
        this.paddleHeight = this.grid * 5;
        this.maxPaddleY = this.canvas.height - this.grid - this.paddleHeight;

        this.paddleSpeed = 6;
        this.ballSpeed = 5;

        this.leftPaddle = {
            x: this.grid * 2,
            y: this.canvas.height / 2 - this.paddleHeight / 2,
            width: this.grid,
            height: this.paddleHeight,
            dy: 0
        };

        this.rightPaddle = {
            x: this.canvas.width - this.grid * 3,
            y: this.canvas.height / 2 - this.paddleHeight / 2,
            width: this.grid,
            height: this.paddleHeight,
            dy: 0
        };

        this.ball = {
            x: this.canvas.width / 2,
            y: this.canvas.height / 2,
            width: this.grid,
            height: this.grid,
            resetting: false,
            dx: this.ballSpeed,
            dy: -this.ballSpeed
        };

        this.attachEventListeners();
    }

    attachEventListeners() {
        document.addEventListener("keydown", this.handleKeyDown.bind(this));
        document.addEventListener("keyup", this.handleKeyUp.bind(this));
    }

    handleKeyDown(e) {
        if (e.which === 38) {
            this.rightPaddle.dy = -this.paddleSpeed;
        } else if (e.which === 40) {
            this.rightPaddle.dy = this.paddleSpeed;
        }

        if (e.which === 87) {
            this.leftPaddle.dy = -this.paddleSpeed;
        } else if (e.which === 83) {
            this.leftPaddle.dy = this.paddleSpeed;
        }
    }

    handleKeyUp(e) {
        if (e.which === 38 || e.which === 40) {
            this.rightPaddle.dy = 0;
        }

        if (e.which === 83 || e.which === 87) {
            this.leftPaddle.dy = 0;
        }
    }

    startTournament(tournamentData) {
        this.parseTournamentData(tournamentData);
        this.matches = [
            { players: [this.players[0], this.players[1]], score: [0, 0] },
            { players: [this.players[2], this.players[3]], score: [0, 0] }
        ];
        // this.querySelector('#gameContainer').style.display = 'flex';
        this.startNextMatch();
    }

    parseTournamentData(data) {
        this.players = Object.values(data.players).map(player => ({
            username: player.username,
            tournamentName: player.tournament_name,
            avatar: player.avatar
        }));
        this.tournamentId = data.tournament_id;
    }

    startNextMatch() {
        if (this.currentRound === 0 && this.currentMatch < this.matches.length) {
            this.startMatch(
                this.matches[this.currentMatch].players[0],
                this.matches[this.currentMatch].players[1]
            );
        } else if (this.currentRound === 1) {
            const finalists = [
                this.matches[0].score[0] > this.matches[0].score[1]
                    ? this.matches[0].players[0]
                    : this.matches[0].players[1],
                this.matches[1].score[0] > this.matches[1].score[1]
                    ? this.matches[1].players[0]
                    : this.matches[1].players[1]
            ];
            this.matches = [{ players: finalists, score: [0, 0] }];
            this.currentMatch = 0;
            this.startMatch(finalists[0], finalists[1]);
        } else {
            this.endTournament();
        }
    }

    startMatch(player1, player2) {
        this.updateMatchInfo(player1, player2);
        this.resetGame();
        this.gameActive = true;
        setTimeout(() => {
            requestAnimationFrame(this.gameLoop.bind(this));
        }, 3000);
    }

    updateMatchInfo(player1, player2) {
        const roundName = this.currentRound === 0 ? "Semi-final" : "Final";
        this.querySelector('#currentRound').textContent = roundName;
        this.querySelector('#currentMatch').textContent = `Match ${this.currentMatch + 1}`;

        const leftPlayer = this.querySelector('#leftPlayer');
        leftPlayer.querySelector('img').src = player1.avatar;
        leftPlayer.querySelector('h3').textContent = player1.tournamentName;
        leftPlayer.querySelector('.score').textContent = this.matches[this.currentMatch].score[0];

        const rightPlayer = this.querySelector('#rightPlayer');
        rightPlayer.querySelector('img').src = player2.avatar;
        rightPlayer.querySelector('h3').textContent = player2.tournamentName;
        rightPlayer.querySelector('.score').textContent = this.matches[this.currentMatch].score[1];
    }

    resetGame() {
        this.ball.x = this.canvas.width / 2;
        this.ball.y = this.canvas.height / 2;
        this.ball.dx = this.ballSpeed * (Math.random() > 0.5 ? 1 : -1);
        this.ball.dy = this.ballSpeed * (Math.random() > 0.5 ? 1 : -1);
        this.leftPaddle.y = this.canvas.height / 2 - this.paddleHeight / 2;
        this.rightPaddle.y = this.canvas.height / 2 - this.paddleHeight / 2;
    }

    gameLoop() {
        if (!this.gameActive) return;

        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);

        this.leftPaddle.y += this.leftPaddle.dy;
        this.rightPaddle.y += this.rightPaddle.dy;

        if (this.leftPaddle.y < this.grid) {
            this.leftPaddle.y = this.grid;
        } else if (this.leftPaddle.y > this.maxPaddleY) {
            this.leftPaddle.y = this.maxPaddleY;
        }

        if (this.rightPaddle.y < this.grid) {
            this.rightPaddle.y = this.grid;
        } else if (this.rightPaddle.y > this.maxPaddleY) {
            this.rightPaddle.y = this.maxPaddleY;
        }

        this.context.fillStyle = "white";
        this.context.fillRect(
            this.leftPaddle.x,
            this.leftPaddle.y,
            this.leftPaddle.width,
            this.leftPaddle.height
        );
        this.context.fillRect(
            this.rightPaddle.x,
            this.rightPaddle.y,
            this.rightPaddle.width,
            this.rightPaddle.height
        );

        this.ball.x += this.ball.dx;
        this.ball.y += this.ball.dy;

        if (this.ball.y < this.grid) {
            this.ball.y = this.grid;
            this.ball.dy *= -1;
        } else if (this.ball.y + this.grid > this.canvas.height - this.grid) {
            this.ball.y = this.canvas.height - this.grid * 2;
            this.ball.dy *= -1;
        }

        if ((this.ball.x < 0 || this.ball.x > this.canvas.width) && !this.ball.resetting) {
            if (this.ball.x < 0) {
                this.matches[this.currentMatch].score[1]++;
            } else {
                this.matches[this.currentMatch].score[0]++;
            }
            this.updateMatchInfo(
                this.matches[this.currentMatch].players[0],
                this.matches[this.currentMatch].players[1]
            );

            if (Math.max(...this.matches[this.currentMatch].score) >= 5) {
                this.endMatch();
            } else {
                this.ball.resetting = true;
                setTimeout(() => {
                    this.ball.resetting = false;
                    this.resetGame();
                }, 1000);
            }
        }

        if (this.collides(this.ball, this.leftPaddle)) {
            this.ball.dx *= -1;
            this.ball.x = this.leftPaddle.x + this.leftPaddle.width;
        } else if (this.collides(this.ball, this.rightPaddle)) {
            this.ball.dx *= -1;
            this.ball.x = this.rightPaddle.x - this.ball.width;
        }

        this.context.fillRect(this.ball.x, this.ball.y, this.ball.width, this.ball.height);

        this.context.fillStyle = "lightgrey";
        this.context.fillRect(0, 0, this.canvas.width, this.grid);
        this.context.fillRect(0, this.canvas.height - this.grid, this.canvas.width, this.canvas.height);

        for (let i = this.grid; i < this.canvas.height - this.grid; i += this.grid * 2) {
            this.context.fillRect(this.canvas.width / 2 - this.grid / 2, i, this.grid, this.grid);
        }

        requestAnimationFrame(this.gameLoop.bind(this));
    }

    collides(obj1, obj2) {
        return (
            obj1.x < obj2.x + obj2.width &&
            obj1.x + obj1.width > obj2.x &&
            obj1.y < obj2.y + obj2.height &&
            obj1.y + obj1.height > obj2.y
        );
    }

    endMatch() {
        this.gameActive = false;
        const winner =
            this.matches[this.currentMatch].score[0] > this.matches[this.currentMatch].score[1]
                ? this.matches[this.currentMatch].players[0]
                : this.matches[this.currentMatch].players[1];
        this.tournamentResults.push({
            round: this.currentRound === 0 ? "Semi-final" : "Final",
            players: this.matches[this.currentMatch].players,
            score: this.matches[this.currentMatch].score,
            winner: winner
        });

        this.showGameEndPopup(winner);
    }

    endTournament() {
        const winner = this.tournamentResults[this.tournamentResults.length - 1].winner;
        
        // Create and show a popup
        this.showWinnerPopup(winner);
        
        // Dispatch the tournamentEnded event
        this.dispatchEvent(new CustomEvent('tournamentEnded', { detail: { tournamentId: this.tournamentId, winner, results: this.tournamentResults } }));
    }

    showWinnerPopup(winner) {
        // Create the popup element
        const popup = document.createElement('div');
        popup.className = 'winner-popup';
        popup.innerHTML = `
            <div class="popup-content">
                <h2>Tournament Winner!</h2>
                <img src="${winner.avatar}" alt="${winner.tournamentName}" class="winner-avatar">
                <p>${winner.tournamentName} is the champion!</p>
                <button id="closePopup">Close</button>
            </div>
        `;

        // Add styles to the popup
        const style = document.createElement('style');
        style.textContent = `
            .winner-popup {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            .popup-content {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                width: 600px;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .winner-avatar {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                margin: 10px 0;
            }
            #closePopup {
                margin-top: 15px;
                padding: 10px 20px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        `;

        // Append the popup and styles to the document
        document.body.appendChild(style);
        document.body.appendChild(popup);

        // Add event listener to close button
        document.getElementById('closePopup').addEventListener('click', () => {
            document.body.removeChild(popup);
            document.body.removeChild(style);
            // Redirect to home page
            app.router.go('/');
        });
    }

    showGameEndPopup(winner) {
        const popup = document.createElement('div');
        popup.className = 'game-end-popup';
        popup.innerHTML = `
            <div class="popup-content">
                <h2>Game Ended!</h2>
                <img src="${winner.avatar}" alt="${winner.tournamentName}" class="winner-avatar">
                <p>${winner.tournamentName} wins the match!</p>
                <button id="nextButton">Next</button>
            </div>
        `;

        const style = document.createElement('style');
        style.textContent = `
            .game-end-popup {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }
            .popup-content {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                width: 600px;
                height: 400px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .winner-avatar {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                margin: 10px 0;
            }
            #nextButton {
                margin-top: 15px;
                padding: 10px 20px;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        `;

        document.body.appendChild(style);
        document.body.appendChild(popup);

        document.getElementById('nextButton').addEventListener('click', () => {
            document.body.removeChild(popup);
            document.body.removeChild(style);
            
            this.currentMatch++;
            if (this.currentMatch >= this.matches.length) {
                this.currentRound++;
                this.currentMatch = 0;
            }

            this.startNextMatch();
        });
    }
}

customElements.define('tournament-screen', TournamentScreen);