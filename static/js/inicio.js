const contenedor = document.getElementById('disp-total');
const contenedor1 = document.getElementById('disp-done');

let state = {
  done: Number(contenedor1.dataset.horasObtenidas),
  total: Number(contenedor.dataset.horasMeta),
  role: null
};

// ── Progress rendering ────────────────────────────────────────
function renderProgress() {
  const pct = Math.min(100, Math.max(0, Math.round(state.done / state.total * 100)));

  document.getElementById('disp-done').textContent  = state.done;
  document.getElementById('disp-total').textContent = state.total;
  document.getElementById('pct-label').textContent  = pct + '%';
  document.getElementById('donut-pct').textContent  = pct + '%';

  // CSS variable drives both bar and donut via CSS calc()
  document.documentElement.style.setProperty('--progress-done', pct);

  // Donut (manual because CSS var in SVG stroke-dashoffset is limited on some browsers)
  const circumference = 2 * Math.PI * 40; // 251.2
  const offset = circumference * (1 - pct / 100);
  document.getElementById('donut-fill').style.strokeDashoffset = offset;

  // Bar
  document.getElementById('bar-fill').style.width = pct + '%';
}


setTimeout(function() {
  document.querySelector('.main').classList.add('visible');
}, 100);

renderProgress();