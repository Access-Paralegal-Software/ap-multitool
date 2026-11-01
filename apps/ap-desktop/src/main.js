document.addEventListener("DOMContentLoaded", () => {
  const statusEl = document.getElementById("appliance-status");
  if (statusEl) {
    statusEl.textContent = "Ready (Local Engine)";
  }
});
