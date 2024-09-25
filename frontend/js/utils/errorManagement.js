export function displayRequestStatus(type, message) {
    const error = document.createElement("div");
    error.classList.add("error", type);
    error.innerHTML = `
          <span>${message}</span>
          <span class="close-btn">&times;</span>
      `;
  
    const errorManager = document.getElementById("error-management");
    errorManager.appendChild(notification);

    setTimeout(() => {
      error.classList.add("show");
    }, 100);

    setTimeout(() => {
      removeNotification(error);
    }, 5000);

    error.querySelector(".close-btn").addEventListener("click", () => {
      removeNotification(error);
    });
  }
  
  function removeNotification(error) {
    error.classList.remove("show");
    setTimeout(() => {
      error.remove();
    }, 500);
}
