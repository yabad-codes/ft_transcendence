import BaseHTMLElement from "./BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class ProfilePage extends BaseHTMLElement {
  constructor() {
    super("profilepage");
    const { state, registerUpdate } = createState({
      profile: null,
      friends: [],
      matches: [],
      isPersonalProfile: false,
      isLoading: false,
    });

    this.state = state;
    this.registerUpdate = registerUpdate;
    this.registerLocalFunctions();
  }

  connectedCallback() {
    super.connectedCallback();
    this.determineProfileType();
    window.addEventListener("popstate", this.handleURLChange.bind(this));
  }

  disconnectedCallback() {
    window.removeEventListener("popstate", this.handleURLChange.bind(this));
    if (super.disconnectedCallback) {
      super.disconnectedCallback();
    }
  }

  handleURLChange() {
    this.determineProfileType();
  }

  registerLocalFunctions() {
    this.registerUpdate(
      "isPersonalProfile",
      this.loadPersonalProfile.bind(this)
    );
    this.registerUpdate("profile", this.updateUserInfoView.bind(this));
    this.registerUpdate("matches", this.updateMatchesListView.bind(this));
    this.registerUpdate("isLoading", this.updateLoadingState.bind(this));
  }

  updateLoadingState() {
    const loadingIndicator = this.querySelector(".loading-indicator");
    if (this.state.isLoading) {
      if (!loadingIndicator) {
        const indicator = document.createElement("div");
        indicator.classList.add("loading-indicator", "text-center", "my-3");
        indicator.innerHTML =
          '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';
        this.querySelector(".match-list-profile").prepend(indicator);
      }
    } else {
      if (loadingIndicator) {
        loadingIndicator.remove();
      }
    }
  }

  determineProfileType() {
    const path = window.location.pathname;
    if (path === "/profile") {
      this.state.isPersonalProfile = true;
    } else if (path.startsWith("/profile/")) {
      const username = path.split("/")[2];
      if (username === app.profile.username) {
        app.router.go("/profile");
        return;
      }
      this.loadUserProfile(username);
    }
  }

  changeProfileView() {
    if (this.state.isPersonalProfile) {
      //     this.updateUserInfoView();
      this.querySelector(".match-list-profile").classList.add("col-md-8");
      this.querySelector(".friend-list-section").classList.remove("d-none");
      this.updateFriendListView();
      //     // this.updateMatchesListView();
    }
  }

  loadPersonalProfile() {
    this.state.profile = app.profile;
    this.loadFriends();
    this.loadMatches(app.profile.username);
  }

  loadUserProfile(username) {
    this.state.isLoading = true;
    app.api
      .get(`/api/profile/${username}`)
      .then((response) => {
        if (response.status >= 400) {
          displayRequestStatus("error", response.data);
          app.router.go("/404");
          return;
        }
        this.state.profile = response.data;
        this.loadFriends();
        this.loadMatches(username);
      })
      .finally(() => {
        this.state.isLoading = false;
      });
  }

  loadFriends() {
    app.api.get("/api/friendships/").then((response) => {
      if (response.status >= 400) {
        displayRequestStatus("error", response.data);
        return;
      }
      this.state.friends = response.data.filter(
        (friend) => friend.friendshipAccepted
      );
      this.changeProfileView();
    });
  }

  loadMatches(username) {
    this.state.isLoading = true;
    app.api
      .get(`/api/history/matches/${username}/`)
      .then((response) => {
        if (response.status >= 400) {
          displayRequestStatus("error", response.data);
          return;
        }
        this.state.matches = response.data.matches || [];
      })
      .catch((error) => {
        displayRequestStatus("error", "Failed to load match history");
        console.error("Error loading match history:", error);
      })
      .finally(() => {
        this.state.isLoading = false;
      });
  }

  updateUserInfoView() {
    const user = this.state.profile;
    // console.log(user);
    this.querySelector(".profile-user-image").src =
      user.avatar_url || "./images/avatar.jpg";
    this.querySelector(".profile-user-name").textContent =
      user.username || "default username";
    this.querySelector(".profile-user-wins").textContent = user.wins || 0;
    this.querySelector(".profile-user-losses").textContent = user.losses || 0;
    this.querySelector(".profile-user-matches").textContent =
      (user.wins || 0) + (user.losses || 0);

    const statusIndicator = this.querySelector(".avatar_status");
    if (user.online) {
      statusIndicator.classList.add("online");
      statusIndicator.classList.remove("offline");
    } else {
      statusIndicator.classList.add("offline");
      statusIndicator.classList.remove("online");
    }

    // Show/hide friend management buttons based on profile type
    if (this.state.isPersonalProfile) {
      this.querySelector(".first-btn").classList.remove("d-none");
      this.querySelector(".first-btn").addEventListener("click", () => {
        app.router.go("/settings");
      });
    } else {
      // Handle non-personal profile view
      const addBtn = this.querySelector(".second-btn");
      const blockBtn = this.querySelector(".third-btn");
      const removeBtn = this.querySelector(".fourth-btn");

      blockBtn.setAttribute("data-friendship-username", user.username);
      // removeBtn.setAttribute('data-friendship-id', user.friendshipID);

      this.getFriendshipID(user.username).then((friendshipID) => {
        console.log("ID is :", friendshipID);
        if (friendshipID) {
          // Proceed with removing the friend
          removeBtn.setAttribute("data-friendship-id", friendshipID);
        } else {
          console.log("No friendship ID found for this user.");
        }
      });
      // removeBtn.addEventListener("click", this.handleRemoveFriend.bind(this));
      // blockBtn.addEventListener("click", this.handleBlockFriend.bind(this));

      if (user.isFriend) {
        // User is a friend: show remove and block buttons
        removeBtn.classList.remove("d-none");
        blockBtn.classList.remove("d-none");
        addBtn.classList.add("d-none");

        removeBtn.addEventListener("click", this.handleRemoveFriend.bind(this));
        blockBtn.addEventListener("click", this.handleBlockFriend.bind(this));
      } else {
        // User is not a friend: show add and block buttons
        addBtn.classList.remove("d-none");
        blockBtn.classList.remove("d-none");
        removeBtn.classList.add("d-none");

        addBtn.addEventListener("click", this.handleAddFriend.bind(this));
        blockBtn.addEventListener("click", this.handleBlockFriend.bind(this));
      }
    }
    // add the logic to add friend and remove or block it
    // ...
  }

  updateFriendListView() {
    const friendList = this.querySelector(".friend-list");
    if (!friendList) return;

    friendList.innerHTML = "";
    this.state.friends.forEach((friend) => {
      const friendship =
        friend.player1.username === app.profile.username
          ? friend.player2
          : friend.player1;
      let friendItem = document.createElement("li");
      friendItem.classList.add(
        "list-group-item",
        "d-flex",
        "align-items-center"
      );

      friendItem.innerHTML = `
                <div class="avatar me-2">
                    <img class="avatar_image" src="${friendship.avatar_url}" alt="Avatar image" /> 
                    <span class="avatar_status"></span>
                </div>
                <span class="col friend-name" style="cursor: pointer;">${friendship.username}</span>
            `;

      const friendName = friendItem.querySelector(".friend-name");
      friendName.addEventListener("click", () => {
        app.router.go(`/profile/${friendship.username}`);
      });

      if (this.state.isPersonalProfile) {
        const removeBtn = document.createElement("button");
        removeBtn.setAttribute("type", "button");
        removeBtn.setAttribute("class", "btn btn-secondary col-auto me-2");
        removeBtn.setAttribute("data-friendship-id", friend.friendshipID);
        removeBtn.textContent = "Remove";
        removeBtn.addEventListener("click", this.handleRemoveFriend.bind(this));
        friendItem.appendChild(removeBtn);

        const blockBtn = document.createElement("button");
        blockBtn.setAttribute("type", "button");
        blockBtn.setAttribute("class", "btn btn-secondary col-auto me-2");
        blockBtn.setAttribute("data-friendship-username", friendship.username);
        blockBtn.textContent = "Block";
        blockBtn.addEventListener("click", this.handleBlockFriend.bind(this));
        friendItem.appendChild(blockBtn);

        const statusIndicator = friendItem.querySelector(".avatar_status");
        if (friendship.online) {
          statusIndicator.classList.add("online");
          statusIndicator.classList.remove("offline");
        } else {
          statusIndicator.classList.add("offline");
          statusIndicator.classList.remove("online");
        }
      }

      friendList.appendChild(friendItem);
    });
  }
  updateMatchesListView() {
    const matchesList = this.querySelector(".match-list-profile");
    if (!matchesList) return;

    matchesList.innerHTML = "<p class='leaderboard-title'>Recent Matches</p>";

    if (this.state.matches.length === 0) {
      const noMatchesMessage = document.createElement("li");
      noMatchesMessage.classList.add("list-group-item", "text-center");
      noMatchesMessage.textContent = "No matches found";
      matchesList.appendChild(noMatchesMessage);
      return;
    }

    this.state.matches.forEach((match) => {
      let matchItem = document.createElement("li");
      matchItem.classList.add("list-group-item");

      const isPlayer1 = match.player === this.state.profile.username;
      const opponent = isPlayer1 ? match.opponent : match.player;
      const playerScore = isPlayer1 ? match.player_score : match.opponent_score;
      const opponentScore = isPlayer1
        ? match.opponent_score
        : match.player_score;
      const result =
        match.winner === this.state.profile.username ? "Won" : "Lost";

      matchItem.innerHTML = `
            <div style="text-align: center;" class="matches-label">${
              match.date
            }</div>
            <div class="d-flex align-items-center justify-content-between mb-5">
                <div class="d-flex align-items-center">
                    <img class="avatar_image me-2" src="${app.profile.avatar_url}" alt="${
                      this.state.profile.username
                    }" />
                    <span>${this.state.profile.username}</span>
                </div>
                <div class="text-center mt-2 d-flex flex-column" style="padding-right: 15px;">
                    <span class="pb-2">${playerScore} / ${opponentScore}</span>
                    <span class="badge ${
                    result === "Won" ? "bg-success" : "bg-danger"
                    } rounded-pill">${result}</span>
                </div>
                <div class="d-flex align-items-center">
                    <span>${opponent}</span>
                    <img class="avatar_image ms-2" src="${match.opponent_avatar}" alt="${opponent}" />
                </div>
            </div>
            
        `;

      matchesList.appendChild(matchItem);
    });
  }

  handleBlockFriend(event) {
    const username = event.target.getAttribute("data-friendship-username");
    app.api
      .patch(`/api/profile/${username}/block`)
      .then(() => {
        this.state.friends = this.state.friends.filter(
          (friend) => friend.username !== username
        );
        event.target.parentNode.remove();
        app.router.go(`/profile`);
      })
      .catch((error) => {
        displayRequestStatus("error", "Failed to block friend");
      });
  }

  handleRemoveFriend(event) {
    const friendshipId = event.target.getAttribute("data-friendship-id");
    app.api
      .delete(`/api/friendships/${friendshipId}`)
      .then(() => {
        this.state.friends = this.state.friends.filter(
          (friend) => friend.friendshipID !== friendshipId
        );
        event.target.parentNode.remove();
      })
      .catch((error) => {
        displayRequestStatus("error", "Failed to remove friend");
      });
  }
  handleAddFriend() {
    const targetUsername = this.state.profile.username;
    console.log("Attempting to send friend request to:", targetUsername);

    const requestData = {
      player2_username: targetUsername,
    };

    try {
      app.api.post(`/api/friendships/`, requestData).then((response) => {
        // Handle the response based on the status code
        if (response.status === 200) {
          displayRequestStatus("success", "Friend request sent successfully");
          this.state.profile.isFriend = true; // Mark as a friend after success
          this.updateUserInfoView();
        } else if (response.status === 400) {
          displayRequestStatus(
            "error",
            "A pending friendship request already exists."
          );
          this.updateUserInfoView();
        } else if (response.status === 403) {
          displayRequestStatus("error", "You are already friends.");
          this.updateUserInfoView();
        }
      });
    } catch (error) {
      let errorMessage = "Failed to send friend request";
      displayRequestStatus("error", errorMessage);
    }
  }

  getFriendshipID(username) {
    return app.api.get("/api/friendships/").then((response) => {
      if (response.status >= 400) {
        displayRequestStatus("error", response.data);
        return null;
      }
      this.state.friends = response.data.filter(
        (friend) => friend.friendshipAccepted
      );
      const friendship = this.state.friends.find(
        (friend) =>
          friend.player1.username === username ||
          friend.player2.username === username
      );
      return friendship ? friendship.friendshipID : null;
    });
  }
}

customElements.define("profile-page", ProfilePage);
