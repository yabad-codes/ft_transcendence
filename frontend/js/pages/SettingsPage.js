
import BaseHTMLElement from "./BaseHTMLElement.js";
import { ModalManager } from "./ModalManager.js";
import { TwoFactorAuthManager } from "./TwoFactorAuthManager.js";
import { AccountManager } from "./AccountManager.js";
import { PasswordManager } from "./PasswordManager.js";
import { GameManager } from "./GameManager.js";
import { api } from "../utils/api_service.js";

export class SettingsPage extends BaseHTMLElement {
    constructor() {
        super("settingspage");
        this.modalManager = null;
        this.twoFactorAuthManager = null;
		this.accountManager = null;
        this.activeModal = null;
		this.profileImage = null;
		this.blockedUsers = [];
        this.modals = {
            boostSecurity: {
                title: "Security Settings",
                content: this.getBoostSecurityContent.bind(this),
                footer: this.getBoostSecurityFooter.bind(this)
            },
			editAccount: {
				title: "Account Settings",
				content: this.getAccountContent.bind(this),
				footer: this.getAccountFooter.bind(this)
			},
			editPassword: {
				title: "Password Settings",
				content: this.getPasswordContent.bind(this),
				footer: this.getPasswordFooter.bind(this)
			},
			blockedUsers: {
				title: "Blocked Users",
				content: this.getBlockedUsersContent.bind(this),
			},
			gameSettings: {
				title: "Game Settings",
				content: this.gameSettingsContent.bind(this),
				footer: () => { return ''; }
			}
        };
    }

	async setProfileImage() {
		try {
			const response = await api.getUserDetails();
			if (response.success) {
				if (response.avatar) {
					const cacheBuster = new Date().getTime();
                	this.profileImage.src = `${response.avatar}?t=${cacheBuster}`;
				}
			}
		} catch (error) {
			console.error('Error getting user details:', error);
		}
	}

	initElements() {
		this.profileImage = document.getElementById('settingsProfileImage');
	}

	async getBlockedUsers() {
		try {
			const response = await api.getBlockedUsers();
			if (response.length > 0) {
				this.blockedUsers = response.map(block => ({
					blockID: block.blockID,
					username: block.blockedUser.username,
					firstName: block.blockedUser.first_name,
					lastName: block.blockedUser.last_name,
					avatarUrl: block.blockedUser.avatar_url,
					wins: block.blockedUser.wins,
					losses: block.blockedUser.losses,
					blockTimestamp: new Date(block.blockTimestamp)
				}));
			}
		} catch (error) {
			console.error('An error occurred while fetching blocked users:', error);
		}
	}

    async connectedCallback() {
		super.connectedCallback();
		this.initElements();
		this.setProfileImage();
        await this.checkTwoFactorStatus();
		await this.getBlockedUsers();
        this.setupEventListeners();
    }

    async checkTwoFactorStatus() {
        try {
            const response = await api.checkTwoFactor();
            this.twoFactorEnabled = response.two_factor_enabled;
        } catch (error) {
            console.error('Error checking 2FA status:', error);
            this.twoFactorEnabled = false;
        }
    }

	async handleChangeAvatar() {
		const input = document.createElement('input');
		input.type = 'file';
		input.accept = 'image/*';
		input.onchange = async (event) => {
			const file = event.target.files[0];
			if (file) {
				const formData = new FormData();
				formData.append('avatar', file);
	
				try {
					const response = await fetch('/api/update-avatar/', {
						method: 'POST',
						body: formData,
						credentials: 'include',
					});
	
					const data = await response.json();
	
					if (response.ok) {
						const reader = new FileReader();
						reader.onload = (e) => {
							this.profileImage.src = e.target.result;
						};
						reader.readAsDataURL(file);
					} else {
						console.error("Error updating avatar:", data.errors);
					}
				} catch (error) {
					console.error('Error during avatar update:', error);
				}
			}
		};
		input.click();
	}

    setupEventListeners() {
        this.querySelectorAll('.active-modal').forEach(button => {
			button.addEventListener('click', this.handleModalButtonClick.bind(this));
        });
		
		this.querySelector('#changeAvatar').addEventListener('click', this.handleChangeAvatar.bind(this));
    }

    handleModalButtonClick(event) {
        this.activeModal = event.target.dataset.modal;
        this.renderModal();
        this.modalManager.showModal();
    }

	handle2FAModalTask() {
		this.twoFactorAuthManager = new TwoFactorAuthManager(this.twoFactorEnabled);
        this.setupTwoFactorAuthListeners();
	}

	handleAccountModalTask() {
		this.accountManager = new AccountManager();
		this.setupAccountListeners();
	}

	handlePasswordModalTask() {
		this.passwordManager = new PasswordManager();
		this.setupPasswordListeners();
	}

	handleBlockedUsersModalTask() {
		this.renderBlockedUsers();
	}

	handleGameSettingsModalTask() {
		this.gameManager = new GameManager();
	}

    renderModal() {
        const modalConfig = this.modals[this.activeModal];

        if (!modalConfig) {
            console.error(`No configuration found for modal: ${this.activeModal}`);
            return;
        }

        const modalHTML = this.getModalHTML(modalConfig);

		this.insertAdjacentHTML('beforeend', modalHTML);

        this.setupModalListeners();

		switch (this.activeModal) {
			case 'boostSecurity':
				this.handle2FAModalTask();
				break;
			case 'editAccount':
				this.handleAccountModalTask();
				break;
			case 'editPassword':
				this.handlePasswordModalTask();
				break;
			case 'blockedUsers':
				this.handleBlockedUsersModalTask();
				break;
			case 'gameSettings':
				this.handleGameSettingsModalTask();
				break;
			default:
				break;
		}
    }

    setupModalListeners() {
        this.modalManager = new ModalManager(this.activeModal);

        const modalOverlay = this.querySelector('.modal-overlay');
        modalOverlay.addEventListener('click', () => this.modalManager.hideModal());

        const closeBtn = this.querySelector('#closeBtn');
        closeBtn.addEventListener('click', () => {
            this.modalManager.hideModal();
            this.removeModal();
        });
    }

	setupAccountListeners() {
		const saveChangesBtn = this.querySelector('#saveChanges');
		saveChangesBtn.addEventListener('click', () => this.accountManager.saveChanges());
	}

	setupPasswordListeners() {
		const saveChangesBtn = this.querySelector('#saveChanges');
		saveChangesBtn.addEventListener('click', () => this.passwordManager.saveChanges());
	}

    setupTwoFactorAuthListeners() {
        const enable2faToggle = this.querySelector('#enable2fa');
        enable2faToggle.addEventListener('change', () => this.twoFactorAuthManager.toggle2FA());

        const saveChangesBtn = this.querySelector('#saveChanges');
        saveChangesBtn.addEventListener('click', () => this.twoFactorAuthManager.saveChanges());
    }

    getModalHTML(modalConfig) {
		const footer = this.activeModal !== 'blockedUsers' ? modalConfig.footer() : '';
        return `
            <div class="modal-overlay"></div>
            <div class="modal fade" id="${this.activeModal}" tabindex="-1" aria-labelledby="${this.activeModal}Label" aria-hidden="false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        ${this.getModalHeaderHTML(modalConfig.title)}
                        ${modalConfig.content()}
						${footer ? footer : ''}
                    </div>
                </div>
            </div>
        `;
    }

    getModalHeaderHTML(title) {
        return `
            <div class="modal-header">
                <h5 class="modal-title" id="${this.activeModal}Label">${title}</h5>
                <button id="closeBtn" type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
        `;
    }

	// || Boost Security  ||
    getBoostSecurityContent() {
        return `
            <div class="modal-body animated">
                ${this.getTwoFactorAuthToggleHTML()}
                ${this.getTwoFactorAuthSetupHTML()}
                <div id="messageAlert" class="alert d-none" role="alert">
                    <span id="messageText" class="small"></span>
                    <button type="button" class="btn-close" aria-label="Close"></button>
                </div>
            </div>
        `;
    }

    getBoostSecurityFooter() {
        return `
            <div class="modal-footer ${this.twoFactorEnabled ? 'd-none' : 'block'}">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="saveChanges" disabled>Set up</button>
            </div>
        `;
    }

    getTwoFactorAuthToggleHTML() {
        const guideOne = 'Toggle the switch to disable 2FA.';
        const guideTwo = 'Toggle the switch to begin setting up Two-Factor Authentication.';
        return `
            <div class="step" id="switch">
                <div class="toggle-container">
                    <span id="stepTitle" class="step-title">${this.twoFactorEnabled ? 'Disable 2FA' : 'Enable 2FA'}</span>
                    <label class="toggle">
                        <input type="checkbox" id="enable2fa" ${this.twoFactorEnabled ? 'checked' : ''}>
                        <span class="slider"></span>
                    </label>
                </div>
                <p id="guide">${this.twoFactorEnabled ? guideOne : guideTwo}</p>
            </div>
        `;
    }

    getTwoFactorAuthSetupHTML() {
        return `
            <div id="setup2fa" class="${this.twoFactorEnabled ? 'd-none' : 'block'}">
                <h2 class="text-center mb-4">Authentication Hub</h2>
                <p class="text-muted">
                    Use an authenticator app like Google Authenticator, Microsoft Authenticator, Authy, or 1Password to scan this QR code. It will generate a 6-digit code for you to enter below.
                </p>
                <div class="qr-code position-relative" id="qrCode">
                    <div class="qr-scanner"></div>
                </div>
                <div class="mb-3">
                    <label for="authCode" class="form-label">Enter Authentication Code</label>
                    <input type="text" minlength="6" maxlength="6" class="form-control" id="authCode" placeholder="6-digit code">
                </div>
                <p class="text-muted small">
                    <i class="bi bi-info-circle"></i> 
                </p>
            </div>
        `;
    }

	// || Account ||
	getAccountContent() {
		return `
			<div class="modal-body animated">
				<div class="profile-card">
					<div class="text-center mb-4">
						<div class="position-relative d-inline-block">
							<img src="../images/loading.gif" alt="profile picture" class="profile-image" id="profilePicture">
							<span class="online-badge"></span>
						</div>
						<h2 id="profileName" class="profile-name mt-3">Sara Tancredi</h2>
						<p id="profileId" class="profile-id">New York, USA</p>
					</div>
					
					<form>
						<div class="row mb-3">
							<div class="col-12">
								<label for="tournament_name" class="form-label">Tournament Name</label>
								<input type="text" class="form-control" id="tournament_name">
							</div>
						</div>

						<div class="row mb-3">
							<div class="col-12">
								<label for="firstName" class="form-label">First Name</label>
								<input type="text" class="form-control" id="firstName">
							</div>
						</div>
						
						<div class="row mb-3">
							<div class="col-12">
								<label for="lastname" class="form-label">Last Name</label>
								<input type="text" class="form-control" id="lastName">
							</div>
						</div>
					</form>
       			 </div>
				<div id="messageAlert" class="alert d-none" role="alert">
					<span id="messageText" class="small"></span>
					<button type="button" class="btn-close" aria-label="Close"></button>
				</div>
			</div>
		`;
	}

	getAccountFooter() {
		return `
			<div class="modal-footer text-center">
				<button id="saveChanges" type="submit" class="btn btn-primary save-button px-4 py-2">Save Changes</button>
			</div>
		`;
	}

	// || Password ||
	getPasswordContent() {
		return `
			<div class="modal-body text-center animated">
				<img src="/images/padlock.png" style="width: 80px; height: 80px" alt="Password" class="password-image mb-2">
				<h2 class="text-center">Change your password</h2>
				<p class="text-muted text-center mb-4">Enter your current password and a new password to change your password.</p>
				<form id="passwordForm">
					<div class="mb-3">
						<div class="input-group">
							<span class="input-group-text"><i class="fas fa-lock"></i></span>
							<input type="password" class="form-control" id="currentPassword" placeholder="Current Password" required>
						</div>
					</div>
					<div class="mb-3">
						<div class="input-group">
							<span class="input-group-text"><i class="fas fa-key"></i></span>
							<input type="password" class="form-control" id="newPassword" placeholder="New Password" required>
						</div>
						<div class="password-strength"></div>
					</div>
					<div class="mb-3">
						<div class="input-group">
							<span class="input-group-text"><i class="fas fa-check"></i></span>
							<input type="password" class="form-control" id="confirmPassword" placeholder="Confirm Password" required>
						</div>
					</div>
				</form>
				<div id="messageAlert" class="alert d-none" role="alert">
					<span id="messageText" class="small"></span>
					<button type="button" class="btn-close" aria-label="Close"></button>
				</div>
			</div>
		`;
	}

	getPasswordFooter() {
		return `
			<div class="modal-footer text-center">
				<button id="saveChanges" type="submit" class="btn btn-primary save-button px-4 py-2">Save Changes</button>
			</div>
		`;
	}

	// || Blocked Users ||
	getBlockedUsersContent() {
		return `
		<div class="modal-body">
        	<div id="blockedUsersList" class="row g-4">
          		<!-- Blocked users will be dynamically added here -->
        	</div>
			<div id="messageAlert" class="alert d-none" role="alert">
				<span id="messageText" class="small"></span>
				<button type="button" class="btn-close" aria-label="Close"></button>
			</div>
      	</div>
		`;
	}

    removeModal() {
        const modal = this.querySelector('.modal');
        const overlay = this.querySelector('.modal-overlay');
        if (modal) modal.remove();
        if (overlay) overlay.remove();
        this.activeModal = null;
    }

	async unblockUser(username) {
		try {
			const response = await api.unblockUser(username);
			if (response === null) {
				console.log('User unblocked successfully.');
			}
		}
		catch (error) {
			console.error('Error unblocking user:', error);
		}
	}

	async renderBlockedUsers() {

		if (this.blockedUsers.length === 0) {
			const blockedUsersList = document.getElementById('blockedUsersList');
			blockedUsersList.innerHTML = `
				<div class="alert alert-info" role="alert">
					You have not blocked any users.
				</div>
			`;
			return;
		}

		const blockedUsersList = document.getElementById('blockedUsersList');
		blockedUsersList.innerHTML = '';
	
		this.blockedUsers.forEach(user => {
			const userCard = document.createElement('div');
			userCard.className = 'col-md-6 col-lg-6';
			userCard.innerHTML = `
				<div class="user-card card h-100">
					<div class="card-body text-center">
						<img src="${user.avatarUrl}" alt="${user.username}'s avatar" class="user-avatar mb-3">
						<h5 class="card-title">${user.username}</h5>
						<p class="card-text text-muted">${user.firstName} ${user.lastName}</p>
						<button class="btn btn-success unblock-btn" id="unblockButton">Unblock</button>
					</div>
				</div>
			`;
			blockedUsersList.appendChild(userCard);
		});

		const unblockButtons = document.querySelectorAll('.unblock-btn');
		unblockButtons.forEach((button, index) => {
			button.addEventListener('click', () => {
				this.unblockUser(this.blockedUsers[index].username);
				this.blockedUsers.splice(index, 1);
				this.renderBlockedUsers();
			});
		});
	}

	// || Game Settings ||
	gameSettingsContent() {
		return `
			<div class="modal-body">
				
				<div class="row g-4">
					<!-- Board Color Section -->
					<div class="col-12">
						<div class="color-picker-group p-3 bg-light rounded-3 shadow-sm">
							<div class="d-flex align-items-center justify-content-between">
								<label class="form-label h6 mb-3">
									<i class="fas fa-palette me-2"></i>Board Color
								</label>
								<div class="color-preview rounded-circle shadow-sm" id="boardPreview"></div>
							</div>
							<select class="form-select form-select-lg bg-white border-0 shadow-sm" id="boardColor">
								<option value="#000000">Midnight Black</option>
								<option value="#1E1E1E">Carbon Gray</option>
								<option value="#2C3E50">Ocean Blue</option>
								<option value="#2E4053">Twilight Gray</option>
								<option value="#34495E">Storm Blue</option>
							</select>
						</div>
					</div>
		
					<!-- Paddles Color Section -->
					<div class="col-12">
						<div class="color-picker-group p-3 bg-light rounded-3 shadow-sm">
							<div class="d-flex align-items-center justify-content-between">
								<label class="form-label h6 mb-3">
									<i class="fas fa-table-tennis me-2"></i>Paddles Color
								</label>
								<div class="color-preview rounded-circle shadow-sm" id="paddlePreview"></div>
							</div>
							<select class="form-select form-select-lg bg-white border-0 shadow-sm" id="paddleColor">
								<option value="#FFFFFF">Pure White</option>
								<option value="#FF0000">Racing Red</option>
								<option value="#00FF00">Neon Green</option>
								<option value="#0000FF">Electric Blue</option>
								<option value="#FFA500">Blazing Orange</option>
							</select>
						</div>
					</div>
		
					<!-- Ball Color Section -->
					<div class="col-12">
						<div class="color-picker-group p-3 bg-light rounded-3 shadow-sm">
							<div class="d-flex align-items-center justify-content-between">
								<label class="form-label h6 mb-3">
									<i class="fas fa-circle me-2"></i>Ball Color
								</label>
								<div class="color-preview rounded-circle shadow-sm" id="ballPreview"></div>
							</div>
							<select class="form-select form-select-lg bg-white border-0 shadow-sm" id="ballColor">
								<option value="#FFFFFF">Classic White</option>
								<option value="#FFD700">Golden Shine</option>
								<option value="#FF69B4">Neon Pink</option>
								<option value="#7FFF00">Lime Flash</option>
								<option value="#9B59B6">Royal Purple</option>
							</select>
						</div>
					</div>
				
				</div>
				
			</div>
		`;
	}
}

customElements.define("settings-page", SettingsPage);