import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ...infra.Container import Container
from ...infra.config.Settings import settings
from .routers import CatalogoRouter, WebhookRouter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bot")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_directories()
    app.state.container = Container(settings)
    logger.info("Container iniciado, MongoDB conectado.")
    yield


app = FastAPI(title="WhatsApp Bot - Loja de Suplementos", lifespan=lifespan)
app.include_router(WebhookRouter.router)
app.include_router(CatalogoRouter.router)
