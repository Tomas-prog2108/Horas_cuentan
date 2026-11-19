setTimeout(function() {
  document.querySelector('.main').classList.add('visible');
}, 100);

const botones = document.querySelectorAll(".btn-ins");



function avisoInscripcion(texto) {
  const s = document.getElementById("snackbar");
  s.textContent = texto;
  s.classList.add("show");          // usa la clase que tu CSS ya tenga para mostrarlo
  setTimeout(() => s.classList.remove("show"), 3000);
}

document.addEventListener("click", async (e) => {
  const boton = e.target.closest(".btn-ins");
  if (!boton || boton.disabled) return;

  boton.disabled = true;              
  try {
    const res = await fetch(
      `/estudiante/proyectos/${boton.dataset.idProyecto}/inscribirse`,
      { method: "POST" }
    );

    if (res.redirected) {        
      window.location.href = res.url;
      return;
    }

    const datos = await res.json();
    avisoInscripcion(datos.mensaje);

    if (datos.ok) {
      boton.textContent = "Inscrito";
    } else {
      boton.disabled = false;
    }
  } catch (err) {
    avisoInscripcion("No se pudo completar la inscripción. Intenta de nuevo.");
    boton.disabled = false;
  }
});