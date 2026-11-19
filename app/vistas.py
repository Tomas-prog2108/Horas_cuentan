from datetime import timedelta, date, time
from typing import Annotated
import asyncpg

from fastapi import APIRouter, Form, Request, status, File, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_SESSION
from app.dependencias import ConexionDepend, UserDepend, Estudiante_Depend, Profesor_Depend, Administrador_Depend, PerfilProfesorDepend
from app.repositorio import (obtener_estudiante_por_usuario_id, obtener_proyectos, seguimiento_horas_del_estudiante,
                              horas_obtenidas, obtener_estudiantes, actualizar_proyecto, crear_proyecto, eliminar_proyecto, 
                              listar_inscritos, listar_proyectos_del_profesor, obtener_proyecto_del_profesor, obtener_estudiantes_del_profesor,
                              proyectos_para_registrar, obtener_estudiante_por_identificacion)
from app.seguridad import create_access_token
from app.servicios import autenticar_usuario, resumen_mis_proyectos, ErrorRegistroHoras, registrar_horas_estudiante, ErrorInscripcion, inscribir_estudiante
from app.modelos import ProyectoForm


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
async def home(
    request: Request, 
    usuario: UserDepend,
    conexion: ConexionDepend):
    estudiante = await obtener_estudiante_por_usuario_id(conexion, usuario.id)
    horas = await horas_obtenidas(conexion, estudiante["id_estudiante"])
    return templates.TemplateResponse(
        request=request, name="panel_estudiante.html", context={"usuario": usuario, "estudiante": estudiante, "horas": horas}
    )

@router.get("/estudiante")
async def panel_estudiante(
    request: Request,
    usuario: Estudiante_Depend,
    conexion: ConexionDepend
):
    estudiante = await obtener_estudiante_por_usuario_id(conexion, usuario.id)
    horas = await horas_obtenidas(conexion, estudiante["id_estudiante"])
    return templates.TemplateResponse(
        request=request, name="panel_estudiante.html", context={"usuario": usuario, "estudiante": estudiante, "horas": horas}
    )

@router.get("/administrador")
async def panel_administrador(
    request: Request,
    usuario: Administrador_Depend
):
    return templates.TemplateResponse(
        request=request, name="panel_administrador.html", context={"usuario": usuario}
    )

@router.get("/profesor")
async def panel_profesor(
    request: Request,
    usuario: Profesor_Depend,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    estudiantes = await obtener_estudiantes_del_profesor(conexion, perfil["id_profesor"])
    return templates.TemplateResponse(
        request=request,
        name="panel_profesor.html",
        context={"usuario": usuario, "estudiantes": estudiantes},
    )

async def _render_registro(
    request, usuario, conexion, perfil, estudiante, documento,
    proyecto_preseleccionado=None, valores=None, error=None, status_code=200,
):
    proyectos = await proyectos_para_registrar(
        conexion, estudiante["id_estudiante"], perfil["id_profesor"]
    )
    return templates.TemplateResponse(
        request=request,
        name="registrar_horas.html",
        context={
            "usuario": usuario,
            "estudiante": estudiante,
            "documento": documento,
            "proyectos": proyectos,
            "proyecto_preseleccionado": proyecto_preseleccionado,
            "valores": valores or {},
            "error": error,
        },
        status_code=status_code,
    )


@router.get("/registrar_horas/{documento}")
async def formulario_registrar_horas(
    documento: str,
    request: Request,
    usuario: Profesor_Depend,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
    proyecto: int | None = None,
):
    estudiante = await obtener_estudiante_por_identificacion(conexion, documento)
    if estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    return await _render_registro(
        request, usuario, conexion, perfil, estudiante, documento,
        proyecto_preseleccionado=proyecto,
    )


@router.post("/registrar_horas/{documento}")
async def guardar_horas(
    documento: str,
    request: Request,
    usuario: Profesor_Depend,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
    proyecto_id: Annotated[int, Form()],
    fecha: Annotated[date, Form()],
    hora_inicio: Annotated[time, Form()],
    hora_fin: Annotated[time, Form()],
    observaciones: Annotated[str, Form()] = "",
    evidencia: Annotated[UploadFile | None, File()] = None,
):
    estudiante = await obtener_estudiante_por_identificacion(conexion, documento)
    if estudiante is None:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")

    try:
        await registrar_horas_estudiante(
            conexion,
            profesor_id=perfil["id_profesor"],
            estudiante_id=estudiante["id_estudiante"],
            proyecto_id=proyecto_id,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            observaciones=observaciones,
            evidencia=evidencia,
        )
    except ErrorRegistroHoras as e:
        return await _render_registro(
            request, usuario, conexion, perfil, estudiante, documento,
            proyecto_preseleccionado=proyecto_id,
            valores={
                "fecha": fecha.isoformat(),
                "hora_inicio": hora_inicio.strftime("%H:%M"),
                "hora_fin": hora_fin.strftime("%H:%M"),
                "observaciones": observaciones,
            },
            error=str(e),
            status_code=422,
        )

    return RedirectResponse("/profesor", status_code=status.HTTP_303_SEE_OTHER)
    

@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        request=request, name="login.html", context={"error": None}
    )


@router.post("/login")
async def entrar(
    request: Request,
    conexion: ConexionDepend,
    identificacion: Annotated[str, Form()],
    contrasena: Annotated[str, Form()],
):
    usuario = await autenticar_usuario(conexion, identificacion, contrasena)
    if usuario is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "La identificacion o contraseña incorrectos."},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = create_access_token(
        data={
            "sub": usuario.identificacion,
            "rol": usuario.rol,
        },
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    if usuario.rol == "estudiante":
        destino = "/estudiante"

    elif usuario.rol == "profesor":
        destino = "/profesor"

    elif usuario.rol == "administrador":
        destino = "/administrador"

    else:
        destino = "/login"

    respuesta = RedirectResponse(destino, status_code=status.HTTP_303_SEE_OTHER)
    respuesta.set_cookie(
        key=COOKIE_SESSION,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax",
        # En producción, servir la app tras HTTPS y añadir secure=True.
    )
    return respuesta


@router.get("/logout")
async def salir():
    respuesta = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    respuesta.delete_cookie(COOKIE_SESSION)
    return respuesta

@router.get("/estudiante/proyectos")
async def ver_proyectos(
    request: Request,
    usuario: Estudiante_Depend,
    conexion: ConexionDepend,
):
    proyectos = await obtener_proyectos(conexion)
    return templates.TemplateResponse(
        request=request,
        name="proyectos_disponibles.html",
        context={"usuario": usuario, "proyectos": proyectos},
    )

@router.get("/estudiante/mis-proyectos")
async def mis_proyectos(
    request: Request,
    usuario: Estudiante_Depend,
    conexion: ConexionDepend,
):
    perfil = await obtener_estudiante_por_usuario_id(conexion, usuario.id)

    if perfil is None:
        resumen = {
            "proyectos": [],
            "stats": {"inscritos": 0, "obtenidas": 0, "totales": 0,
                      "pendientes": 0, "completados": 0},
        }
    else:
        resumen = await resumen_mis_proyectos(conexion, perfil["id_estudiante"])

    return templates.TemplateResponse(
        request=request,
        name="mis-proyectos.html",  # ajusta a tu nombre
        context={"usuario": usuario, **resumen},
    )

@router.get("/estudiante/seguimiento_horas")
async def seguimiento_horas(
    request:Request,
    usuario: Estudiante_Depend,
    conexion: ConexionDepend,
):
    perfil = await obtener_estudiante_por_usuario_id(conexion, usuario.id)
    horas = await horas_obtenidas(conexion, perfil["id_estudiante"])
    resumen = await seguimiento_horas_del_estudiante(conexion, perfil["id_estudiante"])

    return templates.TemplateResponse(
        request=request,
        name="seguimiento_horas.html",
        context={"usuario": usuario, "resumen": resumen, "perfil": perfil, "horas": horas}
    )

async def _proyecto_o_404(conexion, proyecto_id: int, profesor_id: int) -> dict:
    proyecto = await obtener_proyecto_del_profesor(conexion, proyecto_id, profesor_id)
    if proyecto is None:
        # 404 y no 403: no revelamos que el proyecto existe pero es de otro
        raise HTTPException(status_code=404, detail="Proyecto no encontrado.")
    return proyecto


@router.get("/g_proyectos")
async def g_proyectos(
    request: Request,
    usuario: Profesor_Depend,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    proyectos = await listar_proyectos_del_profesor(conexion, perfil["id_profesor"])
    return templates.TemplateResponse(
        request=request,
        name="proyectos_profesor.html",
        context={"usuario": usuario, "proyectos": proyectos},
    )


# ¡"nuevo" va ANTES de "{proyecto_id}"!
@router.get("/g_proyectos/nuevo")
async def formulario_nuevo(
    request: Request, usuario: Profesor_Depend, perfil: PerfilProfesorDepend
):
    return templates.TemplateResponse(
        request=request,
        name="crear_proyecto.html",
        context={
            "usuario": usuario, "profesor": perfil, "proyecto": None,
            "accion": "/g_proyectos/nuevo", "titulo": "Crear nuevo proyecto",
        },
    )


@router.post("/g_proyectos/nuevo")
async def guardar_nuevo(
    datos: Annotated[ProyectoForm, Form()],
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    await crear_proyecto(conexion, perfil["id_profesor"], datos)
    return RedirectResponse("/g_proyectos", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/g_proyectos/{proyecto_id}")
async def detalle_proyecto(
    proyecto_id: int,
    request: Request,
    usuario: Profesor_Depend,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    proyecto = await _proyecto_o_404(conexion, proyecto_id, perfil["id_profesor"])
    inscritos = await listar_inscritos(conexion, proyecto_id)
    proyecto["cupos_disponibles"] = proyecto["cupos"] - len(inscritos)
    return templates.TemplateResponse(
        request=request,
        name="estudiantes_inscritos.html",
        context={
            "usuario": usuario, "proyecto": proyecto,
            "proyecto_id": proyecto_id, "inscritos": inscritos,
        },
    )


@router.get("/g_proyectos/{proyecto_id}/editar")
async def formulario_editar(
    proyecto_id: int,
    request: Request,
    usuario: Profesor_Depend,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    proyecto = await _proyecto_o_404(conexion, proyecto_id, perfil["id_profesor"])
    return templates.TemplateResponse(
        request=request,
        name="crear_proyecto.html",
        context={
            "usuario": usuario, "profesor": perfil, "proyecto": proyecto,
            "accion": f"/g_proyectos/{proyecto_id}/editar",
            "titulo": "Editar proyecto",
        },
    )


@router.post("/g_proyectos/{proyecto_id}/editar")
async def guardar_edicion(
    proyecto_id: int,
    datos: Annotated[ProyectoForm, Form()],
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    if not await actualizar_proyecto(conexion, proyecto_id, perfil["id_profesor"], datos):
        raise HTTPException(status_code=404, detail="Proyecto no encontrado.")
    return RedirectResponse("/g_proyectos", status_code=status.HTTP_303_SEE_OTHER)


@router.delete("/g_proyectos/{proyecto_id}")
async def borrar_proyecto(
    proyecto_id: int,
    perfil: PerfilProfesorDepend,
    conexion: ConexionDepend,
):
    try:
        eliminado = await eliminar_proyecto(conexion, proyecto_id, perfil["id_profesor"])
    except asyncpg.ForeignKeyViolationError:
        return PlainTextResponse(
            "No se puede eliminar: el proyecto ya tiene horas registradas. "
            "Edítalo y márcalo como inactivo.",
            status_code=409,
        )
    if not eliminado:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado.")
    return HTMLResponse("")

@router.post("/estudiante/proyectos/{proyecto_id}/inscribirse")
async def inscribirse(
    proyecto_id: int,
    usuario: Estudiante_Depend,
    conexion: ConexionDepend,
):
    perfil = await obtener_estudiante_por_usuario_id(conexion, usuario.id)
    if perfil is None:
        return JSONResponse(
            {"ok": False, "mensaje": "Tu usuario no tiene perfil de estudiante."},
            status_code=403,
        )

    try:
        await inscribir_estudiante(conexion, perfil["id_estudiante"], proyecto_id)
    except ErrorInscripcion as e:
        return JSONResponse(
            {"ok": False, "mensaje": str(e)}, status_code=e.status_code
        )

    return JSONResponse({"ok": True, "mensaje": "Te inscribiste correctamente"})


