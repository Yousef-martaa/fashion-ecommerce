from fastapi import FastAPI

from app.api import auth, health
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health.router)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
