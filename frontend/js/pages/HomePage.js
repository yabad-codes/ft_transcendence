import BaseHTMLElement from "./BaseHTMLElement.js"

export class HomePage extends BaseHTMLElement {
    constructor() {
        super('homepage')

    }

    connectedCallback() {
        super.connectedCallback()
        // Add additional logic for the home page ... 
    }
}

customElements.define('home-page', HomePage)
