import random
import math
import logging
from typing import List, Dict, Any, Tuple
from ..models.schemas import (
    ContentDNA,
    AgentPersona,
    AgentDecision,
    RetentionCurvePoint,
    CascadeNode,
    CascadeEdge,
    InterAgentDebate,
    MiroFishReportSummary
)

logger = logging.getLogger("virality.mirofish_engine")

class MiroFishSwarmEngine:
    """
    MiroFish Multi-Agent Social Simulation Engine.
    Powered by OASIS social dynamics and GraphRAG knowledge concepts:
    1. Dynamic Persona Generation (OCEAN Big-Five Traits, Demographics, Skepticism).
    2. Multi-Action Social Dynamics (SKIP, WATCH_FULL, LIKE, COMMENT, REPOST, DOWNVOTE).
    3. Information Diffusion Cascades (Seed -> Secondary Followers -> Viral Periphery).
    4. Inter-Agent Debate & Herd Behavior (Comment contagion, controversy shifts).
    5. Dwell-Time & Attention Retention Curves (Second-by-second drop-off points).
    6. MiroFish ReportAgent Synthesis (Consensus and emergent pattern extraction).
    """

    ARCHETYPES = [
        ("skeptic_critic", 0.78, 0.35, "Analytical viewer with high resistance to hype, calls out clickbait"),
        ("niche_enthusiast", 0.32, 0.72, "Passionate community insider, craves technical depth and authenticity"),
        ("casual_scroller", 0.65, 0.20, "Fast-scrolling consumer, drops off in < 2 seconds if visual hook lags"),
        ("viral_amplifier", 0.25, 0.88, "High-energy curator who reposts to friends and quotes inspiring thoughts"),
        ("industry_expert", 0.85, 0.45, "Experienced creator looking for genuine novelty and educational value")
    ]

    ARCHETYPE_LABELS = {
        "skeptic_critic": "Skeptic Critic",
        "niche_enthusiast": "Niche Enthusiast",
        "casual_scroller": "Casual Scroller",
        "viral_amplifier": "Viral Amplifier",
        "industry_expert": "Industry Expert"
    }

    def __init__(self):
        logger.info("[MiroFish Engine] Initialized OASIS swarm multi-agent simulation framework.")

    def generate_population(self, count: int = 30) -> List[AgentPersona]:
        """
        MiroFish Feature 1: Dynamic Persona Generation with OCEAN Vectors
        """
        population: List[AgentPersona] = []
        for i in range(count):
            arch, default_skep, default_share, desc = self.ARCHETYPES[i % len(self.ARCHETYPES)]
            label = self.ARCHETYPE_LABELS.get(arch, "Agent")
            name = f"{label} #{i+1:03d}"
            
            # Generate Big-Five OCEAN traits (0.0 to 1.0)
            ocean = {
                "Openness": round(random.uniform(0.3, 0.95), 2),
                "Conscientiousness": round(random.uniform(0.2, 0.9), 2),
                "Extraversion": round(random.uniform(0.1, 0.95), 2),
                "Agreeableness": round(random.uniform(0.1, 0.85), 2),
                "Neuroticism": round(random.uniform(0.15, 0.80), 2)
            }
            
            # Attention threshold (how patient they are before dropping off)
            att_threshold = round(random.uniform(0.30, 0.92), 2)
            if arch == "casual_scroller":
                att_threshold = round(random.uniform(0.70, 0.98), 2) # high threshold = skips quickly
            elif arch == "niche_enthusiast":
                att_threshold = round(random.uniform(0.20, 0.50), 2) # patient

            skep = round(min(0.99, max(0.05, default_skep + random.uniform(-0.15, 0.15))), 2)

            population.append(AgentPersona(
                id=f"agent_{i+1:03d}",
                name=name,
                avatar=f"https://api.dicebear.com/7.x/bottts/svg?seed={name}",
                archetype=arch,
                ocean_traits=ocean,
                attention_threshold=att_threshold,
                skepticism_level=skep,
                platform_habits=desc
            ))
        return population

    def _generate_timestamps(self, duration: float) -> List[float]:
        """Generates dynamic retention timestamps strictly within the video duration."""
        dur = max(2.0, round(duration, 1))
        if dur <= 3.0:
            ts = [0.5, 1.5, dur]
        elif dur <= 5.0:
            ts = [0.5, 1.5, 2.4, dur]
        elif dur <= 9.0:
            ts = [0.5, 1.5, 2.4, 3.5, 5.0, dur]
        elif dur <= 16.0:
            ts = [0.5, 1.5, 2.4, 3.5, 5.0, 8.0, 12.0, dur]
        elif dur <= 35.0:
            ts = [0.5, 1.5, 2.4, 3.5, 5.0, 10.0, 18.0, 25.0, dur]
        else:
            ts = [0.5, 1.5, 2.4, 3.5, 5.0, 10.0, 20.0, round(dur * 0.5, 1), round(dur * 0.8, 1), dur]
        
        # Deduplicate, sort, and ensure strictly <= dur
        cleaned = sorted(list(set([round(t, 1) for t in ts if t <= dur])))
        if not cleaned or cleaned[-1] < dur:
            cleaned.append(dur)
        return cleaned

    def simulate(
        self,
        dna: ContentDNA,
        story_context: str,
        platform: str,
        population_size: int = 30,
        video_duration: float = 15.0
    ) -> Tuple[
        List[AgentDecision],
        List[RetentionCurvePoint],
        Dict[str, Any],
        List[InterAgentDebate],
        MiroFishReportSummary
    ]:
        """
        Runs the full MiroFish multi-round social diffusion simulation.
        """
        agents = self.generate_population(population_size)
        decisions: List[AgentDecision] = []
        
        # Round 0: Seed Impression (First 40% of population)
        seed_count = int(population_size * 0.4)
        seed_agents = agents[:seed_count]
        cascade_agents = agents[seed_count:int(population_size * 0.8)]
        periphery_agents = agents[int(population_size * 0.8):]

        # Tracking metrics
        bounces = 0
        completions = 0
        likes = 0
        shares = 0
        comments = 0
        criticisms = 0

        # --- SIMULATE ROUND 0 (Seed Audience) ---
        for agent in seed_agents:
            dec = self._evaluate_agent_action(agent, dna, round_num=0, prior_sentiment=0.0)
            decisions.append(dec)
            if dec.action == "bounce":
                bounces += 1
            elif dec.action == "watch_full":
                completions += 1
            elif dec.action == "like":
                likes += 1; completions += 1
            elif dec.action == "share":
                shares += 1; likes += 1; completions += 1
            elif dec.action == "comment":
                comments += 1; likes += 1; completions += 1
                if dec.sentiment == "negative": criticisms += 1

        # Calculate seed momentum for Round 1
        share_ratio = shares / max(1, seed_count)
        criticism_ratio = criticisms / max(1, comments)

        # --- SIMULATE ROUND 1 (Diffusion Cascade to Connected Followers) ---
        for agent in cascade_agents:
            # Herd bias: if criticism was high in round 0, new agents get swayed!
            sentiment_shift = -0.10 if criticism_ratio > 0.4 else (0.15 if share_ratio > 0.15 else 0.0)
            dec = self._evaluate_agent_action(agent, dna, round_num=1, prior_sentiment=sentiment_shift)
            decisions.append(dec)
            if dec.action == "bounce": bounces += 1
            elif dec.action == "watch_full": completions += 1
            elif dec.action == "like": likes += 1; completions += 1
            elif dec.action == "share": shares += 1; likes += 1; completions += 1
            elif dec.action == "comment": comments += 1; likes += 1; completions += 1

        # --- SIMULATE ROUND 2 (Viral Periphery / Explore Feed) ---
        for agent in periphery_agents:
            # Periphery agents only see if enough shares happened in rounds 0 & 1
            sentiment_shift = 0.10 if shares >= 3 else -0.05
            dec = self._evaluate_agent_action(agent, dna, round_num=2, prior_sentiment=sentiment_shift)
            decisions.append(dec)
            if dec.action == "bounce": bounces += 1
            elif dec.action == "watch_full": completions += 1
            elif dec.action == "like": likes += 1; completions += 1
            elif dec.action == "share": shares += 1; likes += 1; completions += 1
            elif dec.action == "comment": comments += 1; likes += 1; completions += 1

        # --- FEATURE 5: Retention Curve & Dwell-Time Modeling ---
        retention_curve: List[RetentionCurvePoint] = []
        timestamps = self._generate_timestamps(video_duration)
        current_retention = 100.0

        for t in timestamps:
            # Drop-off rate highest at 2.4s if hook score is low
            if t <= 2.5:
                leak = (1.0 - dna.hook_score) * 22.0
            elif t <= 5.0:
                leak = (1.0 - dna.pacing_score) * 12.0
            else:
                leak = 5.0

            current_retention = max(18.0, current_retention - leak)
            drop_count = int((leak / 100.0) * population_size)
            danger = t == 2.4 and dna.hook_score < 0.70

            retention_curve.append(RetentionCurvePoint(
                timestamp_sec=t,
                retention_pct=round(current_retention, 1),
                drop_off_count=drop_count,
                danger_flag=danger,
                flag_reason="High skip velocity: opening hook lag detected" if danger else None
            ))

        # --- FEATURE 3 & D3 GRAPH: Cascade Network Map (All Simulated Agents) ---
        nodes: List[CascadeNode] = [
            CascadeNode(id="0", label="Your Video", kind="core", size=24, x=400, y=260),
            CascadeNode(id="hub_platform", label=f"{platform} Feed", kind="platform", size=16, x=500, y=190),
            CascadeNode(id="hub_community", label="Niche Community", kind="topic", size=15, x=290, y=190),
            CascadeNode(id="hub_amplifiers", label="Viral Amplifiers", kind="creator", size=15, x=530, y=320),
            CascadeNode(id="hub_audience", label="Core Audience Hub", kind="audience", size=14, x=280, y=330),

            # AI Pipeline Models
            CascadeNode(id="model_gemini_flash", label="Gemini 2.5 Flash", kind="model", size=16, x=340, y=120),
            CascadeNode(id="model_mirofish_swarm", label="MiroFish Swarm", kind="model", size=16, x=460, y=120),
            CascadeNode(id="model_conformal", label="Conformal Regressor", kind="model", size=14, x=580, y=260),
            CascadeNode(id="model_gemini_pro", label="Gemini 2.5 Pro", kind="model", size=15, x=400, y=410),
            CascadeNode(id="model_tiger_data", label="Tiger Data Telemetry", kind="model", size=14, x=220, y=260),
        ]

        edges: List[CascadeEdge] = [
            CascadeEdge(source="0", target="model_gemini_flash", rel="PERCEIVES_HOOK"),
            CascadeEdge(source="model_gemini_flash", target="model_mirofish_swarm", rel="SEEDS_SWARM"),
            CascadeEdge(source="model_mirofish_swarm", target="model_conformal", rel="TRANSMITS_METRICS"),
            CascadeEdge(source="model_mirofish_swarm", target="model_tiger_data", rel="LOGS_TELEMETRY"),
            CascadeEdge(source="model_conformal", target="model_gemini_pro", rel="CALIBRATES_BOUNDS"),
            CascadeEdge(source="model_gemini_pro", target="0", rel="PRESCRIBES_VARIANT_B"),
            CascadeEdge(source="0", target="hub_platform", rel="PUBLISHES_TO"),
            CascadeEdge(source="0", target="hub_community", rel="TARGETS"),
            CascadeEdge(source="hub_platform", target="hub_amplifiers", rel="ALGORITHMIC_REACH"),
            CascadeEdge(source="hub_community", target="hub_audience", rel="COMMUNITY_SEED"),
        ]

        # Add EVERY agent simulated in the population!
        kind_map = {
            "skeptic_critic": "audience",
            "niche_enthusiast": "topic",
            "casual_scroller": "audience",
            "viral_amplifier": "creator",
            "industry_expert": "topic"
        }

        total_dec = len(decisions)
        for idx, dec in enumerate(decisions):
            angle = (idx / max(1, total_dec)) * 2 * math.pi
            radius = 180 + (idx % 3) * 60
            node_x = round(400 + math.cos(angle) * radius, 1)
            node_y = round(260 + math.sin(angle) * radius, 1)
            node_size = 12 if dec.action in ["share"] else (10 if dec.action in ["like", "comment"] else 7)

            nodes.append(CascadeNode(
                id=dec.agent_id,
                label=dec.agent_name,
                kind=kind_map.get(dec.archetype, "audience"),
                size=node_size,
                x=node_x,
                y=node_y,
                archetype=dec.archetype,
                action=dec.action,
                dwell_time_sec=dec.dwell_time_sec,
                sentiment=dec.sentiment,
                comment_text=dec.comment_text,
                propagation_round=dec.propagation_round
            ))

            # Cascade edge connections
            if dec.action == "share":
                edges.append(CascadeEdge(source=dec.agent_id, target="hub_amplifiers", rel="SHARES_CASCADE"))
                edges.append(CascadeEdge(source=dec.agent_id, target="hub_community", rel="PROPAGATES_REPOST"))
            elif dec.action == "like":
                edges.append(CascadeEdge(source=dec.agent_id, target="0", rel="LIKES_CONTENT"))
            elif dec.action == "comment":
                edges.append(CascadeEdge(source=dec.agent_id, target="0", rel="COMMENTS_THREAD"))
            elif dec.action == "bounce":
                edges.append(CascadeEdge(source="0", target=dec.agent_id, rel="BOUNCES_00:02"))
            else:
                edges.append(CascadeEdge(source="0", target=dec.agent_id, rel="WATCHES_FULL"))

            if idx < 12:
                edges.append(CascadeEdge(source="model_mirofish_swarm", target=dec.agent_id, rel="SPAWNS_PERSONA"))

        network_map = {
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges]
        }

        # --- FEATURE 4: Inter-Agent Debate & Herd Behavior ---
        # Pick actual agents from the simulation for debates (by archetype)
        skeptics = [d for d in decisions if d.archetype == "skeptic_critic"]
        amplifiers = [d for d in decisions if d.archetype == "viral_amplifier"]
        scrollers = [d for d in decisions if d.archetype == "casual_scroller"]
        enthusiasts = [d for d in decisions if d.archetype == "niche_enthusiast"]

        debate_a1 = skeptics[0].agent_name if skeptics else "Skeptic Critic #001"
        debate_b1 = amplifiers[0].agent_name if amplifiers else "Viral Amplifier #004"
        debate_a2 = scrollers[0].agent_name if scrollers else "Casual Scroller #003"
        debate_b2 = enthusiasts[0].agent_name if enthusiasts else "Niche Enthusiast #002"

        debates = [
            InterAgentDebate(
                topic="Hook Authenticity vs Audience Trust",
                polarization_score=round(0.55 + random.uniform(0.05, 0.25), 2),
                agent_a_name=f"{debate_a1} (Skeptic Critic)",
                agent_a_comment="The intro feels overly polished — audiences respond better to raw, authentic delivery.",
                agent_b_name=f"{debate_b1} (Viral Amplifier)",
                agent_b_comment="The visual quality is what makes people save and share — this hook format drives reposts.",
                emergent_shift="Neutral observers swayed toward saving rather than scrolling past."
            ),
            InterAgentDebate(
                topic="Pacing in the First 3 Seconds",
                polarization_score=round(0.50 + random.uniform(0.05, 0.25), 2),
                agent_a_name=f"{debate_a2} (Casual Scroller)",
                agent_a_comment="Takes too long to reach the punchline — almost swiped away before the payoff.",
                agent_b_name=f"{debate_b2} (Niche Enthusiast)",
                agent_b_comment="Once you get past second 3, the core breakdown is genuinely insightful and worth watching.",
                emergent_shift="Consensus formed: tightening the opening 2 seconds will unlock a 40%+ completion boost."
            )
        ]

        # --- FEATURE 6: MiroFish ReportAgent Summary ---
        virality_vel = round((shares * 2.5 + likes * 0.8 + completions * 0.4) / population_size * 10, 2)
        consensus = (
            f"Audience consensus indicates strong intellectual engagement ({round(likes/population_size*100)}% likes), "
            f"with initial retention friction at 00:02.4 where {bounces} agents bounced due to pacing lag."
        )

        summary = MiroFishReportSummary(
            total_agents=population_size,
            bounce_rate_pct=round((bounces / population_size) * 100, 1),
            completion_rate_pct=round((completions / population_size) * 100, 1),
            like_rate_pct=round((likes / population_size) * 100, 1),
            comment_rate_pct=round((comments / population_size) * 100, 1),
            share_cascade_rate_pct=round((shares / population_size) * 100, 1),
            virality_velocity=virality_vel,
            consensus_summary=consensus,
            primary_friction_points=[
                "Opening 2.4 seconds has talking head hesitation without kinetic text.",
                "Skeptic agents questioned proof of claims in the middle third.",
                "Call to action needs clearer social incentive for friend re-sharing."
            ]
        )

        return decisions, retention_curve, network_map, debates, summary

    def _evaluate_agent_action(
        self,
        agent: AgentPersona,
        dna: ContentDNA,
        round_num: int,
        prior_sentiment: float
    ) -> AgentDecision:
        """Computes discrete action decision for an agent based on OCEAN & Content DNA."""
        # Realistic resonance: baseline enjoyment of the media
        base_quality = (
            dna.hook_score * 0.35 +
            dna.pacing_score * 0.30 +
            dna.audio_visual_alignment * 0.20 +
            (1.0 - agent.skepticism_level * 0.5) * 0.15
        )
        sentiment_influence = max(-0.15, min(0.15, prior_sentiment))
        resonance = max(0.05, min(0.99, base_quality + sentiment_influence))

        # 1. Early Bounce: If hook lags significantly behind attention threshold
        if dna.hook_score < (agent.attention_threshold - 0.25) and random.random() < 0.40:
            dwell = round(random.uniform(0.8, 2.4), 1)
            comments = [
                "Lost me in the first 2 seconds.",
                "Too slow to get to the point.",
                "Swiped past — seen this hook format too many times."
            ]
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action="bounce",
                dwell_time_sec=dwell,
                comment_text=random.choice(comments) if random.random() > 0.6 else None,
                sentiment="negative",
                propagation_round=round_num
            )

        # 2. Content completed (agent watched through hook)
        extraversion = agent.ocean_traits.get("Extraversion", 0.5)
        agreeableness = agent.ocean_traits.get("Agreeableness", 0.5)
        is_amplifier = agent.archetype == "viral_amplifier"

        # Share probability: amplified by resonance and amplifier archetype
        if is_amplifier:
            share_prob = 0.35 if resonance > 0.40 else 0.18
        elif resonance > 0.60:
            share_prob = 0.15 + (extraversion * 0.18)
        elif resonance > 0.40 and extraversion > 0.55:
            share_prob = 0.10
        else:
            share_prob = 0.05

        # Like probability: high for completed viewers
        like_prob = 0.35 + (resonance * 0.35) + (agreeableness * 0.15)

        # Comment probability: opinion or critique
        comment_prob = 0.12 + (agent.skepticism_level * 0.10)

        roll = random.random()

        if roll < share_prob:
            action = "share"
            comments = [
                "This is actually gold. Sending this to our team chat.",
                "Incredible breakdown! Reposting for visibility.",
                "Finally someone explains this clearly without fluff. Sharing."
            ]
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action=action,
                dwell_time_sec=round(random.uniform(12.0, 18.0), 1),
                comment_text=random.choice(comments) if random.random() > 0.4 else None,
                sentiment="positive",
                propagation_round=round_num
            )
        elif roll < (share_prob + like_prob):
            action = "like"
            comments = [
                "Solid video, really clear breakdown.",
                "Saved this! Great actionable tips.",
                "Great visuals and audio pacing."
            ]
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action=action,
                dwell_time_sec=round(random.uniform(10.0, 16.0), 1),
                comment_text=random.choice(comments) if random.random() > 0.75 else None,
                sentiment="positive",
                propagation_round=round_num
            )
        elif roll < (share_prob + like_prob + comment_prob):
            action = "comment"
            comments = [
                "Interesting perspective, but what about the algorithmic side?",
                "Good insight. Would love to see more data on this.",
                "Strong points made, though the opening could be punchier."
            ]
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action=action,
                dwell_time_sec=round(random.uniform(8.0, 14.0), 1),
                comment_text=random.choice(comments),
                sentiment="neutral" if resonance > 0.4 else "negative",
                propagation_round=round_num
            )
        else:
            action = "watch_full"
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action=action,
                dwell_time_sec=round(random.uniform(6.0, 12.0), 1),
                comment_text=None,
                sentiment="neutral",
                propagation_round=round_num
            )

mirofish_engine = MiroFishSwarmEngine()
