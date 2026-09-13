import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import health, alerts, incidents, dashboard

app = FastAPI(title="THREATMESH API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(health.router, prefix="/api")
app.include_router(alerts.router, prefix="/api/alerts")
app.include_router(incidents.router, prefix="/api/incidents")
app.include_router(dashboard.router, prefix="/api/dashboard")
app.include_router(incidents.bob_router, prefix="/api/bob")

@app.on_event("startup")
async def startup_event():
    import logging
    logging.info(f"App starting... Database URL configured: {bool(settings.DATABASE_URL)}")
    logging.info(f"Bob API configured: {bool(settings.BOB_API_URL)}")
