# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import configure_middleware
from app.db.mongo import connect_to_mongo, close_mongo
from app.api import auth, products, events, recs, metrics
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.ml.trainer import schedule_training_job, run_training

setup_logging()

app = FastAPI(title="BuyBixx Backend (MVP)")

# include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(recs.router, prefix="/recommend", tags=["recommend"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

configure_middleware(app)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup():
    # Connect to MongoDB
    await connect_to_mongo()

    # Run training once on startup to generate popularity.json & similarity.json
    await run_training()

    # Add scheduled training job
    schedule_training_job(scheduler)

    # Start scheduler only if not already running
    if not scheduler.running:
        scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    # Stop scheduler and close DB
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await close_mongo()

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "env": settings.ENV})

@app.get("/")
async def root():
    return {"message": "Welcome to BuyBixx Backend API"}
