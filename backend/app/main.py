from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core import models  # noqa: F401  (register tables before create_all)
from app.core.db import Base, engine
from app.core.errors import install_error_handlers
from app.features.events.router import router as events_router
from app.features.guests.router import router as guests_router
from app.features.hosts.router import router as hosts_router
from app.features.imports.router import router as imports_router
from app.features.people.router import router as people_router
from app.features.stats.router import router as stats_router
from app.seed import seed

ROUTERS = (
    guests_router,
    people_router,
    hosts_router,
    events_router,
    stats_router,
    imports_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # POC: no migrations — create tables on startup, then seed if empty.
    Base.metadata.create_all(bind=engine)
    seed()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AU POC CRM API",
        version="0.1.0",
        lifespan=lifespan,
        swagger_ui_parameters={"tryItOutEnabled": True},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    install_error_handlers(app)

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    for router in ROUTERS:
        app.include_router(router)

    return app


app = create_app()
