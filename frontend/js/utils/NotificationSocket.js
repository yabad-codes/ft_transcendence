
// Handle websocket connection to notification server
export function connectToNotificationServer() {
    const wss = new WebSocket("wss://" + window.location.host + "/ws/notification/");
    app.socket = wss;
  
    wss.onopen = function () {
      console.log("Connected to notification server");
      wss.send(JSON.stringify({ type: "online_status", status: true}))
    };
  
    wss.onmessage = function (event) {
      const parsedData = JSON.parse(event.data);
      const data = parsedData.message;
      console.log(data);

      if (data.type === "online_status") {
        const chatPage = document.querySelector("chat-page");
        if (chatPage) {
          chatPage.updateOnlineStatusOfFriends(data.username, data.online);
        }
      }
    };
  
    wss.onclose = function () {
      console.log("Disconnected from notification server");
      wss.send(JSON.stringify({ type: "online_status", status: false}))
    };
}
