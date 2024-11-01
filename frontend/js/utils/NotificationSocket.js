import { GameRequestPopup } from "../utils/PlayerGameRequest.js";
import { displayRequestStatus } from "./errorManagement.js";

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
        if (data.game_id === null) {
          displayRequestStatus("error", "Game request declined successfully");
          return;
        }
        app.router.removeOldPages();
        app.router.insertPage("game-screen");
        const gameScreen = document.querySelector("game-screen");
        gameScreen._setGameId = data.game_id;
      }

      if (data.type === "tournament_request") {
        displayRequestStatus("success", `${data.message} from ${data.requester}!`);
      }
    };

    wss.onclose = function () {
      console.log("Disconnected from notification server");
    };
}
