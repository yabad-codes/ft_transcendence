import { NavBar } from "./js/components/Navbar.js";
import { ChatPage } from "./js/pages/ChatPage.js";
import { GamePage } from "./js/pages/GamePage.js";
import { GameScreen } from "./js/pages/GameScreen.js";
import { HomePage } from "./js/pages/HomePage.js";
import { LoginPage } from "./js/pages/LoginPage.js";
import { RegisterPage } from "./js/pages/RegisterPage.js";
import { ChatMessage } from "./js/components/ChatMessage.js";
import { LeaderboardPage } from "./js/pages/LeaderboardPage.js";
import { TwoFactorAuthPage } from "./js/pages/2faPage.js";
import { SettingsPage } from "./js/pages/SettingsPage.js";
import API from "./js/utils/API.js";
import Router from "./js/utils/router.js";

// global app object that is available on all JS source code, later will be modified as our needs
window.app = {};

app.router = Router;
app.api = API;
app.isLoggedIn = true;
app.profile = null;

window.addEventListener("DOMContentLoaded", () => {
  app.router.init();
});
