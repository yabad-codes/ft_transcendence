import BaseHTMLElement from "../pages/BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";

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
      "span > span"
    ).textContent = `${this._conversation.player.first_name} ${this._conversation.player.last_name}`;

    this.handleDropdown();
    this.updateMessageInputUIBasedOnBlockStatus();
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
      .then((messages) => {
        this.state.messages = messages;
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
          this._conversation.id = response.conversationID;
          this.state.newConversation = response;
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
        this.state.messages = [...this.state.messages, response];
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

  updateMessageInputUIBasedOnBlockStatus() {
    const messageInputContainer = this.querySelector(".send_message_container");
    const messageInputContainerParent = messageInputContainer.parentElement;
    const blockMessage = messageInputContainerParent.querySelector("p");

    if (this._conversation.IsBlockedByMe) {
      messageInputContainer.style.display = "none";
      blockMessage.style.display = "block";
      blockMessage.textContent = "You have blocked this user, you can't send messages.";
    }
    else if (this._conversation.IsBlockedByOtherPlayer) {
      messageInputContainer.style.display = "none";
      blockMessage.style.display = "block";
      blockMessage.textContent = "This user has blocked you, you can't send messages.";
    }
    else {
      messageInputContainer.style.display = "flex";
      blockMessage.style.display = "none";
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
}

customElements.define("chat-message", ChatMessage);
