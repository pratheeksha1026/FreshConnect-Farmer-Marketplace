// Small progressive enhancement: confirm before deleting a demo listing.
document.addEventListener("submit", function (event) {
  if (event.target.matches("[data-confirm-delete]")) {
    if (!window.confirm("Remove this listing? This demo action cannot be undone.")) {
      event.preventDefault();
    }
  }
});
