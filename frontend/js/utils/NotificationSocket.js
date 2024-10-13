import { GameRequestPopup } from "../utils/PlayerGameRequest.js";

// Handle websocket connection to notification server
export function connectToNotificationServer() {
    const wss = new WebSocket("wss://" + window.location.host + "/ws/notification/");
    app.socket = wss;
  
    wss.onopen = function () {
      console.log("Connected to notification server");
    };
  
    wss.onmessage = function (event) {
      const parsedData = JSON.parse(event.data);
      const data = parsedData.message;
      console.log(data);

      /* Handle different types of notifications */

      // Update online status of friends
      if (data.type === "online_status") {
        const chatPage = document.querySelector("chat-page");
        if (chatPage) {
          chatPage.updateOnlineStatusOfFriends(data.username, data.online);
        }
      }

      // Show game request popup
      if (data.type === "game_request") {
        GameRequestPopup.show({requesterName: data.requester_name, avatarUrl: data.avatar_url, requestId: data.request_id});
      }

      // Redirect to game screen
      if (data.type === "game_request_response") {
        const gameScreen = document.createElement("game-screen");
        gameScreen.gameId = data.game_id;
        document.body.innerHTML = "";
        document.body.appendChild(gameScreen);
      }
    };

    wss.onclose = function () {
      console.log("Disconnected from notification server");
    };
}
