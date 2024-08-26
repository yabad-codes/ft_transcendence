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
    this.registerUpdate = registerUpdate;
    this.registerLocalFunctions();
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the chat page ...
    app.api.get("/api/conversations").then((conversations) => {
      this.state.conversations = conversations;
    });
    this.popupConversationActions();
    this.searchFriends();
    this.searchConversations();
  }

  registerLocalFunctions() {
    this.registerUpdate("conversations", this.updateUIConversations.bind(this));
    this.registerUpdate("searchConversations", this.updateUIConversations.bind(this));
    this.registerUpdate("searchFriends", this.updateUIfriends.bind(this));
  }

  conversationActions() {
    const messageButtons = this.querySelectorAll(".direct_message_btn");

    messageButtons.forEach((button, index) => {
      button.addEventListener("click", (event) => {
        this.openConversationEvent(index);
      });
    });
  }

  openConversationEvent(index) {
    const chatMessageElement = document.createElement("chat-message");
    const chatContainer = this.querySelector(".chat_message_container");
    if (chatContainer.lastElementChild.nodeName === "CHAT-MESSAGE") {
      if (
        chatContainer.lastElementChild._conversation.id ===
        this.state.conversations[index].conversationID
      ) {
        return;
      }
      chatContainer.removeChild(chatContainer.lastElementChild);
    }
    const currentConversation = this.state.conversations[index];
    chatMessageElement.conversation = {
      id: currentConversation.conversationID,
      player: this.choosePlayerConversation(currentConversation),
    };
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
          // if the conversation does not exist, open a temporary conversation
          // app.api
          //   .post("/api/conversations/", {
          //     player2_username: player.username,
          //   })
          //   .then((response) => {
          //     this.state.conversations = [
          //       response,
          //       ...this.state.conversations,
          //     ];
          //     this.openConversationEvent(0);
          //     const conversationBtn = this.querySelector(
          //       "button[data-conversation-id='" + response.conversationID + "']"
          //     );
          //     conversationBtn.click();
          //   });
          const chatMessage = document.createElement("chat-message");
          const chatContainer = this.querySelector(".chat_message_container");
          if (chatContainer.lastElementChild.nodeName === "CHAT-MESSAGE") {
            if (
              chatContainer.lastElementChild._conversation.id === 0
            ) {
              popupContainer.classList.add("hidden");
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

        popupContainer.classList.add("hidden");
        const searchInput = this.querySelector(
          "input[name='popup-search-players']"
        );
        searchInput.value = "";
      });
    });
  }

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

    const conversationsToDisplay = this.state.searchConversations.length > 0 
    ? this.state.searchConversations 
    : this.state.conversations;

    const conversationElements = conversationsToDisplay.map((conversation) => {
      const conversationElement = this.createConversationElement(conversation);
      return conversationElement;
    });
    conversationContainer.innerHTML = conversationElements.join("");
    this.conversationActions();
  }

  createConversationElement(conversation) {
    const conversationParticipant = this.choosePlayerConversation(conversation);
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
        <h6 class="text-start m-0">${conversationParticipant.first_name} ${conversationParticipant.last_name}</h6>
        <p class="direct_message_text text-start m-0">
            ${conversation.last_message}
        </p>
        <span
            class="direct_message_notification_icon position-absolute top-0 end-0 border border-light badge rounded-circle d-flex justify-content-center align-items-center"
            >2</span
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
