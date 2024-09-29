/**
 * ModalManager Class
 * 
 * The ModalManager class is responsible for managing the display 
 * of modals within the user interface. It provides methods to show 
 * and hide modals, as well as manage the overlay that appears 
 * behind the modal.
 * 
 * Key Responsibilities:
 * - Initialize and control the visibility of modals using Bootstrap's modal functionality.
 * - Manage the display of the modal overlay to enhance user experience.
 * 
 * This class simplifies modal management by encapsulating the logic 
 * required to show and hide modals and their associated overlays.
 */
export class ModalManager {
	/**
     * Constructor for the ModalManager class.
     * Initializes the modal instance and selects the modal overlay element.
     */

	constructor(modalId) {
		this.modalElement = document.getElementById(modalId);
        this.modal = new bootstrap.Modal(this.modalElement, {
            backdrop: false,
        });
        this.modalOverlay = document.querySelector('.modal-overlay');
        this.setupEventListeners();
	}

	/**
     * Sets up event listeners for the modal.
     */
    setupEventListeners() {
        this.modalElement.addEventListener('hidden.bs.modal', () => this.hideOverlay());
    }
  
	/**
     * Displays the modal and the overlay.
     */
	showModal() {
	  this.modal.show();
	  this.modalOverlay.style.display = 'block';
	}
  
	/**
     * Hides the modal and the overlay.
     */
	hideModal() {
	  this.modal.hide();
	//   this.hideOverlay();
	}
  
	/**
     * Hides the modal overlay.
     */
	hideOverlay() {
	  this.modalOverlay.style.display = 'none';
	}

	/**
     * Cleans up the modal manager by removing event listeners and destroying the modal instance.
     */
    cleanup() {
        this.modalElement.removeEventListener('hidden.bs.modal', this.hideOverlay);
        this.modal.dispose();
        this.modal = null;
        this.modalElement = null;
        this.modalOverlay = null;
    }

  }