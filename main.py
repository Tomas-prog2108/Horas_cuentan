from contextlib import asynccontextmanager


from fastapi import FastAPI


from app.config import URL_DATABASE
from app.database import db
from app.vistas import router as vistas_router
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect(URL_DATABASE)
    try:
        yield
    finally:
        await db.close()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(vistas_router)
