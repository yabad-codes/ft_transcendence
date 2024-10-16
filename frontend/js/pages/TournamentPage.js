// TournamentPage.js
import BaseHTMLElement from "./BaseHTMLElement.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class TournamentPage extends BaseHTMLElement {
    constructor() {
        super("tournamentpage");
        // this.friends = [
        //     { id: 1, name: "Alice Johnson", avatar: "https://robohash.org/aelmaar.jpg" },
        //     { id: 2, name: "Bob Smith", avatar: "https://robohash.org/aelmaar.jpg" },
        //     { id: 3, name: "Charlie Brown", avatar: "https://robohash.org/aelmaar.jpg" },
        //     { id: 4, name: "David Lee", avatar: "https://robohash.org/aelmaar.jpg" },
        //     { id: 5, name: "Eve Taylor", avatar: "https://robohash.org/aelmaar.jpg" },
        //     { id: 6, name: "Frank Miller", avatar: "https://robohash.org/aelmaar.jpg" },
        // ];
    }

    connectedCallback() {
        super.connectedCallback();
        // this.render();
        this.getPlayers();
        this.attachEventListeners();
    }

    getPlayers () {
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
        this.querySelector('#searchBar').addEventListener('input', this.handleSearch.bind(this));
        this.querySelector('#friendsList').addEventListener('change', this.updateStartTournamentButton.bind(this));
        this.querySelector('#startTournament').addEventListener('click', this.startTournament.bind(this));
    }

    renderFriendsList(playersToRender) {
        const friendsList = this.querySelector('#friendsList');
        friendsList.innerHTML = playersToRender.map(player => `
            <div class="friend-item">
                <input type="checkbox" username="${player.username}" class="friend-checkbox">
                <img src="${player.avatar_url}" alt="${player.username}" class="avatar_69">
                <label for="${player.username}">${player.first_name} ${player.last_name}</label>
            </div>
        `).join('');
        this.updateStartTournamentButton();
    }

    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        // don't forget to handle whitespaces
        const filteredFriends = this.players.filter(player => player.first_name.toLowerCase().includes(searchTerm) || player.last_name.toLowerCase().includes(searchTerm));
        this.renderFriendsList(filteredFriends);
    }

    updateStartTournamentButton() {
        const selectedFriends = this.querySelectorAll('.friend-checkbox:checked');
        this.querySelector('#startTournament').disabled = selectedFriends.length !== 3;
    }

    startTournament() {
        // make an api call to start the tournament by sending the selected friends as player2, player3 and player4
        const checkedBoxes = Array.from(this.querySelectorAll('.friend-checkbox:checked'));
        const message = {
            player2_username: checkedBoxes[0].getAttribute('username'),
            player3_username: checkedBoxes[1].getAttribute('username'),
            player4_username: checkedBoxes[2].getAttribute('username'),
        };
        console.log(message);
        
        app.api.post("/api/create-tournament/", message).then((response) => {
            if (response.status >= 400) {
                displayRequestStatus("error", response.data.message);
                return;
            }
            this.querySelector('#friendsList').style.display = 'none';
            this.querySelector('#searchBar').style.display = 'none';
            this.querySelector('#startTournament').style.display = 'none';
            this.querySelector('#progressBarContainer').style.display = 'block';
            displayRequestStatus("success", "Tournament created successfully!");
            let progress = 0;
            const progressBar = this.querySelector('#progressBar');
            const interval = setInterval(() => {
                progress += 100 / 15;
                progressBar.style.width = `${progress}%`;
                if (progress >= 100) {
                    clearInterval(interval);
                    alert("Tournament is starting!");
                    // Here you would launch the game
                }
            }, 1000);
        });
    }
}

customElements.define('tournament-page', TournamentPage);