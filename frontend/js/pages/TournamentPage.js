// TournamentPage.js
import BaseHTMLElement from "./BaseHTMLElement.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class TournamentPage extends BaseHTMLElement {
  constructor() {
    super("tournamentpage");
  }

  connectedCallback() {
    super.connectedCallback();
    this.getPlayers();
    this.attachEventListeners();
  }

  getPlayers() {
    app.api.get("/api/players/online").then((response) => {
      if (response.status >= 400) {
        displayRequestStatus("error", response.data.message);
        return;
      }
      this.players = response.data;
      this.render();
    });
  }

  render() {
    this.renderFriendsList(this.players);
  }

  attachEventListeners() {
    this.querySelector("#searchBar").addEventListener(
      "input",
      this.handleSearch.bind(this)
    );
    this.querySelector("#friendsList").addEventListener(
      "change",
      this.updateStartTournamentButton.bind(this)
    );
    this.querySelector("#startTournament").addEventListener(
      "click",
      this.startTournament.bind(this)
    );
  }

  renderFriendsList(playersToRender) {
    const friendsList = this.querySelector("#friendsList");
    friendsList.innerHTML = playersToRender
      .map(
        (player) => `
            <div class="friend-item">
                <input type="checkbox" username="${player.username}" class="friend-checkbox">
                <img src="${player.avatar_url}" alt="${player.username}" class="avatar_69">
                <label for="${player.username}">${player.first_name} ${player.last_name}</label>
            </div>
        `
      )
      .join("");
    this.updateStartTournamentButton();
  }

  handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const filteredFriends = this.players.filter(
      (player) =>
        player.first_name.toLowerCase().includes(searchTerm) ||
        player.last_name.toLowerCase().includes(searchTerm)
    );
    this.renderFriendsList(filteredFriends);
  }

  updateStartTournamentButton() {
    const selectedFriends = this.querySelectorAll(".friend-checkbox:checked");
    this.querySelector("#startTournament").disabled =
      selectedFriends.length !== 3;
  }

  startTournament() {
    const checkedBoxes = Array.from(
      this.querySelectorAll(".friend-checkbox:checked")
    );
    const message = {
      player2_username: checkedBoxes[0].getAttribute("username"),
      player3_username: checkedBoxes[1].getAttribute("username"),
      player4_username: checkedBoxes[2].getAttribute("username"),
    };
    console.log(message);

    app.api.post("/api/create-tournament/", message).then((response) => {
      if (response.status >= 400) {
        displayRequestStatus("error", response.data.message);
        return;
      }
      this.querySelector("#friendsList").style.display = "none";
      this.querySelector("#searchBar").style.display = "none";
      this.querySelector("#startTournament").style.display = "none";
      this.querySelector("#progressBarContainer").style.display = "block";
      displayRequestStatus("success", "Tournament created successfully!");
      let progress = 0;
      const progressBar = this.querySelector("#progressBar");
      const interval = setInterval(() => {
        progress += 100 / 15;
        progressBar.style.width = `${progress}%`;
        if (progress >= 100) {
          clearInterval(interval);
          this.launchTournamentScreen(response.data);
        }
      }, 1000);
    });
  }

  launchTournamentScreen(tournamentData) {
    this.querySelector("#progressBarContainer").style.display = "none";

    app.router.removeOldPages();
    app.router.insertPage("tournament-screen");
    const tournamentScreen = document.querySelector("tournament-screen");

    tournamentScreen.addEventListener(
      "tournamentEnded",
      this.handleTournamentEnd.bind(this)
    );

    tournamentScreen.startTournament(tournamentData);
  }

  handleTournamentEnd(event) {
    const {tournamentId ,winner, results } = event.detail;

    const requestBody = {
      tournament_id: tournamentId,
      results: results
    };

    console.log(requestBody);

    app.api.post("/api/end-tournament/", requestBody).then((response) => {
      if (response.status >= 400) {
        displayRequestStatus("error", response.data.message);
        return;
      }
        displayRequestStatus("success", `${winner.tournamentName} won the tournament!`);
    });
  }
}
customElements.define("tournament-page", TournamentPage);
