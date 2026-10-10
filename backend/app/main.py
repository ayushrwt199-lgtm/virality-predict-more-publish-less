from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .config import settings
from .routes.auth_routes import router as auth_router
from .routes.analysis_routes import router as analysis_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Virality: Pre-publication social media reach and engagement prediction engine using Google Gemini and MiroFish multi-agent simulation.",
    version="2.0.0"
)

# CORS configuration to allow local and Lovable/Vite frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(analysis_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {
        "project": "Virality 2.0 AI Pre-Flight Engine",
        "tagline": "Predict More. Publish Less.",
        "status": "online",
        "api_docs": "/docs",
        "pipeline": "Gemini 2.5 Flash -> MiroFish OASIS Swarm -> Conformal Predictor -> Gemini 2.5 Pro",
        "database": "Tiger Data (TimescaleDB / PostgreSQL)"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
