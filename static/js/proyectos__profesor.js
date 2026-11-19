document.addEventListener("click", (e) => {
  const card = e.target.closest(".card[data-href]");
  if (!card) return;
  if (e.target.closest("button, a")) return;
  window.location.href = card.dataset.href;
});

document.body.addEventListener("htmx:responseError", (e) => {
  alert(e.detail.xhr.responseText || "No se pudo completar la acción.");
});

document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelector('.main').classList.add('visible');
    }, 100);
});
