from fastapi import FastAPI

from app.api import health
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health.router)
