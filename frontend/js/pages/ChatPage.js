import BaseHTMLElement from "./BaseHTMLElement.js"

export class ChatPage extends BaseHTMLElement {
    constructor() {
        super('chatpage')

    }

    connectedCallback() {
        super.connectedCallback()
        // Add additional logic for the chat page ... 
    }
}

customElements.define('chat-page', ChatPage)
