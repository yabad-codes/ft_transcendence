import BaseHTMLElement from "../pages/BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";

export class ChatMessage extends BaseHTMLElement {
  constructor() {
    super("chatmessages");
    const { state, registerUpdate } = createState({
      messages: [],
      newConversation: null,
    });
    this._conversation = { id: 0, player: null };
    this.state = state;
    this.registerUpdate = registerUpdate;
    this.registerLocalFunctions();
  }

  connectedCallback() {
    super.connectedCallback();
    // Add additional logic for the game page ...
    console.log("ChatMessage connected");
    this.submitMessage();
    console.log(this._conversation);
    const userProfile = this.querySelector(".user_profile_bar");
    userProfile.querySelector(".avatar_image").src =
      this._conversation.player.avatar;
    userProfile.querySelector(
      "span > span"
    ).textContent = `${this._conversation.player.first_name} ${this._conversation.player.last_name}`;
  }

  set conversation(conversation) {
    this._conversation = conversation;
    console.log(conversation);
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
      });
  }

  updateUIMessages() {
    const messageContainer = this.querySelector(".chat_messages");

    // add new element to the chat message
    if (messageContainer.lastElementChild) {
      const lastMessage = this.state.messages[this.state.messages.length - 1];
      console.log(lastMessage);
      messageContainer.innerHTML += this.createMessageElement(lastMessage);
      return;
    }
    console.log(this.state.messages);
    const messageElements = this.state.messages.map((message) => {
      const messageElement = this.createMessageElement(message);
      return messageElement;
    });
    messageContainer.innerHTML = messageElements.join("");
  }

  submitMessage() {
    const submitButton = this.querySelector("button[type='submit']");
    submitButton.addEventListener("click", this.createNewMessage.bind(this));
  }

  createNewMessage() {
    const messageInput = this.querySelector("input[name='message-input']");
    console.log(messageInput);
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
  }

  createMessageElement(message) {
    const isCurrentUser = message.sender != app.profile.username;

    return isCurrentUser
      ? `
	<span class="mine_message fw-medium">
		<p
		class="pe-4 ps-4 pt-2 pb-2 d-inline-block rounded-top-4 rounded-end-4 me-2"
		>
		${message.content}
		</p>
		3:15PM
	</span>
	`
      : `
	<span class="friend_message fw-medium align-self-end">
		<p
		class="pe-4 ps-4 pt-2 pb-2 d-inline-block text-light rounded-top-4 rounded-start-4 me-2"
		>
		${message.content}
		</p>
		3:15PM
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
    console.log(conversationElement);
    const conversationText = conversationElement.querySelector(".direct_message_text");
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
    const [conversation] = chatPage.state.conversations.splice(conversationIndex, 1);

    // Add the conversation to the beginning of the array
    chatPage.state.conversations.unshift(conversation);
    // check if the conversation is already at the top
    if (conversationContainer.firstElementChild === conversationElement) {
      return;
    }
    conversationContainer.removeChild(conversationElement);
    conversationContainer.prepend(conversationElement);
  }
}

customElements.define("chat-message", ChatMessage);
