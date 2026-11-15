from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_SESSION
from app.dependencias import ConexionDepend, UserDepend, Estudiante_Depend, Profesor_Depend, Administrador_Depend
from app.repositorio import obtener_estudiante_por_usuario_id, obtener_proyectos, seguimiento_horas_del_estudiante, horas_obtenidas, obtener_estudiantes
from app.seguridad import create_access_token
from app.servicios import autenticar_usuario, resumen_mis_proyectos


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
async def home(request: Request, usuario: UserDepend):
    return templates.TemplateResponse(
        request=request, name="panel_estudiante.html", context={"usuario": usuario}
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
    conexion: ConexionDepend
):
    estudiantes = await obtener_estudiantes(conexion)
    return templates.TemplateResponse(
        request=request, name="panel_profesor.html", context={"usuario": usuario, "estudiantes": estudiantes}
    )

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


