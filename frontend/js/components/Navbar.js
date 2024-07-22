import BaseHTMLElement from "../pages/BaseHTMLElement.js";

export class NavBar extends BaseHTMLElement {
    constructor() {
        super('navbar', './css/components/NavBar.css')
    }

    connectedCallback() {
        super.connectedCallback();

        // Handle navigation links
        this.querySelectorAll('a.nav-links').forEach(link => {
            console.log(link);
            link.addEventListener('click', event => {
                event.preventDefault();
                const urlPath = event.currentTarget.getAttribute("href")
                console.log(urlPath);
                app.router.go(urlPath)
            })
        })
    }
}

customElements.define("nav-bar", NavBar)
