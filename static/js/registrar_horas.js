
document.addEventListener("DOMContentLoaded", () => {
  const horaInicio = document.getElementById("hora_inicio");
  const horaFin = document.getElementById("hora_fin");
  const salida = document.getElementById("horasCalculadas");

  function aMinutos(valor) {
    if (!valor) return null;
    const [h, m] = valor.split(":").map(Number);
    return h * 60 + m;
  }

  function calcular() {
    const ini = aMinutos(horaInicio.value);
    const fin = aMinutos(horaFin.value);

    horaFin.setCustomValidity("");

    if (ini === null || fin === null) {
      salida.textContent = "0 horas";
      return;
    }
    if (fin <= ini) {
      salida.textContent = "0 horas";
      horaFin.setCustomValidity("La hora de finalización debe ser posterior a la de inicio.");
      return;
    }

    const horas = (fin - ini) / 60;
    salida.textContent = `${Number(horas.toFixed(2))} ${horas === 1 ? "hora" : "horas"}`;
  }

  ["input", "change"].forEach((ev) => {
    horaInicio.addEventListener(ev, calcular);
    horaFin.addEventListener(ev, calcular);
  });
  calcular(); 
});

setTimeout(function () {
        document.querySelector('.main').classList.add('visible');
    }, 100);
