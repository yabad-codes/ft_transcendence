import BaseHTMLElement from "./BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";

export class ChatPage extends BaseHTMLElement {
  constructor() {
    super("chatpage");
    const { state, registerUpdate } = createState({
      conversations: [],
      searchConversations: [],
      friends: [],
      searchFriends: [],
    });

    this.state = state;
    this.chatSocket = null;
    this.openedConversations = {};
    this.prevOpenedConversation = null;
    this.registerUpdate = registerUpdate;
    this.registerLocalFunctions();
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the chat page ...
    app.api.get("/api/conversations/").then((conversations) => {
      this.state.conversations = conversations;
    });
    this.popupConversationActions();
    this.searchFriends();
    this.searchConversations();
    this.setupWebsocket();
  }

  setupWebsocket() {
    this.chatSocket = new WebSocket(
      "ws://" + window.location.host + "/ws/chat/"
    );

    this.chatSocket.onopen = (e) => {
      console.log("Chat socket open");
    };

    this.chatSocket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log(`Data: ${data}`);
      const conversation = this.state.conversations.find(
        (conversation) =>
          conversation.conversationID === data.message.conversation_id
      );
      if (!conversation) {
        // retrieve the conversation from the server and update the state
        app.api
          .get("/api/conversations/" + data.message.conversation_id)
          .then((response) => {
            this.state.conversations = [response, ...this.state.conversations];
          });
        return;
      }
      this.moveConversationToTop(data.message.conversation_id, data.message.data);
      // If the conversation is opened then add the message to the chat message
      if (this.openedConversations[data.message.conversation_id]) {
        const chatMessage = this.querySelector("chat-message");
        chatMessage.state.messages = [
          ...chatMessage.state.messages,
          data.message.data,
        ];
        // mark message as read if the conversation is opened
        app.api.patch("/api/conversations/" + conversation.conversationID + "/messages/" + data.message.data.messageID + "/mark_as_read/")
        return;
      }
      // If the conversation is not opened then add a notification
      this.notificationConversationMonitor(data.message.conversation_id);
    };

    this.chatSocket.onclose = (e) => {
      // reconnect the websocket if the parent page is still open
      if (!this.isDisconnected) {
        console.log("Reconnecting chat socket...");
        this.setupWebsocket();
        return;
      }
      console.error("Chat socket closed unexpectedly");
    };
  }

  notificationConversationMonitor(conversation_id, isOpened = false) {
    const conversationContainer = this.querySelector(
      ".direct_message_container"
    );
    const conversationElement = conversationContainer.querySelector(
      `[data-conversation-id="${conversation_id}"]`
    );
    const notificationElement = conversationElement.querySelector(
      ".direct_message_notification_icon"
    );
    notificationElement.classList.toggle("style", !isOpened);
    notificationElement.textContent = isOpened
      ? ""
      : parseInt(notificationElement.textContent ? notificationElement.textContent : "0") + 1;
  }

  moveConversationToTop(conversation_id, message) {
    const conversationContainer = this.querySelector(
      ".direct_message_container"
    );
    const conversationElement = conversationContainer.querySelector(
      `[data-conversation-id="${conversation_id}"]`
    );
    const conversationText = conversationElement.querySelector(
      ".direct_message_text"
    );
    conversationText.textContent =
      message.content;
    // update the last message of the conversation and move it to the top in the conversation list
    const conversationIndex = this.state.conversations.findIndex(
      (conversation) => conversation.conversationID === conversation_id
    );
    this.state.conversations[conversationIndex].last_message =
      message.content;

    // Remove the conversation from its current position
    const [conversation] = this.state.conversations.splice(
      conversationIndex,
      1
    );

    // Add the conversation to the beginning of the array
    this.state.conversations.unshift(conversation);
    // check if the conversation is already at the top
    if (conversationContainer.firstElementChild === conversationElement) {
      return;
    }
    conversationContainer.removeChild(conversationElement);
    conversationContainer.prepend(conversationElement);
  }

  registerLocalFunctions() {
    this.registerUpdate("conversations", this.updateUIConversations.bind(this));
    this.registerUpdate(
      "searchConversations",
      this.updateUIConversations.bind(this)
    );
    this.registerUpdate("searchFriends", this.updateUIfriends.bind(this));
  }

  setConversationsActions() {
    const conversationButtons = this.querySelectorAll(".direct_message_btn");

    conversationButtons.forEach((button, index) => {
      const conversationID = button.getAttribute("data-conversation-id");
      this.openedConversations[conversationID] = false;
      button.addEventListener("click", (event) => {
        if (this.openedConversations[conversationID]) {
          return;
        }
        if (this.prevOpenedConversation) {
          const prevConversationBtn = this.querySelector(`.direct_message_btn[data-conversation-id='${this.prevOpenedConversation}']`);
          prevConversationBtn.classList.remove("active");
          this.openedConversations[this.prevOpenedConversation] = false;
        }

        this.prevOpenedConversation = conversationID;
        this.openedConversations[conversationID] = true;

        // add style to the selected conversation
        button.classList.add("active");
        this.openConversationEvent(index);
        this.notificationConversationMonitor(conversationID, true);
      });
    });
  }

  openConversationEvent(index) {
    const chatContainer = this.querySelector(".chat_message_container");
    const chatMessageElement = document.createElement("chat-message");

    const currentConversation = this.state.conversations[index];
    chatMessageElement.conversation = {
      id: currentConversation.conversationID,
      player: this.choosePlayerConversation(currentConversation),
    };
    if (chatContainer.lastElementChild.nodeName === "CHAT-MESSAGE") {
      chatContainer.removeChild(chatContainer.lastElementChild);
    }
    chatContainer.appendChild(chatMessageElement);
  }

  popupConversationActions() {
    const popupContainer = this.querySelector(".popup-container");
    this.querySelector(".add-conversation-btn").addEventListener(
      "click",
      (event) => {
        popupContainer.classList.remove("hidden");
        app.api.get("/api/friendships/").then((friends) => {
          this.state.friends = friends;
          this.state.searchFriends = friends;
        });
      }
    );

    popupContainer.addEventListener("click", (event) => {
      event.target.classList.add("hidden");
      const searchInput = this.querySelector(
        "input[name='popup-search-players']"
      );
      searchInput.value = "";
    });
  }

  updateUIfriends() {
    const popupFriends = this.querySelector(".popup-friends");
    const popupBtns = this.state.searchFriends.map((friend) => {
      const player = this.choosePlayerFriend(friend);
      return `
      <button
      class="popup-btn w-100 border border-secondary-subtle border-top-0 border-end-0 border-start-0 text-start ps-4 pt-2 pb-2"
    >
      <div class="avatar me-2">
        <img
          class="avatar_image shadow-sm"
          src="${player.avatar}"
          alt="Avatar image"
        />
        <span class="avatar_status"></span>
      </div>
      ${player.first_name} ${player.last_name}
    </button>
      `;
    });
    popupFriends.innerHTML = popupBtns.join("");
    this.addNewConversationFromPopup();
  }

  addNewConversationFromPopup() {
    const popupBtns = this.querySelectorAll(".popup-btn");
    popupBtns.forEach((button, index) => {
      button.addEventListener("click", (event) => {
        const popupContainer = this.querySelector(".popup-container");
        const player = this.choosePlayerFriend(this.state.searchFriends[index]);

        this.createTemporayConversation(player);
        popupContainer.classList.add("hidden");
        const searchInput = this.querySelector(
          "input[name='popup-search-players']"
        );
        searchInput.value = "";
      });
    });
  }

  // create a temporary conversation with the player but not saved in the database
  createTemporayConversation(player) {
    // search the player in the conversation
    const existConversation = this.state.conversations.find(
      (conversation) =>
        conversation.player1.username === player.username ||
        conversation.player2.username === player.username
    );
    if (existConversation) {
      // if the conversation already exists, open it
      const conversationBtn = this.querySelector(
        "button[data-conversation-id='" +
          existConversation.conversationID +
          "']"
      );
      conversationBtn.click();
    } else {
      const chatMessage = document.createElement("chat-message");
      const chatContainer = this.querySelector(".chat_message_container");
      if (chatContainer.lastElementChild.nodeName === "CHAT-MESSAGE") {
        if (chatContainer.lastElementChild._conversation.id === 0) {
          return;
        }
        chatContainer.removeChild(chatContainer.lastElementChild);
      }
      chatMessage.conversation = {
        id: 0,
        player: player,
      };
      chatContainer.appendChild(chatMessage);
    }
  }

  // app.route.go(chat) ==> select the chat-page element
  searchConversations() {
    const searchInput = this.querySelector(
      "input[name='search-conversations']"
    );
    searchInput.addEventListener("input", (event) => {
      const searchValue = event.target.value;
      if (searchValue === "") {
        this.state.searchConversations = [];
        return;
      }
      this.state.searchConversations = this.state.conversations.filter(
        (conversation) => {
          const player = this.choosePlayerConversation(conversation);
          return (
            player.first_name
              .toLowerCase()
              .includes(searchValue.toLowerCase()) ||
            player.last_name.toLowerCase().includes(searchValue.toLowerCase())
          );
        }
      );
    });
  }

  searchFriends() {
    const searchInput = this.querySelector(
      "input[name='popup-search-players']"
    );
    searchInput.addEventListener("input", (event) => {
      const searchValue = event.target.value;
      this.state.searchFriends = this.state.friends.filter((friend) => {
        const player = this.choosePlayerFriend(friend);
        return (
          player.first_name.toLowerCase().includes(searchValue.toLowerCase()) ||
          player.last_name.toLowerCase().includes(searchValue.toLowerCase())
        );
      });
    });
  }

  updateUIConversations() {
    const conversationContainer = this.querySelector(
      ".direct_message_container"
    );

    const conversationsToDisplay =
      this.state.searchConversations.length > 0
        ? this.state.searchConversations
        : this.state.conversations;

    const conversationElements = conversationsToDisplay.map((conversation) => {
      const conversationElement = this.createConversationElement(conversation);
      return conversationElement;
    });
    conversationContainer.innerHTML = conversationElements.join("");
    this.setConversationsActions();
  }

  createConversationElement(conversation) {
    const conversationParticipant = this.choosePlayerConversation(conversation);
    const unread_messages_count = conversation.unread_messages_count;
    return `
    <button
        class="direct_message_btn border-0 w-100 p-3 rounded-pill d-inline-flex mb-2"
        data-conversation-id="${conversation.conversationID}"
    >
        <div class="avatar me-2">
        <img
            class="avatar_image"
            src="${conversationParticipant.avatar}"
            alt="Avatar image"
        />
        <span class="avatar_status"></span>
        </div>
        <div
        class="flex-grow-1 d-flex flex-column justify-content-between position-relative"
        style="height: 60px"
        >
        <h6 class="text-start m-0">${conversationParticipant.first_name} ${
      conversationParticipant.last_name
    }</h6>
        <p class="direct_message_text text-start m-0">
            ${
              conversation.last_message != null ? conversation.last_message : ""
            }
        </p>
        <span
            class="direct_message_notification_icon position-absolute top-0 end-0 border border-light badge rounded-circle d-flex justify-content-center align-items-center ${
              unread_messages_count > 0 ? "style" : ""
            }"
            >${unread_messages_count > 0 ? unread_messages_count : ""}</span
        >
        </div>
    </button>
    `;
  }

  choosePlayerConversation(conversation) {
    if (conversation.player1.username == app.profile.username) {
      return conversation.player2;
    } else {
      return conversation.player1;
    }
  }

  choosePlayerFriend(friend) {
    if (friend.player1.username == app.profile.username) {
      return friend.player2;
    } else {
      return friend.player1;
    }
  }

}

customElements.define("chat-page", ChatPage);
