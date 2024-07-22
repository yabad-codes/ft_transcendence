import { NavBar } from "./js/components/Navbar.js"
import { GamePage } from "./js/pages/GamePage.js"
import { HomePage } from "./js/pages/HomePage.js"
import Router from './js/utils/Router.js'

// global app object that is available on all JS source code, later will be modified as our needs
window.app = {}

app.router = Router
app.isLoggedIn = true

window.addEventListener('DOMContentLoaded', () => {
    app.router.init();
})
