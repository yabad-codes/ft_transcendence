import BaseHTMLElement from "./BaseHTMLElement.js";
import { createState } from "../utils/stateManager.js";
import { displayRequestStatus } from "../utils/errorManagement.js";

export class NotificationPage extends BaseHTMLElement {
    constructor() {
        super("notification-page");
        const { state, registerUpdate } = createState({
            friendRequests: [],
        });

        this.state = state;
        this.registerUpdate = registerUpdate;
        this.registerLocalFunctions();
    }

    connectedCallback() {
        super.connectedCallback();
        this.render();
        this.loadFriendRequests();
        this.updateNotificationCount();
    }

    registerLocalFunctions() {
        this.registerUpdate("friendRequests", this.updateFriendRequestsView.bind(this));
    }

    render() {
        this.innerHTML = `
            <div class="container mt-4">
                <h2>Friend Requests</h2>
                <ul class="friend-requests-list list-group mt-3">
                    <!-- Friend requests will be dynamically inserted here -->
                </ul>
            </div>
        `;
    }


    loadFriendRequests() {
        app.api.get("/api/friendships/").then((response) => {
            if (response.status >= 400) {
                displayRequestStatus("error", response.data);
                return;
            }
            this.state.friendRequests = response.data.filter(friendship => 
                friendship.player2.username === app.profile.username && !friendship.friendshipAccepted
            );
            this.updateNotificationCount();
        });
    }
      // Add a method to update the notification count
    updateNotificationCount() {
        const notificationCountElement = document.querySelector('.notification-badge');
        if (notificationCountElement) {
            notificationCountElement.textContent = this.state.friendRequests.length;
        }
    }

    updateFriendRequestsView() {
        const requestsList = this.querySelector(".friend-requests-list");
        if (!requestsList) return;

        requestsList.innerHTML = "";
        if (this.state.friendRequests.length === 0) {
            requestsList.innerHTML = '<li class="list-group-item">No pending friend requests.</li>';
            return;
        }

        this.state.friendRequests.forEach((request) => {
            let requestItem = document.createElement("li");
            requestItem.classList.add("list-group-item", "d-flex", "align-items-center", "justify-content-between");
            
            requestItem.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="avatar me-2">
                        <img class="avatar_image" src="${request.player1.avatar_url}" alt="Avatar image" style="width: 40px; height: 40px; border-radius: 50%;"/> 
                    </div>
                    <span class="friend-name">${request.player1.username}</span>
                </div>
                <div>
                    <button type="button" class="btn btn-success me-2 accept-btn" data-friendship-id="${request.friendshipID}">Accept</button>
                    <button type="button" class="btn btn-danger reject-btn" data-friendship-id="${request.friendshipID}">Reject</button>
                </div>
            `;

            const acceptBtn = requestItem.querySelector('.accept-btn');
            const rejectBtn = requestItem.querySelector('.reject-btn');

            acceptBtn.addEventListener('click', this.handleAcceptFriend.bind(this));
            rejectBtn.addEventListener('click', this.handleRejectFriend.bind(this));

            requestsList.appendChild(requestItem);
        });
    }
   

    handleAcceptFriend(event) {
        const friendshipId = event.target.getAttribute('data-friendship-id');
          app.api.patch(`/api/friendships/${friendshipId}/accept/`)
            .then((response) => {
                if (response.status === 200) {
                    
                    displayRequestStatus("success", "Friend request accepted");

                    this.loadFriendRequests();

                }
            })
            .catch((error) => {
                displayRequestStatus("error", "Failed to accept friend request");
            });
    }

    handleRejectFriend(event) {
        const friendshipId = event.target.getAttribute('data-friendship-id');
        console.log(friendshipId);
        app.api.patch(`/api/friendships/${friendshipId}/reject/`)
            .then((response) => {
                if (response.status === 204) {
                    displayRequestStatus("success", "Friend request rejected");
                    this.loadFriendRequests();
                }
            })
            .catch((error) => {
                displayRequestStatus("error", "Failed to reject friend request");
            });
    }
}

customElements.define("notification-page", NotificationPage);

