export function displayRequestStatus(type, message) {
    const error = document.createElement("div");
    error.classList.add("error", type);
    error.innerHTML = `
          <span>${message}</span>
          <span class="close-btn">&times;</span>
      `;
  
    const errorManager = document.getElementById("error-management");
    errorManager.appendChild(error);

    setTimeout(() => {
      error.classList.add("show");
    }, 100);

    setTimeout(() => {
      removeError(error);
    }, 5000);

    error.querySelector(".close-btn").addEventListener("click", () => {
      removeError(error);
    });
  }
  
  function removeError(error) {
    error.classList.remove("show");
    setTimeout(() => {
      error.remove();
    }, 500);
}
