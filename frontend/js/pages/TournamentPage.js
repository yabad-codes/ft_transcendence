// TournamentPage.js
import BaseHTMLElement from "./BaseHTMLElement.js";

export class TournamentPage extends BaseHTMLElement {
    constructor() {
        super("tournamentpage");
        this.friends = [
            { id: 1, name: "Alice Johnson", avatar: "https://robohash.org/aelmaar.jpg" },
            { id: 2, name: "Bob Smith", avatar: "https://robohash.org/aelmaar.jpg" },
            { id: 3, name: "Charlie Brown", avatar: "https://robohash.org/aelmaar.jpg" },
            { id: 4, name: "David Lee", avatar: "https://robohash.org/aelmaar.jpg" },
            { id: 5, name: "Eve Taylor", avatar: "https://robohash.org/aelmaar.jpg" },
            { id: 6, name: "Frank Miller", avatar: "https://robohash.org/aelmaar.jpg" },
        ];
    }

    connectedCallback() {
        super.connectedCallback();
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.renderFriendsList(this.friends);
    }

    attachEventListeners() {
        this.querySelector('#searchBar').addEventListener('input', this.handleSearch.bind(this));
        this.querySelector('#friendsList').addEventListener('change', this.updateStartTournamentButton.bind(this));
        this.querySelector('#startTournament').addEventListener('click', this.startTournament.bind(this));
    }

    renderFriendsList(friendsToRender) {
        const friendsList = this.querySelector('#friendsList');
        friendsList.innerHTML = friendsToRender.map(friend => `
            <div class="friend-item">
                <input type="checkbox" id="friend${friend.id}" class="friend-checkbox">
                <img src="${friend.avatar}" alt="${friend.name}" class="avatar">
                <label for="friend${friend.id}">${friend.name}</label>
            </div>
        `).join('');
        this.updateStartTournamentButton();
    }

    handleSearch(e) {
        const searchTerm = e.target.value.toLowerCase();
        const filteredFriends = this.friends.filter(friend => friend.name.toLowerCase().includes(searchTerm));
        this.renderFriendsList(filteredFriends);
    }

    updateStartTournamentButton() {
        const selectedFriends = this.querySelectorAll('.friend-checkbox:checked');
        this.querySelector('#startTournament').disabled = selectedFriends.length !== 4;
    }

    startTournament() {
        this.querySelector('#friendsList').style.display = 'none';
        this.querySelector('#searchBar').style.display = 'none';
        this.querySelector('#startTournament').style.display = 'none';
        this.querySelector('#progressBarContainer').style.display = 'block';

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
    }
}

customElements.define('tournament-page', TournamentPage);