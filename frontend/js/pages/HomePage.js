import BaseHTMLElement from "./BaseHTMLElement.js"

export class HomePage extends BaseHTMLElement {
    constructor() {
        super('homepage', './css/pages/HomePage.css')

    }

    connectedCallback() {
        super.connectedCallback()
        // Add additional logic for the game page ... 
    }
}

customElements.define('home-page', HomePage)
