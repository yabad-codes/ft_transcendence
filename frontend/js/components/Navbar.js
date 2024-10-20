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

        // Handle logout
        this.querySelector('.logout-button').addEventListener('click', async () => {
            const response = await app.api.post('/api/logout/', {})
            console.log(response);
            if (response.status === 200) {
                console.log('Logged out successfully');
                app.isLoggedIn = false;
                app.profile = null;
                app.router.go('/login')
            }
        })
    }
}

customElements.define("nav-bar", NavBar)
