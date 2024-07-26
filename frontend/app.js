import { NavBar } from "./js/components/Navbar.js";
import { ChatPage } from "./js/pages/ChatPage.js";
import { GamePage } from "./js/pages/GamePage.js";
import { HomePage } from "./js/pages/HomePage.js";
import { LoginPage } from "./js/pages/LoginPage.js";
import Router from "./js/utils/Router.js";

// global app object that is available on all JS source code, later will be modified as our needs
window.app = {};

app.router = Router;
app.isLoggedIn = true;

window.addEventListener("DOMContentLoaded", () => {
  app.router.init();
  sendMessageActionStyling();
});

// This is temporary for me Anouar, later will be placed in a custom HTML Element 😁
function sendMessageActionStyling() {
  const input = document.querySelector(".send_message_container input");
  const container = document.querySelector(".send_message_container");

  input.addEventListener("focus", () => {
    container.classList.add("focused");
  });

  input.addEventListener("blur", () => {
    container.classList.remove("focused");
  });
}
