import os
import shutil
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from ..config import settings
from ..models.schemas import FullAnalysisResponse
from ..services.gemini_service import gemini_service
from ..services.mirofish_engine import mirofish_engine
from ..services.predictor import reach_predictor
from ..services.gemini_remedy import gemini_remedy_service
from ..services.tiger_db import tiger_db

router = APIRouter(prefix="/analysis", tags=["Content Analysis"])

@router.post("/run", response_model=FullAnalysisResponse)
async def run_analysis(
    file: Optional[UploadFile] = File(None),
    description: str = Form(""),
    platform: str = Form("Instagram"),
    current_audience: str = Form("Tech enthusiasts and creators"),
    target_audience: str = Form("Wider explore feed and viral community"),
    reach_goal: str = Form("50000"),
    baseline_views: int = Form(15000),
    simulation_intensity: str = Form("balanced"),
    agent_count: int = Form(30)
):
    """
    Executes the Complete 4-Stage Virality Intelligence Pipeline:
    1. Gemini 2.5 Flash Multimodal Video & Content Perception
    2. MiroFish Multi-Agent Swarm Simulation (OASIS Cascades & Debates)
    3. Calibrated Conformal Quantile Reach Prediction
    4. Gemini 2.5 Pro Strategic Prescription & Variant B Lift Generator
    """
    analysis_id = f"an_{uuid.uuid4().hex[:10]}"
    saved_video_path = None

    # Handle video file save if provided
    if file:
        file_ext = os.path.splitext(file.filename)[1] or ".mp4"
        saved_video_path = os.path.join(settings.UPLOAD_DIR, f"{analysis_id}{file_ext}")
        with open(saved_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # 1. Gemini Multimodal Perception
    dna = await gemini_service.analyze_content(
        video_path=saved_video_path,
        description=description,
        platform=platform,
        current_audience=current_audience,
        target_audience=target_audience,
        reach_goal=reach_goal
    )

    # 2. MiroFish Swarm Simulation
    pop_count = 50 if simulation_intensity == "deep" else (20 if simulation_intensity == "fast" else agent_count)
    decisions, retention_curve, network_map, debates, summary = mirofish_engine.simulate(
        dna=dna,
        story_context=description,
        platform=platform,
        population_size=pop_count
    )

    # 3. Calibrated Reach Prediction
    prediction = reach_predictor.predict(
        dna=dna,
        summary=summary,
        baseline_views=baseline_views,
        reach_goal=reach_goal
    )

    # 4. Gemini Strategic Prescription & Variant B
    prescription = gemini_remedy_service.synthesize(
        dna=dna,
        summary=summary,
        prediction=prediction,
        story_context=description,
        platform=platform
    )

    response_data = FullAnalysisResponse(
        analysis_id=analysis_id,
        status="completed",
        created_at=datetime.now().isoformat(),
        target_platform=platform,
        story_context=description,
        content_dna=dna,
        swarm_simulation={
            "agent_decisions": [d.model_dump() for d in decisions],
            "total_agents": pop_count
        },
        retention_curve=retention_curve,
        audience_network_map=network_map,
        inter_agent_debates=debates,
        mirofish_summary=summary,
        calibrated_prediction=prediction,
        strategic_prescription=prescription
    )

    # Save to Tiger Data / DB
    await tiger_db.save_analysis(analysis_id, response_data.model_dump())

    return response_data

@router.get("/history", response_model=List[dict])
async def get_history(limit: int = 10):
    return await tiger_db.list_recent_analyses(limit=limit)

@router.get("/{analysis_id}", response_model=dict)
async def get_analysis_by_id(analysis_id: str):
    res = await tiger_db.get_analysis(analysis_id)
    if not res:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return res

@router.get("/system/status")
async def get_system_status():
    """System health check and connected AI components status."""
    return {
        "status": "operational",
        "gemini_model": settings.GEMINI_PERCEPTION_MODEL,
        "gemini_sdk_active": gemini_service.client is not None,
        "mirofish_engine": "OASIS Multi-Agent Swarm (Active)",
        "database_backend": "Tiger Data (Timescale/PostgreSQL Engine)",
        "database_connected": tiger_db.is_connected,
        "supported_platforms": ["Instagram Reels", "YouTube Shorts", "TikTok", "LinkedIn", "X/Twitter"]
    }
