import { GameScreen } from "../pages/GameScreen.js";
import { displayRequestStatus } from "./errorManagement.js";

export const GameRequestPopup = (function() {
    const popup = document.getElementById('gameRequestPopup');
    const requestMessage = document.getElementById('requestMessage');
    const timeProgress = document.getElementById('timeProgress');
    const timeLeft = document.getElementById('timeLeft');
    const declineBtn = document.getElementById('declineBtn');
    const acceptBtn = document.getElementById('acceptBtn');
    const avatarImg = document.getElementById('avatarImg');

    let timer;
    let seconds = 10;
    let currentRequestData = null;

    function showPopup(requestData) {
        currentRequestData = requestData;
        requestMessage.textContent = `${requestData.requesterName} has requested a game with you.`;
        avatarImg.src = requestData.avatarUrl;
        popup.style.display = 'block';
        startTimer();
    }

    function hidePopup() {
        popup.style.display = 'none';
        clearInterval(timer);
        seconds = 10;
        currentRequestData = null;
    }

    function startTimer() {
        updateTimer();
        timer = setInterval(() => {
            seconds--;
            updateTimer();
            if (seconds === 0) {
                clearInterval(timer);
                onDecline();
            }
        }, 1000);
    }

    function updateTimer() {
        timeLeft.textContent = `${seconds} seconds left`;
        timeProgress.style.width = `${(seconds / 10) * 100}%`;
    }

    function onAccept() {
        app.api.post('/api/play/accept-game-request/', {request_id: currentRequestData.requestId})
            .then((response) => {
                
                if (response.status >= 400) {
                    displayRequestStatus("error", response.data.message);
                    return;
                }
                hidePopup();
                const gameScreen = new GameScreen();
                gameScreen.gameId = response.data.game_id;
                document.body.innerHTML = "";
                document.body.appendChild(gameScreen);
            })
            .catch((error) => {
                console.error(error);
            });
        hidePopup();
    }

    function onDecline() {
        app.api.post('/api/play/reject-game-request/', {request_id: currentRequestData.requestId});
        hidePopup();
    }

    declineBtn.addEventListener('click', onDecline);
    acceptBtn.addEventListener('click', onAccept);

    return {
        show: showPopup,
    };
})();
