import { MessageHandler } from './MessageHandler.js';

/**
 * GameManager Class
 * 
 */

export class GameManager {
	constructor() {

		this.boardColor = document.getElementById('boardColor');
		this.boardPreview = document.getElementById('boardPreview');

		this.paddleColor = document.getElementById('paddleColor');
		this.paddlePreview = document.getElementById('paddlePreview');

		this.ballColor = document.getElementById('ballColor');
		this.ballPreview = document.getElementById('ballPreview');

		this.alertElement = document.getElementById('messageAlert');
		this.messageElement = document.getElementById('messageText');

		this.setInitialValues();

		this.setupEventListeners();
	}

	setInitialValues() {
		// set initial values for color pickers from local storage
		this.boardColor.value = localStorage.getItem('boardColor') || '#000000';
		this.boardPreview.style.backgroundColor = this.boardColor.value;

		this.paddleColor.value = localStorage.getItem('paddleColor') || '#000000';
		this.paddlePreview.style.backgroundColor = this.paddleColor.value;

		this.ballColor.value = localStorage.getItem('ballColor') || '#000000';
		this.ballPreview.style.backgroundColor = this.ballColor.value;
	}

	setupEventListeners() {
		this.boardColor.addEventListener('input', () => {
			this.boardPreview.style.backgroundColor = this.boardColor.value;
			localStorage.setItem('boardColor', this.boardColor.value);
		});

		this.paddleColor.addEventListener('input', () => {
			this.paddlePreview.style.backgroundColor = this.paddleColor.value;
			localStorage.setItem('paddleColor', this.paddleColor.value);
		});

		this.ballColor.addEventListener('input', () => {
			this.ballPreview.style.backgroundColor = this.ballColor.value;
			localStorage.setItem('ballColor', this.ballColor.value);
		});
	}
	
}