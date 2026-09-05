from fastapi import FastAPI

from app.routes import generate, health

app = FastAPI(
    title="LIVE AI",
    description="Microservice AI cho LIVE Viễn Chí Bảo",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(generate.router, prefix="/v1")
