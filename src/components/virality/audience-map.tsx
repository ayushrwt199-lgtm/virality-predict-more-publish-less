import React, { useEffect, useRef, useState } from 'react'
import * as d3 from 'd3'
import { Maximize2, Minus, Plus, RotateCcw, X, Sliders, Sparkles, Brain, Cpu, Database, Network } from 'lucide-react'
import { Button } from '@/components/ui/button'

// --- Supported Entity & Model Types with distinctive signature colors ---
export const NODE_TYPES: Record<string, { color: string; model: string; category: string }> = {
  "Gemini 2.5 Flash": { color: "#38bdf8", model: "Google Gemini 2.5 Flash", category: "Multimodal Perception AI" },
  "MiroFish Swarm": { color: "#a855f7", model: "MiroFish (OASIS Swarm Engine)", category: "Multi-Agent Simulation" },
  "Conformal Regressor": { color: "#10b981", model: "Conformal Quantile ML", category: "Statistical Calibration" },
  "Gemini 2.5 Pro": { color: "#ec4899", model: "Google Gemini 2.5 Pro", category: "Strategic Prescription AI" },
  "Tiger Data": { color: "#f59e0b", model: "Tiger Data (TimescaleDB / Postgres)", category: "Temporal Telemetry DB" },
  "Your Video": { color: "#e11d63", model: "Seed Input Post", category: "Content Under Analysis" },
  "Skeptic Critic": { color: "#ef4444", model: "MiroFish OASIS Agent", category: "Synthetic Audience Persona" },
  "Viral Amplifier": { color: "#8b5cf6", model: "MiroFish OASIS Agent", category: "Synthetic Audience Persona" },
  "Casual Scroller": { color: "#eab308", model: "MiroFish OASIS Agent", category: "Synthetic Audience Persona" },
  "Niche Enthusiast": { color: "#06b6d4", model: "MiroFish OASIS Agent", category: "Synthetic Audience Persona" },
  "Platform Feed": { color: "#f43f5e", model: "Recommendation Graph", category: "Distribution Channel" },
  "Community Hub": { color: "#14b8a6", model: "Secondary Follower Cluster", category: "Audience Network" },
  "Industry Expert": { color: "#3b82f6", model: "MiroFish OASIS Agent", category: "Synthetic Audience Persona" }
}

export interface GraphNode extends d3.SimulationNodeDatum {
  id: string
  name: string
  type: string
  model: string
  role: string
  uuid: string
  properties: Record<string, any>
  summary: string
  size?: number
}

export interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: string | GraphNode
  target: string | GraphNode
  rel: string
  curve?: number
  cx?: number
  cy?: number
}

interface AudienceMapProps {
  customNodes?: Array<any>
  customEdges?: Array<any>
}

export function AudienceMap({ customNodes, customEdges }: AudienceMapProps) {
  const svgRef = useRef<SVGSVGElement | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [showEdgeLabels, setShowEdgeLabels] = useState(true)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [isExpanded, setIsExpanded] = useState(false)
  const [revision, setRevision] = useState(0)

  // References to keep D3 selections and simulation
  const simRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null)
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null)
  const gRef = useRef<d3.Selection<SVGGElement, unknown, null, undefined> | null>(null)

  useEffect(() => {
    if (!svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove() // Clean up prior render

    const width = 860
    const height = 520

    // Setup main container group for zooming
    const g = svg.append("g")
    gRef.current = g

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.35, 3.5])
      .on("zoom", (e) => {
        g.attr("transform", e.transform)
        setZoomLevel(Math.round(e.transform.k * 100))
      })

    zoomBehaviorRef.current = zoom
    svg.call(zoom)

    // Build or Map Data
    const { nodes, links } = generateGraphData(customNodes, customEdges)

    // Adjacency map for highlight/dimming
    const neighbors = new Map<string, Set<string>>()
    nodes.forEach(n => neighbors.set(n.id, new Set()))
    links.forEach(l => {
      const sId = typeof l.source === 'object' ? l.source.id : l.source
      const tId = typeof l.target === 'object' ? l.target.id : l.target
      neighbors.get(sId)?.add(tId)
      neighbors.get(tId)?.add(sId)
    })

    // Assign dynamic curvature
    links.forEach((l, i) => {
      l.curve = ((i % 5) - 2) * 16 + (i % 2 ? 8 : -8)
    })

    // Draw Links
    const linkGroup = g.append("g").attr("class", "links-layer")
    const linkSel = linkGroup.selectAll("path")
      .data(links)
      .join("path")
      .attr("class", "graph-link")
      .attr("fill", "none")
      .attr("stroke", "#3b4252")
      .attr("stroke-width", 1.2)
      .attr("opacity", 0.65)

    // Draw Edge Labels
    const edgeLabelGroup = g.append("g").attr("class", "edge-labels-layer")
    const edgeLabelSel = edgeLabelGroup.selectAll("text")
      .data(links)
      .join("text")
      .attr("class", "graph-edge-label")
      .attr("font-size", "7.5px")
      .attr("fill", "#94a3b8")
      .attr("text-anchor", "middle")
      .attr("pointer-events", "none")
      .text(d => d.rel)
      .style("display", showEdgeLabels ? "block" : "none")

    // Draw Nodes
    const nodeGroup = g.append("g").attr("class", "nodes-layer")
    const nodeSel = nodeGroup.selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("class", "graph-node-circle")
      .attr("r", d => d.size || (d.id === "0" ? 14 : 7.5))
      .attr("fill", d => NODE_TYPES[d.type]?.color || "#38bdf8")
      .attr("stroke", "#0f172a")
      .attr("stroke-width", 1.8)
      .attr("cursor", "pointer")
      .on("click", (e, d) => {
        e.stopPropagation()
        selectNode(d)
      })
      .call(
        d3.drag<SVGCircleElement, GraphNode>()
          .on("start", (e, d) => {
            if (!e.active) sim.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on("drag", (e, d) => {
            d.fx = e.x
            d.fy = e.y
          })
          .on("end", (e, d) => {
            if (!e.active) sim.alphaTarget(0)
            d.fx = null
            d.fy = null
          })
      )

    // Draw Node Text Labels
    const nodeLabelGroup = g.append("g").attr("class", "node-labels-layer")
    const nodeLabelSel = nodeLabelGroup.selectAll("text")
      .data(nodes)
      .join("text")
      .attr("class", "graph-node-label")
      .attr("dx", 10)
      .attr("dy", 3.5)
      .attr("font-size", d => d.size && d.size > 11 ? "10px" : "8.5px")
      .attr("font-weight", d => d.size && d.size > 11 ? "600" : "500")
      .attr("fill", "#f8fafc")
      .attr("paint-order", "stroke")
      .attr("stroke", "#090d16")
      .attr("stroke-width", "2.5px")
      .attr("pointer-events", "none")
      .text(d => d.name)

    // Force Simulation Setup
    const sim = d3.forceSimulation<GraphNode>(nodes)
      .force("link", d3.forceLink<GraphNode, GraphLink>(links).id(d => d.id).distance(80).strength(0.65))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(d => (d.size || 8) + 16))
      .on("tick", () => {
        // Compute Quadratic Bézier curve
        linkSel.attr("d", (d: any) => {
          const mx = (d.source.x + d.target.x) / 2
          const my = (d.source.y + d.target.y) / 2
          const dx = d.target.x - d.source.x
          const dy = d.target.y - d.source.y
          const len = Math.hypot(dx, dy) || 1
          const curveVal = d.curve || 0
          d.cx = mx - (dy / len) * curveVal
          d.cy = my + (dx / len) * curveVal
          return `M${d.source.x},${d.source.y} Q${d.cx},${d.cy} ${d.target.x},${d.target.y}`
        })

        edgeLabelSel
          .attr("x", (d: any) => (d.source.x + 2 * d.cx + d.target.x) / 4)
          .attr("y", (d: any) => (d.source.y + 2 * d.cy + d.target.y) / 4)

        nodeSel.attr("cx", d => d.x!).attr("cy", d => d.y!)
        nodeLabelSel.attr("x", d => d.x!).attr("y", d => d.y!)
      })

    simRef.current = sim

    function selectNode(d: GraphNode) {
      setSelectedNode(d)
      linkSel
        .classed("hot-edge", (l: any) => l.source.id === d.id || l.target.id === d.id)
        .classed("dimmed", (l: any) => l.source.id !== d.id && l.target.id !== d.id)

      edgeLabelSel
        .classed("dimmed", (l: any) => l.source.id !== d.id && l.target.id !== d.id)

      nodeSel
        .classed("dimmed", n => n.id !== d.id && !neighbors.get(d.id)?.has(n.id))

      nodeLabelSel
        .classed("dimmed", n => n.id !== d.id && !neighbors.get(d.id)?.has(n.id))
    }

    svg.on("click", () => {
      setSelectedNode(null)
      linkSel.classed("hot-edge", false).classed("dimmed", false)
      edgeLabelSel.classed("dimmed", false)
      nodeSel.classed("dimmed", false)
      nodeLabelSel.classed("dimmed", false)
    })

    return () => {
      sim.stop()
    }
  }, [revision, customNodes, customEdges, showEdgeLabels])

  // Helper Controls
  const handleZoom = (factor: number) => {
    if (!svgRef.current || !zoomBehaviorRef.current) return
    const svg = d3.select(svgRef.current)
    svg.transition().duration(250).call(zoomBehaviorRef.current.scaleBy, factor)
  }

  const handleReset = () => {
    if (!svgRef.current || !zoomBehaviorRef.current) return
    const svg = d3.select(svgRef.current)
    svg.transition().duration(350).call(zoomBehaviorRef.current.transform, d3.zoomIdentity)
    setRevision(r => r + 1)
  }

  return (
    <div className={`audience-map-container relative w-full rounded-2xl overflow-hidden border border-border bg-[#0b0e17] ${isExpanded ? 'fixed inset-4 z-50 shadow-2xl' : 'min-h-[520px]'}`}>
      
      {/* Top Bar with Title, Model Badges & Controls */}
      <div className="absolute top-0 left-0 right-0 z-10 px-4 py-3 flex flex-wrap items-center justify-between gap-3 bg-gradient-to-b from-[#0b0e17]/90 via-[#0b0e17]/70 to-transparent backdrop-blur-sm border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-semibold text-xs tracking-wide text-foreground">
            AI AGENT & CASCADE RELATIONSHIP GRAPH
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20 font-medium">
            MiroFish Swarm + Gemini Multimodal
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs">
          {/* Edge Label Switch */}
          <label className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-card/70 border border-border/60 text-xs cursor-pointer select-none text-muted-foreground hover:text-foreground">
            <input
              type="checkbox"
              checked={showEdgeLabels}
              onChange={e => setShowEdgeLabels(e.target.checked)}
              className="accent-primary cursor-pointer w-3.5 h-3.5"
            />
            <span>Show Edge Labels</span>
          </label>

          {/* Refresh */}
          <Button
            size="sm"
            variant="outline"
            className="h-7 text-xs gap-1 border-border/60"
            onClick={handleReset}
          >
            <RotateCcw size={12} />
            <span>Refresh</span>
          </Button>

          {/* Expand Toggle */}
          <Button
            size="icon"
            variant="ghost"
            className="h-7 w-7 text-muted-foreground"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? "Collapse Map" : "Expand Map"}
          >
            {isExpanded ? <X size={14} /> : <Maximize2 size={14} />}
          </Button>
        </div>
      </div>

      {/* Interactive SVG Canvas */}
      <svg
        ref={svgRef}
        viewBox="0 0 860 520"
        className="w-full h-[520px] block cursor-grab active:cursor-grabbing bg-[#090d16]"
        style={{
          backgroundImage: "radial-gradient(#1e293b 1px, transparent 1px)",
          backgroundSize: "22px 22px"
        }}
      />

      {/* Side Inspector Panel (like panel in graph.html) */}
      {selectedNode && (
        <aside className="absolute right-4 top-14 bottom-14 w-80 max-w-[calc(100%-32px)] bg-card/95 backdrop-blur-md border border-border/80 rounded-xl p-4 shadow-2xl z-20 overflow-y-auto text-xs animate-in slide-in-from-right-4 duration-200">
          <div className="flex items-center justify-between mb-3 border-b border-border/50 pb-2">
            <div>
              <h4 className="font-semibold text-sm text-foreground">{selectedNode.name}</h4>
              <span className="text-[10px] text-muted-foreground">{NODE_TYPES[selectedNode.type]?.category}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className="text-[10px] px-2 py-0.5 rounded-full font-bold text-white shadow-sm"
                style={{ backgroundColor: NODE_TYPES[selectedNode.type]?.color || '#38bdf8' }}
              >
                {selectedNode.type}
              </span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-muted-foreground hover:text-foreground p-1 text-sm rounded"
              >
                ✕
              </button>
            </div>
          </div>

          <dl className="space-y-2 text-xs">
            {/* AI Model Attribution */}
            <div>
              <dt className="text-muted-foreground text-[10px] font-semibold uppercase tracking-wider flex items-center gap-1">
                <Brain size={12} className="text-primary"/> Underlying Model / Engine
              </dt>
              <dd className="font-medium text-foreground text-xs mt-0.5">
                {selectedNode.model}
              </dd>
            </div>

            <div>
              <dt className="text-muted-foreground text-[10px] font-semibold uppercase tracking-wider">Role in Pipeline</dt>
              <dd className="text-foreground mt-0.5">{selectedNode.role}</dd>
            </div>

            <div>
              <dt className="text-muted-foreground text-[10px] font-semibold uppercase tracking-wider">Node UUID</dt>
              <dd className="font-mono text-[10px] text-muted-foreground break-all">{selectedNode.uuid}</dd>
            </div>

            <div className="pt-2 border-t border-border/40">
              <dt className="text-muted-foreground text-[10px] font-semibold uppercase tracking-wider">Simulation Properties</dt>
              <dd className="mt-1 space-y-1">
                {Object.entries(selectedNode.properties || {}).map(([k, v]) => (
                  <div key={k} className="flex justify-between items-center text-[11px] p-1.5 rounded bg-background/50 border border-white/5">
                    <span className="text-muted-foreground">{k}:</span>
                    <span className="font-medium text-foreground">{String(v)}</span>
                  </div>
                ))}
              </dd>
            </div>

            <div className="pt-2 border-t border-border/40">
              <dt className="text-muted-foreground text-[10px] font-semibold uppercase tracking-wider">Summary & Behavioral Reasoning</dt>
              <dd className="text-foreground/90 leading-relaxed mt-1 text-[11px]">
                {selectedNode.summary}
              </dd>
            </div>
          </dl>
        </aside>
      )}

      {/* Bottom Bar: Entity Types & Model Legend */}
      <div className="absolute left-4 bottom-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 bg-card/85 backdrop-blur-md border border-border/60 rounded-xl px-4 py-2.5 text-xs">
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-bold text-[10px] tracking-wider uppercase text-primary flex items-center gap-1">
            <Cpu size={12}/> Models & Entity Types:
          </span>
          <div className="flex flex-wrap items-center gap-2.5">
            {Object.entries(NODE_TYPES).map(([typeKey, cfg]) => (
              <span key={typeKey} className="flex items-center gap-1.5 text-[10.5px] text-muted-foreground">
                <i className="inline-block w-2 h-2 rounded-full shadow-sm" style={{ backgroundColor: cfg.color }} />
                <span>{typeKey}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Zoom Tool Buttons */}
        <div className="flex items-center gap-1.5 border-l border-border/60 pl-3">
          <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => handleZoom(0.8)} title="Zoom Out">
            <Minus size={12} />
          </Button>
          <span className="text-[10px] font-mono w-9 text-center text-muted-foreground">{zoomLevel}%</span>
          <Button size="icon" variant="ghost" className="h-6 w-6" onClick={() => handleZoom(1.2)} title="Zoom In">
            <Plus size={12} />
          </Button>
        </div>
      </div>

      {/* Scoped CSS for Curved Bézier Highlights & Dims */}
      <style>{`
        .graph-link.hot-edge {
          stroke: #ec4899 !important;
          stroke-width: 2.2px !important;
          opacity: 1 !important;
          filter: drop-shadow(0 0 6px rgba(236, 72, 153, 0.6));
        }
        .dimmed {
          opacity: 0.12 !important;
          transition: opacity 0.25s ease;
        }
        .graph-node-circle {
          transition: transform 0.2s, stroke-width 0.2s, opacity 0.25s;
        }
        .graph-node-circle:hover {
          stroke: #ffffff;
          stroke-width: 2.5px;
          filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.7));
        }
      `}</style>
    </div>
  )
}

// --- Data Generator: Combines Pipeline Models + MiroFish Swarm Personas ---
function mapNodeType(node: any): string {
  if (node.id === "0" || node.kind === "core") return "Your Video"
  if (node.id === "model_gemini_flash" || node.label?.includes("Gemini 2.5 Flash")) return "Gemini 2.5 Flash"
  if (node.id === "model_mirofish_swarm" || node.label?.includes("MiroFish")) return "MiroFish Swarm"
  if (node.id === "model_conformal" || node.label?.includes("Conformal")) return "Conformal Regressor"
  if (node.id === "model_gemini_pro" || node.label?.includes("Gemini 2.5 Pro")) return "Gemini 2.5 Pro"
  if (node.id === "model_tiger_data" || node.label?.includes("Tiger Data")) return "Tiger Data"
  if (node.kind === "platform" || node.id === "hub_platform") return "Platform Feed"
  if (node.kind === "topic" || node.id === "hub_community") return "Community Hub"

  if (node.archetype === "skeptic_critic") return "Skeptic Critic"
  if (node.archetype === "viral_amplifier") return "Viral Amplifier"
  if (node.archetype === "casual_scroller") return "Casual Scroller"
  if (node.archetype === "niche_enthusiast") return "Niche Enthusiast"
  if (node.archetype === "industry_expert") return "Industry Expert"

  if (node.kind === "creator") return "Viral Amplifier"
  if (node.kind === "audience") return "Casual Scroller"
  return "Niche Enthusiast"
}

function generateGraphData(customNodes?: Array<any>, customEdges?: Array<any>): { nodes: GraphNode[]; links: GraphLink[] } {
  // If customNodes from MiroFish Swarm are available, map ALL of them dynamically!
  if (customNodes && customNodes.length > 0) {
    const nodes: GraphNode[] = customNodes.map((cn: any) => {
      const type = mapNodeType(cn)
      const isModel = cn.kind === "model"
      const isCore = cn.kind === "core" || cn.id === "0"
      const isHub = cn.kind === "platform" || cn.kind === "topic"

      return {
        id: String(cn.id),
        name: cn.label || cn.name || `Agent ${cn.id}`,
        type: type,
        model: isModel ? cn.label : isCore ? "Candidate Video Post" : isHub ? "Distribution Hub" : "MiroFish OASIS Swarm Persona",
        role: cn.action ? `Action: ${cn.action.toUpperCase()} (${cn.dwell_time_sec || 0}s dwell)` : (cn.kind || "Network Node"),
        uuid: `node-${cn.id}`,
        properties: {
          action: cn.action || "evaluated",
          dwell_time: cn.dwell_time_sec ? `${cn.dwell_time_sec}s` : "12.0s",
          sentiment: cn.sentiment || "neutral",
          round: cn.propagation_round !== undefined ? `Round ${cn.propagation_round}` : "Active",
          archetype: cn.archetype || cn.kind || "participant"
        },
        summary: cn.comment_text || (cn.action === "share" ? "Initiated secondary diffusion cascade to followers." : cn.action === "bounce" ? "Dropped off in first 3 seconds due to pacing lag." : cn.action === "like" ? "Liked and saved post for peer sharing." : "Engaged with content in explore feed."),
        size: cn.size || (isCore ? 24 : isModel ? 16 : isHub ? 15 : (cn.action === "share" ? 13 : 9)),
        x: cn.x,
        y: cn.y
      }
    })

    const links: GraphLink[] = (customEdges && customEdges.length > 0)
      ? customEdges.map((ce: any) => ({
          source: String(ce.source),
          target: String(ce.target),
          rel: ce.rel || "DIFFUSES_TO"
        }))
      : []

    return { nodes, links }
  }

  // Fallback demo graph
  const modelNodes: GraphNode[] = [
    {
      id: "model_gemini_flash",
      name: "Gemini 2.5 Flash",
      type: "Gemini 2.5 Flash",
      model: "Google Gemini 2.5 Flash (Multimodal)",
      role: "Perception & Content DNA Extractor",
      uuid: "gemini-flash-v2.5-perception",
      properties: {
        sampling_rate: "1 FPS video tokens",
        context_window: "1M tokens",
        hook_eval_window: "00:00 - 00:03",
        audio_stream: "Synchronized speech & music"
      },
      summary: "Evaluates visual pacing, on-screen text (OCR), auditory cadence, and 0-3 second hook strength. Seeds the MiroFish knowledge graph.",
      size: 16
    },
    {
      id: "model_mirofish_swarm",
      name: "MiroFish OASIS Swarm",
      type: "MiroFish Swarm",
      model: "CAMEL-AI OASIS / MiroFish Engine",
      role: "Multi-Agent Social Simulation & Diffusion",
      uuid: "mirofish-oasis-swarm-engine",
      properties: {
        population_size: "30-50 agents",
        rounds: "3 propagation stages",
        traits: "Big-Five OCEAN vectors",
        action_space: "Skip, Watch, Like, Comment, Repost"
      },
      summary: "Simulates emergent social network physics. Agents argue in threads, evaluate content against individual skepticism, and initiate diffusion cascades.",
      size: 16
    },
    {
      id: "model_conformal",
      name: "Conformal Regressor",
      type: "Conformal Regressor",
      model: "Non-Parametric Conformal Quantile Predictor",
      role: "Reach & Engagement Uncertainty Calibration",
      uuid: "conformal-quantile-calibrator",
      properties: {
        confidence_level: "90% coverage",
        bounds: "Quantiles [q_0.05, q_0.95]",
        baseline_prior: "Category historical median"
      },
      summary: "Maps multimodal scores and simulated cascade velocity into mathematically bounded reach intervals, avoiding hallucinated view counts.",
      size: 14
    },
    {
      id: "model_gemini_pro",
      name: "Gemini 2.5 Pro",
      type: "Gemini 2.5 Pro",
      model: "Google Gemini 2.5 Pro (Reasoning)",
      role: "Strategic Prescription & Variant B Studio",
      uuid: "gemini-pro-v2.5-synthesizer",
      properties: {
        reasoning_budget: "Dynamic thinking",
        leak_detection: "Timestamped at 00:02.4",
        variant_lift: "+78% reach potential"
      },
      summary: "Arbitrates inter-agent disputes, diagnoses drop-off points, and generates an optimized Variant B hook with projected distribution lift.",
      size: 15
    },
    {
      id: "model_tiger_data",
      name: "Tiger Data Cloud",
      type: "Tiger Data",
      model: "Tiger Data (TimescaleDB / Postgres)",
      role: "Temporal Agent Telemetry & Hypertable Store",
      uuid: "tiger-data-timescaledb-telemetry",
      properties: {
        engine: "PostgreSQL 16 + TimescaleDB",
        table_type: "Hypertable partitioned by time",
        write_latency: "< 2ms ingest"
      },
      summary: "Stores high-throughput second-by-second drop-off points and multi-round propagation logs for sub-millisecond query playback.",
      size: 14
    },
    {
      id: "0",
      name: "Your Video Post",
      type: "Your Video",
      model: "Target Media Asset (MP4/MOV)",
      role: "Draft Content under Pre-Flight Test",
      uuid: "post-draft-0001",
      properties: {
        hook_score: "0.76 / 1.00",
        pacing_cadence: "Cuts at 00:02.4",
        niche: "AI & Tech Storytelling"
      },
      summary: "The candidate creative post evaluated across the entire multi-agent intelligence pipeline before public release.",
      size: 20
    }
  ]

  const audienceNodes: GraphNode[] = [
    {
      id: "agent_skeptic_01",
      name: "Skeptic Critic #001",
      type: "Skeptic Critic",
      model: "MiroFish OASIS Agent",
      role: "Critical Evaluator",
      uuid: "agent-ocean-skeptic-01",
      properties: { skepticism: "0.88", patience: "1.8s", action: "Commented with critique" },
      summary: "Demanded empirical verification around mid-video; questioned authenticity of claims."
    },
    {
      id: "agent_amplifier_01",
      name: "Viral Amplifier #004",
      type: "Viral Amplifier",
      model: "MiroFish OASIS Agent",
      role: "Super-Spreader",
      uuid: "agent-ocean-amplifier-02",
      properties: { extraversion: "0.92", shares: "Re-posted to 12 followers", action: "Share Cascade" },
      summary: "Initiated a Tier 2 secondary network diffusion based on visual clarity."
    },
    {
      id: "agent_scroller_01",
      name: "Casual Scroller #003",
      type: "Casual Scroller",
      model: "MiroFish OASIS Agent",
      role: "Fast Consumer",
      uuid: "agent-ocean-scroller-03",
      properties: { attention_span: "1.2s", action: "Watched 2.4s then skipped" },
      summary: "Skipped at 00:02.4 when pacing hesitated before the punchline."
    },
    {
      id: "agent_enthusiast_01",
      name: "Niche Enthusiast #002",
      type: "Niche Enthusiast",
      model: "MiroFish OASIS Agent",
      role: "Community Insider",
      uuid: "agent-ocean-niche-04",
      properties: { affinity: "0.85", action: "Saved & Liked" },
      summary: "Engaged with the educational breakdown and defended the content in comment threads."
    },
    {
      id: "hub_platform",
      name: "Platform Explore Feed",
      type: "Platform Feed",
      model: "Algorithmic Distribution Engine",
      role: "Recommendation Filter",
      uuid: "hub-explore-recommendation",
      properties: { threshold: "Requires > 65% 3s hold" },
      summary: "Distribution channel that amplifies posts with high early retention and share ratios."
    },
    {
      id: "hub_community",
      name: "Niche Community Hub",
      type: "Community Hub",
      model: "Secondary Follower Cluster",
      role: "Viral Cascade Target",
      uuid: "hub-niche-cluster-42",
      properties: { size: "4,500 active peers" },
      summary: "High-density peer cluster receptive to the core message."
    }
  ]

  const nodes = [...modelNodes, ...audienceNodes]

  const links: GraphLink[] = [
    { source: "0", target: "model_gemini_flash", rel: "PERCEIVES_HOOK" },
    { source: "model_gemini_flash", target: "model_mirofish_swarm", rel: "SEEDS_SWARM" },
    { source: "model_mirofish_swarm", target: "model_conformal", rel: "TRANSMITS_METRICS" },
    { source: "model_mirofish_swarm", target: "model_tiger_data", rel: "LOGS_TELEMETRY" },
    { source: "model_conformal", target: "model_gemini_pro", rel: "CALIBRATES_BOUNDS" },
    { source: "model_gemini_pro", target: "0", rel: "PRESCRIBES_VARIANT_B" },
    { source: "model_mirofish_swarm", target: "agent_skeptic_01", rel: "SPAWNS_PERSONA" },
    { source: "model_mirofish_swarm", target: "agent_amplifier_01", rel: "SPAWNS_PERSONA" },
    { source: "model_mirofish_swarm", target: "agent_scroller_01", rel: "SPAWNS_PERSONA" },
    { source: "model_mirofish_swarm", target: "agent_enthusiast_01", rel: "SPAWNS_PERSONA" },
    { source: "0", target: "agent_scroller_01", rel: "DROPS_OFF_00:02" },
    { source: "0", target: "agent_amplifier_01", rel: "CREATES_CASCADE" },
    { source: "agent_amplifier_01", target: "hub_community", rel: "DIFFUSES_POST" },
    { source: "agent_skeptic_01", target: "agent_enthusiast_01", rel: "DEBATES_IN_THREAD" },
    { source: "agent_amplifier_01", target: "hub_platform", rel: "TRIGGERS_EXPLORE" },
    { source: "hub_platform", target: "model_conformal", rel: "CALIBRATES_REACH" }
  ]

  return { nodes, links }
}