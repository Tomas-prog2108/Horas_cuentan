function obtenerIniciales(nombre) {
    const palabras = nombre.trim().split(' ');

    const iniciales = palabras
        .slice(0,2)
        .map(function(palabra){
            return palabra[0] || '';
        })

        .join('');
    return iniciales.toUpperCase();
}

document.addEventListener('DOMContentLoaded', function() {
    const tarjetas = document.querySelectorAll('.tarjeta-estudiante');

    tarjetas.forEach(function(tarjeta){
        const nombreEstudiante = tarjeta.dataset.nombre;

        if (nombreEstudiante) {
            const iniciales = obtenerIniciales(nombreEstudiante);
            const divAvatar = tarjeta.querySelector('.avatar');

            if (divAvatar) {
                divAvatar.textContent = iniciales;
            }
        }
    })
})

function mostraEstudiantesFiltrados(documentoBuscado) {
    const tarjetas = document.querySelectorAll('.tarjeta-estudiante');
    const mensajeVacio = document.getElementById('mensajeVacio');

    let tarjetasVisibles = 0;

    tarjetas.forEach(function(tarjeta) {
        const documentoEstudiante = tarjeta.dataset.identificacion;
        
        if (documentoEstudiante.startsWith(documentoBuscado)) {
            tarjeta.style.display = 'flex';
            tarjetasVisibles++;
        } else {
            tarjeta.style.display = 'none';
        }
    });

    if (tarjetasVisibles === 0) {
        mensajeVacio.classList.remove('oculto');
    } else {
        mensajeVacio.classList.add('oculto')
    }
}

function Iniciarbusqueda() {
    const input = document.getElementById('busqueda');

    if (!input) return;

    input.addEventListener('input', function(){
        const textoBuscado = input.value.trim();

        mostraEstudiantesFiltrados(textoBuscado)
    });
}

document.addEventListener("click", (e) => {
  const tarjeta = e.target.closest(".tarjeta-estudiante");
  if (!tarjeta) return;
  window.location.href =
    "/registrar_horas/" + encodeURIComponent(tarjeta.dataset.identificacion);
});
/*
async function cargarEStudiantes(){
    try{
        const respuesta = await fetch('/api/estudiantes');
        todosLosEstudiantes = await respuesta.json();
        mostraEstudiantes(todosLosEstudiantes)

    } catch (error) {
        console.error('Error al cargar los estudiantes', error);
    }
}


function crearTarjeta(estudiante) {
    const li = document.createElement('li');
    li.className = 'tarjeta-estudiante';

    const iniciales = obtenerIniciales(estudiante.nombre);
    li.innerHTML = `
        <div class="contenedor-avatar-info">
            <div class="avatar">${iniciales}</div>
            <div>
                <p class="nombre-estudiante">${estudiante.nombre}</p>
                <p class="detalle-estudiante">
                    ${estudiante.grado} · Documento: ${estudiante.documento}
                </p>
            </div>
        </div>
        <span class="flecha-tarjeta"><i class="fa-solid fa-angle-right"></i></span>
    `;

    // Al hacer clic en la tarjeta, se abre la pantalla de "Registrar
    // horas" con este estudiante ya preseleccionado.
    li.addEventListener('click', function () {
        window.location.href = `/registrar_horas/${estudiante.documento}`;
    });

    return li;

}


function mostraEstudiantes(lista) {
    const contenedor = document.getElementById('listaEstudiantes');
    const mensajeVacio = document.getElementById('mensajeVacio');

    contenedor.innerHTML = '';

    if (lista.length === 0) {
        mensajeVacio.classList.remove('oculto');

    } else {
        mensajeVacio.classList.add('oculto');

        lista.forEach(function(estudiante){
            const tarjeta = crearTarjeta(estudiante);
            contenedor.appendChild(tarjeta);
        });
    }
}

function Iniciarbusqueda(){
    const input = document.getElementById('busqueda');

    input.addEventListener('input', function(){
        const textoBuscado = input.value.toLowerCase();

        if(textoBuscado === ''){
            mostraEstudiantes(todosLosEstudiantes);
            return;
        }

        const resultados = todosLosEstudiantes.filter(function(estudiante){
            return estudiante.documento.startsWith(textoBuscado);
        });
        mostraEstudiantes(resultados);
    });
}
*/

document.addEventListener('DOMContentLoaded', async function () {    
    Iniciarbusqueda();
    mostraEstudiantesFiltrados('');
 
    setTimeout(function() {
        document.querySelector('.main').classList.add('visible')
    }, 100);
    
});
