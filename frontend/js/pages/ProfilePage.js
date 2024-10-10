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
        });

        this.state = state;
        this.registerUpdate = registerUpdate;
        this.registerLocalFunctions();
    }

    connectedCallback() {

        super.connectedCallback();
        this.determineProfileType();
        // this.changeProfileView();

        // this.updateMatchesListView.bind(this);
        // Add event listener for URL changes
        window.addEventListener('popstate', this.handleURLChange.bind(this));
    }

    disconnectedCallback() {
       
        // Remove event listener when component is disconnected
        window.removeEventListener('popstate', this.handleURLChange.bind(this));
        if (super.disconnectedCallback) {
            super.disconnectedCallback();
        }
    }

    handleURLChange() {
        this.determineProfileType();
    }

    registerLocalFunctions() {
        this.registerUpdate("isPersonalProfile", this.loadPersonalProfile.bind(this));
        this.registerUpdate("profile", this.updateUserInfoView.bind(this));
        this.registerUpdate("matches", this.updateMatchesListView.bind(this));
    }

    determineProfileType() {
        
        const path = window.location.pathname;
        if (path === "/profile") {
            this.state.isPersonalProfile = true;
            // this.loadPersonalProfile();
        } else if (path.startsWith("/profile/")) {
            // this.state.isPersonalProfile = false;
            const username = path.split("/")[2];
            if (username === app.profile.username) {
                app.router.go("/profile");
                return ;
            }
            this.loadUserProfile(username);
        }
    }

    changeProfileView (){
        if (this.state.isPersonalProfile) {
            //     this.updateUserInfoView();
                this.querySelector('.match-list-profile').classList.add('col-md-8');
                this.querySelector('.friend-list-section').classList.remove('d-none');
                this.updateFriendListView();
            //     // this.updateMatchesListView();
        }
    }

    loadPersonalProfile() {
      
        this.state.profile = app.profile;
        this.loadFriends();
        // this.loadMatches();
    }

    loadUserProfile(username) {
        app.api.get(`/api/profile/${username}`).then((response) => {
            if (response.status >= 400) {
                displayRequestStatus("error", response.data);
                app.router.go("/404");      
                return;
            }
            this.state.profile = response.data;
            this.loadFriends();
            // this.loadMatches();
        });
    }

    loadFriends() {

        app.api.get("/api/friendships/").then((response) => {
            if (response.status >= 400) {
                displayRequestStatus("error", response.data);
                return;
            }
            this.state.friends = response.data.filter(friend => friend.friendshipAccepted);
            this.changeProfileView();
        });
    }

    // loadMatches() {
    //     app.api.get(`/api/matches/${this.state.profile.username}`).then((response) => {
    //         if (response.status >= 400) {
    //             displayRequestStatus("error", response.data);
    //             return;
    //         }
    //         this.state.matches = response.data;
    //     });
    // }

    updateUserInfoView() {
        const user = this.state.profile;
        // console.log(user);
        this.querySelector(".profile-user-image").src = user.avatar_url || "./images/avatar.jpg";
        this.querySelector(".profile-user-name").textContent = user.username || "default username";
        this.querySelector(".profile-user-wins").textContent = user.wins || 0;
        this.querySelector(".profile-user-losses").textContent = user.losses || 0;
        this.querySelector(".profile-user-matches").textContent = (user.wins || 0) + (user.losses || 0);

        const statusIndicator = this.querySelector(".avatar_status");
        if (user.online) {
            statusIndicator.classList.add("online");
            statusIndicator.classList.remove("offline");
        } else {
            statusIndicator.classList.add("offline");
            statusIndicator.classList.remove("online");
        }
        console.log("Status indicator:", statusIndicator);
        console.log("User online status:", user.online);



        // Show/hide friend management buttons based on profile type
        if (this.state.isPersonalProfile) {
            this.querySelector(".first-btn").addEventListener("click", () => {
                app.router.go('/edit-profile');
            });
        }
        else {
            this.querySelector(".first-btn").classList.add("d-none");
            // check if friend or not
        }
        // add the logic to add friend and remove or block it 
        // ...
    }

    updateFriendListView() {
        const friendList = this.querySelector(".friend-list");
        if (!friendList) return;
    
        friendList.innerHTML = "";
        this.state.friends.forEach((friend) => {
            const friendship = (friend.player1.username === app.profile.username) ? friend.player2 : friend.player1;
            let friendItem = document.createElement("li");
            friendItem.classList.add("list-group-item", "d-flex", "align-items-center");
            
            friendItem.innerHTML = `
                <div class="avatar me-2">
                    <img class="avatar_image" src="${friendship.avatar_url}" alt="Avatar image" /> 
                    <span class="avatar_status"></span>
                </div>
                <span class="col friend-name" style="cursor: pointer;">${friendship.username}</span>
            `;
    
            // Add click event to navigate to friend's profile
            const friendName = friendItem.querySelector('.friend-name');
            friendName.addEventListener('click', () => {
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
        const matchesList = this.querySelector(".matches-list");
        if (!matchesList) return;

        matchesList.innerHTML = "";
        this.state.matches.forEach((match) => {
            let matchItem = document.createElement("li");
            matchItem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
            
            const opponent = match.player1.username === this.state.profile.username ? match.player2 : match.player1;
            const result = match.winner === this.state.profile.username ? "Won" : "Lost";
            
            matchItem.innerHTML = `
                <span>${opponent.username}</span>
                <span>${match.score}</span>
                <span class="badge ${result === 'Won' ? 'bg-success' : 'bg-danger'} rounded-pill">${result}</span>
            `;
            
            matchesList.appendChild(matchItem);
        });
    }
    handleBlockFriend(event){
        const username = event.target.getAttribute('data-friendship-username');
       app.api.patch(`/api/profile/${username}/block`)
            .then(() => {
                this.state.friends = this.state.friends.filter(friend => friend.username !== username);
                event.target.parentNode.remove();
            })
            .catch((error) => {
                displayRequestStatus("error", "Failed to block friend");
            });
    }

    handleRemoveFriend(event) {
        const friendshipId = event.target.getAttribute('data-friendship-id');
        app.api.delete(`/api/friendships/${friendshipId}`)
            .then(() => {
                this.state.friends = this.state.friends.filter(friend => friend.friendshipID !== friendshipId);
                event.target.parentNode.remove();
            })
            .catch((error) => {
                displayRequestStatus("error", "Failed to remove friend");
            });
    }
}

customElements.define("profile-page", ProfilePage);