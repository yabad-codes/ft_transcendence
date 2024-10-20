import BaseHTMLElement from "../pages/BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class ChatMessage extends BaseHTMLElement {
  constructor() {
    super("chatmessages");
    const { state, registerUpdate } = createState({
      messages: [],
      newConversation: null,
    });
    this._conversation = { id: 0, IsBlockedByMe: false, IsBlockedByOtherPlayer: false ,player: null };
    this.state = state;
    this.registerUpdate = registerUpdate;
    this.registerLocalFunctions();
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the game page ...
    this.submitMessage();
    const userProfile = this.querySelector(".user_profile_bar");
    userProfile.querySelector(".avatar_image").src =
      this._conversation.player.avatar_url;
    userProfile.querySelector(
      "button > span"
    ).textContent = `${this._conversation.player.first_name} ${this._conversation.player.last_name}`;

    this.handleProfileClick();
    this.handleDropdown();
    this.updateMessageInputUIBasedOnBlockStatus();
    this.updateOnlineStatus(this._conversation.player.online);
  }

  set conversation(conversation) {
    this._conversation = conversation;
    if (conversation.id) {
      this.getMessages(conversation);
    }
  }

  registerLocalFunctions() {
    this.registerUpdate("messages", this.updateUIMessages.bind(this));
    this.registerUpdate("newConversation", this.addNewConversation.bind(this));
  }

  getMessages(conversation) {
    app.api
      .get("/api/conversations/" + conversation.id + "/messages")
      .then((response) => {
        if (response.status >= 400) {
          displayRequestStatus("error", response.data)
          return;
        }
        this.state.messages = response.data;
      })
  }

  updateUIMessages() {
    const messageContainer = this.querySelector(".chat_messages");

    (messageContainer);
    // add new element to the chat message
    if (messageContainer.lastElementChild && this.state.messages.length > 0) {
      const lastMessage = this.state.messages[this.state.messages.length - 1];
      messageContainer.innerHTML += this.createMessageElement(lastMessage);

      return;
    }
    const messageElements = this.state.messages.map((message) => {
      const messageElement = this.createMessageElement(message);
      return messageElement;
    });
    messageContainer.innerHTML = messageElements.join("");
  }

  submitMessage() {
    const submitForm = this.querySelector(".send_message_container");
    submitForm.addEventListener("submit", (event) => {
      event.preventDefault();
      this.createNewMessage();
    });
  }

  createNewMessage() {
    const messageInput = this.querySelector("input[name='message-input']");
    if (!messageInput.value) {
      return;
    }
    (messageInput);
    const message = {
      content: messageInput.value,
    };
    messageInput.value = "";
    if (this._conversation.id === 0) {
      // create a new conversation
      app.api
        .post("/api/conversations/", {
          player2_username: this._conversation.player.username,
        })
        .then((response) => {
          if (response.status >= 400) {
            displayRequestStatus("error", response.data)
            return;
          }
          this._conversation.id = response.data.conversationID;
          this.state.newConversation = response.data;
          this.postNewMessage(message);
        });
      return;
    }
    this.postNewMessage(message);
  }

  postNewMessage(message) {
    app.api
      .post(
        "/api/conversations/" + this._conversation.id + "/messages",
        message
      )
      .then((response) => {
        if (response.status >= 400) {
          displayRequestStatus("error", response.data)
          return;
        }
        this.state.messages = [...this.state.messages, response.data];
        this.moveConversationToTop();
      });
  }

  addNewConversation() {
    const chatPage = document.querySelector("chat-page");
    // update the last message of the conversation
    chatPage.state.conversations = [
      this.state.newConversation,
      ...chatPage.state.conversations,
    ];
    chatPage.openedConversations[this.state.newConversation.conversationID] = true;
    chatPage.prevOpenedConversation = this.state.newConversation.conversationID;
    const conversationBtn = document.querySelector(`[data-conversation-id="${this.state.newConversation.conversationID}"]`);
    conversationBtn.classList.add("active");
  }

  createMessageElement(message) {
    const isCurrentUser = message.sender != app.profile.username;

    return isCurrentUser
      ? `
	<span class="mine_message fw-medium">
		<p
		class="p-3 d-inline-block rounded-top-4 rounded-end-4 me-2"
		>
		${message.content}
		</p>
	</span>
	`
      : `
	<span class="friend_message fw-medium align-self-end">
		<p
		class="p-3 d-inline-block text-light rounded-top-4 rounded-start-4 me-2"
		>
		${message.content}
		</p>
	</span>
	`;
  }

  moveConversationToTop() {
    const conversationContainer = document.querySelector(
      ".direct_message_container"
    );
    const conversationElement = conversationContainer.querySelector(
      `[data-conversation-id="${this._conversation.id}"]`
    );
    const conversationText = conversationElement.querySelector(
      ".direct_message_text"
    );
    conversationText.textContent =
      this.state.messages[this.state.messages.length - 1].content;
    // update the last message of the conversation and move it to the top in the conversation list
    const chatPage = document.querySelector("chat-page");
    const conversationIndex = chatPage.state.conversations.findIndex(
      (conversation) => conversation.conversationID === this._conversation.id
    );
    chatPage.state.conversations[conversationIndex].last_message =
      this.state.messages[this.state.messages.length - 1].content;

    // Remove the conversation from its current position
    const [conversation] = chatPage.state.conversations.splice(
      conversationIndex,
      1
    );

    // Add the conversation to the beginning of the array
    chatPage.state.conversations.unshift(conversation);
    // check if the conversation is already at the top
    if (conversationContainer.firstElementChild === conversationElement) {
      return;
    }
    conversationContainer.removeChild(conversationElement);
    conversationContainer.prepend(conversationElement);
  }

  handleDropdown() {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const clearButton = dropdownMenu.querySelector(".dropdown-item[data-action='clear']");
    const blockButton = dropdownMenu.querySelector(".dropdown-item[data-action='block']");
    const unblockButton = dropdownMenu.querySelector(".dropdown-item[data-action='unblock']");

    // Toggle dropdown menu visibility
    dropdownButton.addEventListener("click", () => {
      dropdownMenu.classList.toggle("show");
      clearButton.style.display = this._conversation.id === 0 ? "none" : "block";
      blockButton.style.display = this._conversation.IsBlockedByMe ? "none" : "block";
      unblockButton.style.display = this._conversation.IsBlockedByMe ? "block" : "none";
    });

    // Close dropdown if clicked outside
    document.addEventListener("click", function (event) {
      if (
        !dropdownButton.contains(event.target) &&
        !dropdownMenu.contains(event.target)
      ) {
        dropdownMenu.classList.remove("show");
      }
    });

    // Add event listeners to each action
    const dropdownItems = dropdownMenu.querySelectorAll(".dropdown-item");
    dropdownItems.forEach((item) => {
      item.addEventListener("click", (event) => {
        event.preventDefault();
        const action = event.target.getAttribute("data-action");
        this.handleDropdownItemAction(action);
        dropdownMenu.classList.remove("show");
      });
    });
  }

  handleDropdownItemAction(action) {
    switch (action) {
      case "game":
        this.requestGameWithUser();
        break;
      case "clear":
        this.clearChatMessages();
        break;
      case "block":
        this.blockUser();
        break;
      case "unblock":
        this.unblockUser();
        break;
      default:
        this.deleteConversation();
    }
  }

  requestGameWithUser() {
    app.api.post("/api/play/request-game-with-player/", { opponent_username: this._conversation.player.username }).then((response) => {
      if (response.status >= 400) {
        displayRequestStatus("error", response.data.message);
        return;
      }
      displayRequestStatus("success", "Game request sent successfully");
    });
  }

  blockUser() {
    app.api.patch("/api/profile/" + this._conversation.player.username + "/block", {});
    this._conversation.IsBlockedByMe = true;
    if (this._conversation.id !== 0) {
      // set the conversation to be blocked
      const chatPage = document.querySelector("chat-page");
      const conversationIndex = chatPage.state.conversations.findIndex(
        (conversation) => conversation.conversationID === this._conversation.id
      );
      chatPage.state.conversations[conversationIndex].IsBlockedByMe = true;
    }


    this.updateMessageInputUIBasedOnBlockStatus();
  }

  unblockUser() {
    app.api.delete("/api/profile/" + this._conversation.player.username + "/unblock");
    this._conversation.IsBlockedByMe = false;
    if (this._conversation.id !== 0) {
      // set the conversation to be unblocked
      const chatPage = document.querySelector("chat-page");
      const conversationIndex = chatPage.state.conversations.findIndex((conversation) => conversation.conversationID === this._conversation.id);
      chatPage.state.conversations[conversationIndex].IsBlockedByMe = false;
    }
    this.updateMessageInputUIBasedOnBlockStatus();
  }

  handleProfileClick() {
    const userProfile = this.querySelector(".user_profile_bar");
    const userProfileBtn = userProfile.querySelector("button");
    userProfileBtn.addEventListener("click", () => {
      app.router.go(`/profile/${this._conversation.player.username}`);
    });
  }

  updateMessageInputUIBasedOnBlockStatus() {
    const messageInputContainer = this.querySelector(".send_message_container");
    const messageInputContainerParent = messageInputContainer.parentElement;
    const blockMessage = messageInputContainerParent.querySelector("p");
    const userProfile = this.querySelector(".user_profile_bar");
    const userProfileBtn = userProfile.querySelector("button");

    if (this._conversation.IsBlockedByMe) {
      messageInputContainer.style.display = "none";
      blockMessage.style.display = "block";
      blockMessage.textContent = "You have blocked this user, you can't send messages.";
      userProfileBtn.disabled = true;
    }
    else if (this._conversation.IsBlockedByOtherPlayer) {
      messageInputContainer.style.display = "none";
      blockMessage.style.display = "block";
      blockMessage.textContent = "This user has blocked you, you can't send messages.";
      userProfileBtn.disabled = true;
    }
    else {
      messageInputContainer.style.display = "flex";
      blockMessage.style.display = "none";
      userProfileBtn.disabled = false
    }
  }

  clearChatMessages() {
    app.api.post("/api/conversations/" + this._conversation.id + "/clear", {});
    this.state.messages = [];

    // update the last message of the conversation
    const chatPage = document.querySelector("chat-page");
    const conversationContainer = document.querySelector(
      ".direct_message_container"
    );
    const conversationElement = conversationContainer.querySelector(
      `[data-conversation-id="${this._conversation.id}"]`
    );
    conversationElement.querySelector(".direct_message_text").textContent = "";
    const conversationIndex = chatPage.state.conversations.findIndex(
      (conversation) => conversation.conversationID === this._conversation.id
    );
    chatPage.state.conversations[conversationIndex].last_message = "";
  }

  deleteConversation() {
    if (this._conversation.id === 0) {
      this.parentElement.removeChild(this);
      return;
    }
    app.api.post("/api/conversations/" + this._conversation.id + "/delete", {});
    const chatPage = document.querySelector("chat-page");
    const conversationContainer = document.querySelector(
      ".direct_message_container"
    );
    const conversationElement = conversationContainer.querySelector(
      `[data-conversation-id="${this._conversation.id}"]`
    );
    conversationContainer.removeChild(conversationElement);
    const conversationIndex = chatPage.state.conversations.findIndex(
      (conversation) => conversation.conversationID === this._conversation.id
    );
    chatPage.state.conversations.splice(conversationIndex, 1);
    // remove the opened conversation from the object
    chatPage.prevOpenedConversations = null;
    delete chatPage.openedConversations[this._conversation.id];

    // remove the current parent element
    this.parentElement.removeChild(this);
  }

  updateOnlineStatus(status) {
    const avatar = this.querySelector(".avatar");
    const avatar_status = avatar.querySelector(".avatar_status");

    if (!this._conversation.player.isFriend) {
      avatar_status.style.display = "none";
    }
    avatar_status.classList.toggle("online", status);
  }
}

customElements.define("chat-message", ChatMessage);
