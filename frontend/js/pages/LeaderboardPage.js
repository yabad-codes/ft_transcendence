import BaseHTMLElement from "./BaseHTMLElement.js";
import { api } from "../utils/api.js";

export class LeaderboardPage extends BaseHTMLElement {
  constructor() {
    super("leaderboardpage");

	this.players = [];
  }

  intializeElements() {
	this.player_rank = 1;
	this.avatar_src = "./images/Image-not-found.png";

	this.LeaderboardContainer = document.getElementById('leaderboardContainer');
  }

  async fetchPlayers() {
	try {
		const response = await api.getPlayers();
		//! Backend API response should include a success member like this : { success: true, players: [] }
		if (response.success) {
			this.players = response;
			this.calculateRank();
		}
	}
	catch (error) {
		console.error('Error getting leaderboard:', error);
	}
  }

  async connectedCallback() {
	  super.connectedCallback();
	  this.intializeElements();
	  await this.fetchPlayers();
	  this.render();
  }

  calculateRank() {
	if (!this.players.length) return;
  
	// Sort players by performance score
	this.players.sort((a, b) => {
	  const performanceA = a.matches_played > 0 ? (a.wins - a.losses) / a.matches_played : 0;
	  const performanceB = b.matches_played > 0 ? (b.wins - b.losses) / b.matches_played : 0;
  
	  return performanceB - performanceA;
	});
  
	// Assign ranks
	this.players.forEach((player, index) => {
	  player.rank = index + 1;
	});
  }
  
  

  render() {
	if (!this.LeaderboardContainer)
        return;
	if (!this.players.length) {
		this.LeaderboardContainer.insertAdjacentHTML('beforebegin', `
			<div class="container min-vh-100 d-flex align-items-center justify-content-center">
				<div class="no-player-card p-5 text-center">
					<div class="trophy-icon mb-4">🏆</div>
					<h2 class="mb-3">No Players Found</h2>
					<p class="mb-4">
						We've searched far and wide <span class="search-animation">🔍</span><br>
						but couldn't find any players on the leaderboard.
					</p>
				</div>
			</div>
		`);
		return;
	}
	this.LeaderboardContainer.classList.remove('d-none');
	this.LeaderboardContainer.insertAdjacentHTML('beforeend', this.poduim());
	this.players && this.players.forEach(player => {
		this.player_rank = player.rank || 0;
		this.avatar_src = player.avatar || this.avatar_src;
		this.player_name = player.username;
		this.coalition_src = player.coalition || this.coalition_src;
		this.cloalition_name = player.coalition_name || '';
		this.matches_played = player.matches_played || 0;
		this.wins_number = player.wins || 0;
		this.losses_value = player.losses || 0;
		this.player_achievements = player.achievements || 0;

		this.LeaderboardContainer.insertAdjacentHTML('beforeend', this.generateCard());
	});
  }

  poduim() {
	if (this.players.length < 3) return '';
	return `
		<div class="podium d-flex align-items-end justify-content-center mb-4">
			<div class="podium-item second-place h-75 d-flex flex-column align-items-center justify-content-end mx-2 px-3 pb-2 rounded">
				<div class="trophy mb-2"><i class="fas fa-trophy text-white"></i></div>
				<img src="${this.players[1].avatar}" alt="Player 2" class="rounded-circle mb-2 player-avatar">
				<span class="text-white">${this.players[1].username}</span>
			</div>
			<div class="podium-item first-place h-100 d-flex flex-column align-items-center justify-content-end mx-2 px-3 pb-2 rounded">
				<div class="trophy mb-2"><i class="fas fa-trophy text-white"></i></div>
				<img src="${this.players[0].avatar}" alt="Player 1" class="rounded-circle mb-2 player-avatar">
				<span class="text-white">${this.players[0].username}</span>
			</div>
			<div class="podium-item third-place h-50 d-flex flex-column align-items-center justify-content-end mx-2 px-3 pb-2 rounded">
				<div class="trophy mb-2"><i class="fas fa-trophy text-white"></i></div>
				<img src="${this.players[2].avatar}" alt="Player 3" class="rounded-circle mb-2 player-avatar">
				<span class="text-white">${this.players[2].username}</span>
			</div>
		</div>
	`;
  }


  generateCard() {
	return `
		<section class="player-card row align-items-center flex-nowrap">
			<div class="col-1 rank-container text-center">
				<div class="rank-number">#${this.player_rank}</div>
				<div class="rank-label">Rank</div>
			</div>
			<div class="col-3 player-info">
				<img src="${this.avatar_src}" alt="Player avatar" class="player-avatar rounded-circle">
				<div class="player-details">
					<div class="player-name">${this.player_name}</div>
				</div>
			</div>
			<div class="col-1 matches-container text-center">
				<div class="matches-value">${this.matches_played}</div>
				<div class="matches-label">Matches played</div>
			</div>
			<div class="col-1 wins-container text-center">
				<div class="wins-value">${this.wins_number}</div>
				<div class="wins-label">Wins</div>
			</div>
			<div class="col-1 losses-container text-center">
				<div class="losses-value">${this.losses_value}</div>
				<div class="losses-label">losses</div>
			</div>
			<div class="col-1 text-end">
				<img src="./images/arrow.png" alt="More icon" class="more-icon">
			</div>
		</section>
	`;
  }

}

// Define the new custom element in the customElements registry so it can be used in the DOM later
customElements.define("leaderboard-page", LeaderboardPage);
