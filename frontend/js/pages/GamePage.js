import BaseHTMLElement from "./BaseHTMLElement.js"

export class GamePage extends BaseHTMLElement {
    constructor() {
        super('gamepage');
    }

    connectedCallback() {
        super.connectedCallback()
        // Add additional logic for the game page ... 
    }
}

customElements.define('game-page', GamePage)
