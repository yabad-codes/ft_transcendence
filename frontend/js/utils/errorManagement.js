export function addNotification(type, message) {
    const notification = document.createElement("div");
    notification.classList.add("notification", type);
    notification.innerHTML = `
          <span>${message}</span>
          <span class="close-btn">&times;</span>
      `;
  
    const notifications = document.getElementById("notifications");
    notifications.appendChild(notification);

    setTimeout(() => {
      notification.classList.add("show");
    }, 100);

    setTimeout(() => {
      removeNotification(notification);
    }, 5000);

    notification.querySelector(".close-btn").addEventListener("click", () => {
      removeNotification(notification);
    });
  }
  
  function removeNotification(notification) {
    notification.classList.remove("show");
    setTimeout(() => {
      notification.remove();
    }, 500);
}
