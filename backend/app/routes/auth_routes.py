from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from ..models.schemas import UserLogin, UserRegister, TokenResponse, UserProfile
from ..services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await auth_service.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Use demo@virality.ai / innohacks2026 for instant access."
        )
    
    token = auth_service.create_access_token({"sub": user["email"], "id": user["id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "handle": user["handle"],
            "primary_niche": user.get("primary_niche", "Creator"),
            "avg_historical_views": user.get("avg_historical_views", 15000)
        }
    }

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    user = await auth_service.register_user(
        email=payload.email,
        password=payload.password,
        name=payload.name or payload.email.split("@")[0].capitalize(),
        handle=payload.handle or f"@{payload.email.split('@')[0]}"
    )
    token = auth_service.create_access_token({"sub": user["email"], "id": user["id"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "handle": user["handle"],
            "primary_niche": user.get("primary_niche", "Creator"),
            "avg_historical_views": user.get("avg_historical_views", 15000)
        }
    }

@router.get("/demo-credentials")
async def get_demo_credentials():
    """Returns pre-configured demo credentials for judges and quick testing."""
    return {
        "demo_accounts": [
            {
                "email": "demo@virality.ai",
                "password": "innohacks2026",
                "role": "Lead Creator & AI Strategist",
                "name": "Ayush (InnoHacks)"
            },
            {
                "email": "creator@virality.ai",
                "password": "innohacks2026",
                "role": "Social Media Growth Hacker",
                "name": "Virality Pro"
            }
        ],
        "instructions": "Enter either demo account or click 'Fill Demo Credentials' in the workspace."
    }
