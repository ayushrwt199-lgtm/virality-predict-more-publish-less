from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal

# --- Auth Schemas ---
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = "Creator"
    handle: Optional[str] = "@creator"

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    handle: str
    primary_niche: str = "general"
    avg_historical_views: int = 15000

# --- Analysis Request Options ---
class AnalysisRequestOptions(BaseModel):
    description: str = Field(..., description="The story/context behind the video")
    target_platform: Literal["Instagram", "YouTube", "TikTok"] = "Instagram"
    current_audience: Optional[str] = "Followers, tech enthusiasts, peers"
    target_audience: Optional[str] = "Wider niche community, viral explore feed"
    reach_goal: Optional[str] = "50000"
    historical_baseline_views: Optional[int] = 12000
    niche_category: Optional[str] = "tech_creator"
    simulation_intensity: Optional[Literal["fast", "balanced", "deep"]] = "balanced"
    audience_agent_count: Optional[int] = 30

# --- Step 1: Gemini Multimodal Content DNA ---
class SentimentArcPoint(BaseModel):
    timestamp: str # "00:02"
    valence: float # -1.0 to 1.0
    label: str # "Tension", "Resolution", "Curiosity"

class ContentDNA(BaseModel):
    hook_score: float = Field(..., ge=0.0, le=1.0, description="0-3s hook punchiness")
    hook_diagnosis: str = Field(..., description="Explanation of hook strength/weakness")
    pacing_score: float = Field(..., ge=0.0, le=1.0, description="Cuts and visual tempo")
    audio_clarity: float = Field(..., ge=0.0, le=1.0, description="Voice vs background sound")
    audio_visual_alignment: float = Field(..., ge=0.0, le=1.0)
    sentiment_arc: List[SentimentArcPoint] = Field(default_factory=list)
    ocr_extracted_text: List[str] = Field(default_factory=list)
    detected_topics: List[str] = Field(default_factory=list)
    controversy_polarization_risk: Literal["LOW", "MODERATE", "HIGH"] = "MODERATE"
    raw_gemini_observations: str = ""

# --- Step 2: MiroFish Multi-Agent Swarm Simulation ---
class AgentPersona(BaseModel):
    id: str
    name: str
    avatar: str
    archetype: Literal["skeptic_critic", "niche_enthusiast", "casual_scroller", "viral_amplifier", "industry_expert"]
    ocean_traits: Dict[str, float] # Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
    attention_threshold: float # 0.0 - 1.0
    skepticism_level: float # 0.0 - 1.0
    platform_habits: str

class AgentDecision(BaseModel):
    agent_id: str
    agent_name: str
    archetype: str
    action: Literal["bounce", "watch_full", "like", "comment", "share", "downvote"]
    dwell_time_sec: float
    comment_text: Optional[str] = None
    sentiment: Literal["positive", "neutral", "negative"]
    propagation_round: int # 0 (seed), 1 (cascade), 2 (viral periphery)

class RetentionCurvePoint(BaseModel):
    timestamp_sec: float
    retention_pct: float
    drop_off_count: int
    danger_flag: bool = False
    flag_reason: Optional[str] = None

class CascadeNode(BaseModel):
    id: str
    label: str
    kind: str # 'core', 'creator', 'audience', 'topic', 'platform'
    size: int
    x: Optional[float] = 0
    y: Optional[float] = 0

class CascadeEdge(BaseModel):
    source: str
    target: str

class InterAgentDebate(BaseModel):
    topic: str
    polarization_score: float # 0.0 to 1.0
    agent_a_name: str
    agent_a_comment: str
    agent_b_name: str
    agent_b_comment: str
    emergent_shift: str

class MiroFishReportSummary(BaseModel):
    total_agents: int
    bounce_rate_pct: float
    completion_rate_pct: float
    like_rate_pct: float
    comment_rate_pct: float
    share_cascade_rate_pct: float
    virality_velocity: float
    consensus_summary: str
    primary_friction_points: List[str]

# --- Step 3: Calibrated Conformal Prediction ---
class ReachPredictionInterval(BaseModel):
    min_impressions: int
    median_impressions: int
    peak_impressions: int
    confidence_level_pct: int = 90
    calibration_method: str = "Conformal Quantile Regression"

class CalibratedPrediction(BaseModel):
    reach: ReachPredictionInterval
    predicted_engagement_rate: float # e.g. 7.4%
    virality_potential_index: int # 0 to 100
    share_propensity: Literal["Low", "Moderate", "High", "Viral Explosive"]
    comment_propensity: Literal["Low", "Moderate", "Elevated", "Intense Debate"]
    category_benchmark_percentile: int # e.g. 78th percentile in Niche

# --- Step 4: Gemini Strategic Prescription & Variant B ---
class ActionableFix(BaseModel):
    timestamp: str
    issue: str
    recommended_change: str
    expected_impact: str

class VariantBComparison(BaseModel):
    original_hook: str
    recommended_optimized_hook: str
    original_caption: str
    recommended_caption_hashtags: str
    predicted_lift_pct: str # e.g. "+85% Reach Lift"
    why_it_works: str

class StrategicPrescription(BaseModel):
    executive_verdict: str
    strengths: List[str]
    retention_leaks: List[str]
    actionable_remedies: List[ActionableFix]
    variant_b: VariantBComparison

# --- Full Unified Analysis Result ---
class FullAnalysisResponse(BaseModel):
    analysis_id: str
    status: str = "completed"
    created_at: str
    target_platform: str
    story_context: str
    content_dna: ContentDNA
    swarm_simulation: Dict[str, Any]
    retention_curve: List[RetentionCurvePoint]
    audience_network_map: Dict[str, Any]
    inter_agent_debates: List[InterAgentDebate]
    mirofish_summary: MiroFishReportSummary
    calibrated_prediction: CalibratedPrediction
    strategic_prescription: StrategicPrescription
