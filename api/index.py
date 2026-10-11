"""
Vercel Serverless Function entry point for the Virality FastAPI backend.
Vercel routes all /api/* requests to this file.
"""
import sys
import os

# Make backend package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.main import app  # noqa: F401 — Vercel picks up `app` as the ASGI handler
