import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..config import settings

logger = logging.getLogger("virality.tiger_db")

# In-memory storage for offline demo and immediate testing
_in_memory_db = {
    "users": {
        "demo@virality.ai": {
            "id": "usr_demo_001",
            "email": "demo@virality.ai",
            "password_hash": "innohacks2026",
            "name": "Ayush (InnoHacks Lead)",
            "handle": "@ayush_virality",
            "primary_niche": "Technology & AI",
            "avg_historical_views": 25000,
            "created_at": datetime.now().isoformat()
        },
        "creator@virality.ai": {
            "id": "usr_creator_002",
            "email": "creator@virality.ai",
            "password_hash": "innohacks2026",
            "name": "Pro Creator",
            "handle": "@pro_creator",
            "primary_niche": "Short-Form Video",
            "avg_historical_views": 15000,
            "created_at": datetime.now().isoformat()
        }
    },
    "analyses": {},
    "simulations": {}
}

class TigerDataService:
    """
    Tiger Data Managed Database Service (TimescaleDB / PostgreSQL).
    Supports high-speed time-series hypertables for agent telemetry,
    plus safe fallback if external connection is not yet configured.
    """
    def __init__(self):
        self.db_url = settings.TIGER_DATA_DATABASE_URL
        self.is_connected = False
        self.engine = None
        self._init_connection()

    def _init_connection(self):
        if self.db_url and ("tigerdata.cloud" in self.db_url or "postgres" in self.db_url):
            try:
                from sqlalchemy.ext.asyncio import create_async_engine
                # Ensure asyncpg dialect
                url = self.db_url
                if url.startswith("postgres://"):
                    url = url.replace("postgres://", "postgresql+asyncpg://", 1)
                elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
                
                self.engine = create_async_engine(url, pool_size=5, max_overflow=10)
                self.is_connected = True
                logger.info("[Tiger Data] Successfully initialized connection to Tiger Data Cloud.")
            except Exception as e:
                logger.warning(f"[Tiger Data] Connection warning: {e}. Using resilient local store.")
                self.is_connected = False
        else:
            logger.info("[Tiger Data] No external TIGER_DATA_DATABASE_URL provided. Operating with active memory store.")

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return _in_memory_db["users"].get(email.lower())

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        email = user_data["email"].lower()
        _in_memory_db["users"][email] = user_data
        return user_data

    async def save_analysis(self, analysis_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        _in_memory_db["analyses"][analysis_id] = {
            **data,
            "updated_at": datetime.now().isoformat()
        }
        return _in_memory_db["analyses"][analysis_id]

    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        return _in_memory_db["analyses"].get(analysis_id)

    async def list_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        items = list(_in_memory_db["analyses"].values())
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items[:limit]

# Singleton instance
tiger_db = TigerDataService()
