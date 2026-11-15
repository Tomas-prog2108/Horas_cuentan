const contenedor = document.getElementById('barraProgreso');

const horasMeta = Number(contenedor.dataset.horasMeta);
const horasObtenidas = Number(contenedor.dataset.horasObtenidas);

function escaparHTML(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

function barraProgreso(horasMeta, horasObtenidas) {
    const porcentaje = horasMeta > 0
    ? Math.min(100, Math.round((horasObtenidas/horasMeta)*100))
    : 0;

    document.getElementById('textoPorcentaje').textContent = porcentaje + '%';
    document.getElementById('barraProgreso').style.width = porcentaje + '%';

    const contenedorBarra = document.querySelector('.contenedor-barra');
    contenedorBarra.setAttribute('aria-valuenow', horasObtenidas);
    contenedorBarra.setAttribute('aria-valuemax', horasMeta);
}

// "2026-06-10" -> "10/06/2026"
function formatearFecha(iso) {
    const partes = iso.split('-');
    return partes[2] + '/' + partes[1] + '/' + partes[0];
}

/*
// PASO 1 — ACTUALIZAR EL RESUMEN
// El servidor ya suma solo las horas aprobadas.
function actualizarResumen(horasCompletadas, horasTotales) {
    const porcentaje = horasTotales > 0
        ? Math.min(100, Math.round((horasCompletadas / horasTotales) * 100))
        : 0;

    document.getElementById('horasCompletadas').textContent = horasCompletadas;
    document.getElementById('horasTotales').textContent = horasTotales;
    document.getElementById('textoPorcentaje').textContent = porcentaje + '%';
    document.getElementById('barraProgreso').style.width = porcentaje + '%';

    const contenedorBarra = document.querySelector('.contenedor-barra');
    contenedorBarra.setAttribute('aria-valuenow', horasCompletadas);
    contenedorBarra.setAttribute('aria-valuemax', horasTotales);
}


// PASO 2 — BADGE DE ESTADO (solo pendiente / aprobado)
function crearBadge(estado) {
    const estados = {
        aprobado:  { clase: 'badge-aprobado',  texto: 'Aprobado' },
        pendiente: { clase: 'badge-pendiente', texto: 'Pendiente' }
    };
    const info = estados[estado] || { clase: 'badge-pendiente', texto: estado };
    return `<span class="badge ${info.clase}">${escaparHTML(info.texto)}</span>`;
}


// PASO 3 — BOTONES DE EVIDENCIA (uno por foto, o un guion si no hay)
function crearEvidencias(evidencias) {
    if (!evidencias || evidencias.length === 0) {
        return '<span title="Sin evidencia">—</span>';
    }
    return evidencias.map(function (url, i) {
        return `<a class="btn-evidencia" href="${encodeURI(url)}" target="_blank" rel="noopener"
                   title="Ver evidencia ${i + 1}">👁️</a>`;
    }).join(' ');
}


// PASO 4 — LLENAR LAS TABLAS
function llenarTablas(actividades) {
    const cuerpoResumen   = document.getElementById('cuerpoTablaResumen');
    const cuerpoHistorial = document.getElementById('cuerpoTablaHistorial');

    cuerpoResumen.innerHTML   = '';
    cuerpoHistorial.innerHTML = '';

    if (actividades.length === 0) {
        const vacio = '<tr><td colspan="5">Aún no has registrado horas.</td></tr>';
        cuerpoResumen.innerHTML   = vacio;
        cuerpoHistorial.innerHTML = vacio;
        return;
    }

    actividades.forEach(function (a) {
        const proyecto = escaparHTML(a.proyecto);
        const fecha    = formatearFecha(a.fecha);

        const filaResumen = document.createElement('tr');
        filaResumen.innerHTML = `
            <td>${proyecto}</td>
            <td>${fecha}</td>
            <td>${a.horas}</td>
            <td>${crearBadge(a.estado)}</td>
        `;
        cuerpoResumen.appendChild(filaResumen);

        const filaHistorial = document.createElement('tr');
        filaHistorial.innerHTML = `
            <td>${proyecto}</td>
            <td>${fecha}</td>
            <td>${a.horas}</td>
            <td>${crearBadge(a.estado)}</td>
            <td>${crearEvidencias(a.evidencias)}</td>
        `;
        cuerpoHistorial.appendChild(filaHistorial);
    });
}

*/

function iniciarPestanas() {
    const btnResumen     = document.getElementById('btnResumen');
    const btnHistorial   = document.getElementById('btnHistorial');
    const vistaResumen   = document.getElementById('vistaResumen');
    const vistaHistorial = document.getElementById('vistaHistorial');

    btnResumen.addEventListener('click', function () {
        vistaResumen.classList.remove('oculto');
        vistaHistorial.classList.add('oculto');
        btnResumen.classList.add('activa');
        btnHistorial.classList.remove('activa');
    });

    btnHistorial.addEventListener('click', function () {
        vistaHistorial.classList.remove('oculto');
        vistaResumen.classList.add('oculto');
        btnHistorial.classList.add('activa');
        btnResumen.classList.remove('activa');
    });
}


// PASO 6 — PEDIR LOS DATOS AL SERVIDOR
async function cargarDatos() {
    try {
        const respuesta = await fetch('/api/mis_horas');

        if (respuesta.status === 401) {       // sesión vencida
            window.location.href = '/';
            return;
        }

        const datos = await respuesta.json();
        actualizarResumen(datos.horas_completadas, datos.horas_totales);
        llenarTablas(datos.actividades);
    } catch (error) {
        console.error('No se pudieron cargar las horas:', error);
    }
}


document.addEventListener('DOMContentLoaded', function () {
    iniciarPestanas();
    cargarDatos();
    barraProgreso(horasMeta, horasObtenidas);

    setTimeout(function () {
        document.querySelector('.seguimiento').classList.add('visible');
    }, 100);
});
