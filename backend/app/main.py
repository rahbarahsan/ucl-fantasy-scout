"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.routes import analysis, health, research
from app.utils.logger import setup_logging

setup_logging()

app = FastAPI(
    title="UCL Fantasy Scout",
    description="AI-powered squad analysis for UCL Fantasy Football managers.",
    version="1.0.0",
)

# --- CORS ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiting -------------------------------------------------------
app.add_middleware(RateLimitMiddleware)

# --- Routes --------------------------------------------------------------
app.include_router(health.router)
app.include_router(analysis.router, prefix="/api")
app.include_router(research.router, prefix="/api")
