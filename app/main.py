from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routes import auth, products, orders, admin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando MasterChefEC...")
    await connect_db()
    logger.info("Conexión a MongoDB establecida")
    yield
    logger.info("Cerrando conexión a MongoDB...")
    await close_db()


app = FastAPI(
    title="MasterChefEC",
    description="Ecommerce de cosméticos para mujeres",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error global: {str(exc)}")
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse(
        "error.html", {"request": request, "error": str(exc)}, status_code=500
    )


@app.get("/", tags=["root"])
async def root():
    return {"message": "MasterChefEC API", "version": "1.0.0"}
