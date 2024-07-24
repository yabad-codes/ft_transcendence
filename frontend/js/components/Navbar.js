import BaseHTMLElement from "../pages/BaseHTMLElement.js";

export class NavBar extends BaseHTMLElement {
    constructor() {
        super('navbar')
    }

    connectedCallback() {
        super.connectedCallback();

        // Handle navigation links
        this.querySelectorAll('a.nav-links').forEach(link => {
            link.addEventListener('click', event => {
                event.preventDefault();
                const urlPath = event.currentTarget.getAttribute("href")
                app.router.go(urlPath)
            })
        })
    }
}

customElements.define("nav-bar", NavBar)
