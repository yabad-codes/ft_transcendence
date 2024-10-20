import BaseHTMLElement from "./BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class SearchPage extends BaseHTMLElement {
  constructor() {
    super("search-page");
    const { state, registerUpdate } = createState({
      searchResults: null,
      allPlayers: [],
      isLoading: false,
      error: null,
    });

    this.state = state;
    this.registerUpdate = registerUpdate;
    this.registerLocalFunctions();
    this.debounceTimer = null;
  }

  connectedCallback() {
    super.connectedCallback();
    this.render();
    this.setupEventListeners();
    this.fetchAllPlayers();
  }

  render() {
    this.innerHTML = `
      <div class="container mt-5">
        <div class="row justify-content-center">
          <div class="col-md-8">
            <h1 class="text-center mb-4">Player Search</h1>
            <div class="input-group mb-3">
              <input type="text" id="search-input" class="form-control" placeholder="Enter username, first name, or last name..." aria-label="Search term">
              <button class="btn btn-primary" type="button" id="search-button">
                <i class="bi bi-search"></i> Search
              </button>
            </div>
            <div id="search-results" class="mt-4">
              <!-- Search results will be displayed here -->
            </div>
          </div>
        </div>
      </div>
    `;
    this.searchInput = this.querySelector('#search-input');
    this.searchButton = this.querySelector('#search-button');
    this.searchResults = this.querySelector('#search-results');
  }

  setupEventListeners() {
    this.searchButton.addEventListener('click', () => this.performSearch());
    this.searchInput.addEventListener('input', () => this.debouncedSearch());
    this.searchInput.addEventListener('keypress', (event) => {
      if (event.key === 'Enter') {
        this.performSearch();
      }
    });
  }

  registerLocalFunctions() {
    this.registerUpdate("searchResults", this.updateUISearchResults.bind(this));
    this.registerUpdate("isLoading", this.updateLoadingState.bind(this));
    this.registerUpdate("error", this.displayError.bind(this));
  }

  async fetchAllPlayers() {
    try {
      this.state.isLoading = true;
      const response = await app.api.get('/api/players');
   
      
      if (response.data && response.data.success && Array.isArray(response.data.data)) {
        this.state.allPlayers = response.data.data;
        if (this.state.allPlayers.length === 0) {
          console.warn('Received an empty array of players');
        }
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Error fetching players:', error);
      this.state.error = "Failed to fetch players. Please try again later.";
    } finally {
      this.state.isLoading = false;
    }
  }

  debouncedSearch() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => this.performSearch(), 300);
  }

  performSearch() {
    const searchTerm = this.searchInput.value.trim().toLowerCase();
    if (searchTerm === '') {
      this.state.searchResults = null;
      return;
    }

    this.state.isLoading = true;
    this.state.error = null;

    try {
      if (!Array.isArray(this.state.allPlayers)) {
        throw new Error('Player data is not available');
      }

      const filteredPlayers = this.state.allPlayers.filter(player => 
        player.username.toLowerCase().includes(searchTerm) ||
        player.first_name.toLowerCase().includes(searchTerm) ||
        player.last_name.toLowerCase().includes(searchTerm)
      );

      this.state.searchResults = filteredPlayers;
    } catch (error) {
      console.error('Error during search:', error);
      this.state.error = "An error occurred during the search. Please try again.";
    } finally {
      this.state.isLoading = false;
    }
  }

  updateLoadingState() {
    if (this.state.isLoading) {
      this.showLoading();
    } else {
      this.updateUISearchResults();
    }
  }

  showLoading() {
    this.searchResults.innerHTML = `
      <div class="text-center">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
    `;
  }

  updateUISearchResults() {
    if (this.state.error) {
      this.displayError();
    } else if (this.state.searchResults === null) {
      this.searchResults.innerHTML = ''; // Clear results when no search has been performed
    } else if (this.state.searchResults.length === 0) {
      this.displayNotFound();
    } else {
      this.displayResults(this.state.searchResults);
    }
  }

  displayResults(results) {
    this.searchResults.innerHTML = `
      <ul class="list-group">
        ${results.map(player => `
          <li class="list-group-item" style="cursor: pointer;" data-username="${player.username}">
            <div class="d-flex align-items-center">
              <img src="${player.avatar_url}" alt="${player.username}'s avatar" class="rounded-circle me-3" style="width: 50px; height: 50px;">
              <div>
                <h5 class="mb-1">${player.username}</h5>
                <p class="mb-0">${player.first_name} ${player.last_name}</p>
              </div>
            </div>
          </li>
        `).join('')}
      </ul>
    `;

    const listItems = this.searchResults.querySelectorAll('li');
    listItems.forEach(item => {
        item.addEventListener('click', (event) => {
            const username = event.currentTarget.dataset.username;
            this.handlePlayerClick(username);
        });
    });
  }

  handlePlayerClick(username) {
    console.log(`Clicked on player: ${username}`);
    app.router.go(`/profile/${username}`);
  }

  displayNotFound() {
    this.searchResults.innerHTML = `
      <div class="alert alert-warning" role="alert">
        No players found matching your search.
      </div>
    `;
  }

  displayError() {
    this.searchResults.innerHTML = `
      <div class="alert alert-danger" role="alert">
        ${this.state.error}
      </div>
    `;
  }
}

customElements.define("search-page", SearchPage);