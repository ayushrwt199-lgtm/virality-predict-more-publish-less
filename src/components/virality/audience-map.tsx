import { useEffect, useState } from 'react'
import { forceSimulation, forceLink, forceManyBody, forceCenter, forceCollide, type SimulationNodeDatum } from 'd3-force'
import { Maximize2, Minus, Plus, RotateCcw, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

type Node = SimulationNodeDatum & { id: string; label: string; kind: string; size: number }
const labels = ['Your video','Creators','Gen Z','Lifestyle','Storytelling','Students','Young professionals','Discovery','Community','Trends','Tech enthusiasts','Early adopters','Reels','Entertainment','Shareability','Culture','Curiosity','Authenticity','Visual hook','Music','Comments','Friends','Interest clusters','Watch time','Inspiration','Design','Micro creators','Instagram','YouTube','TikTok']
export function AudienceMap() {
  const [nodes,setNodes]=useState<Node[]>([])
  const [edges,setEdges]=useState<{source:Node;target:Node}[]>([])
  const [zoom,setZoom]=useState(1)
  const [selected,setSelected]=useState('')
  const [expanded,setExpanded]=useState(false)
  const [revision,setRevision]=useState(0)
  const selectedNode=nodes.find(n=>n.label===selected)
  const connections=selectedNode?edges.filter(e=>e.source.id===selectedNode.id||e.target.id===selectedNode.id).map(e=>e.source.id===selectedNode.id?e.target.label:e.source.label):[]
  const category=selectedNode?selectedNode.kind==='core'?'Video':selectedNode.kind[0]?.toUpperCase()+selectedNode.kind.slice(1):''
  useEffect(()=>{
    const data:Node[]=labels.map((label,i)=>({id:String(i),label,kind:i===0?'core':(['creator','audience','topic','platform'][i%4]??'audience'),size:i===0?22:i<9?10:6,x:380+Math.cos(i*2.4)*200,y:245+Math.sin(i*2.4)*180}))
    const links= data.slice(1).map((n,i)=>({source:n.id,target:i<8?'0':String(1+i%8)}))
    links.push(...data.slice(10).map((n,i)=>({source:n.id,target:String((i*3+2)%28+1)})))
    const sim=forceSimulation(data).force('link',forceLink<Node,any>(links).id(n=>n.id).distance(95)).force('charge',forceManyBody().strength(-210)).force('center',forceCenter(380,245)).force('collide',forceCollide(28)).stop()
    for(let i=0;i<180;i++) sim.tick()
    setNodes(data.map(n=>({...n,x:Math.max(55,Math.min(710,n.x??380)),y:Math.max(50,Math.min(425,n.y??245))})))
    setEdges(links as unknown as {source:Node;target:Node}[])
    return ()=>{sim.stop()}
  },[revision])
  return <div className={`audience-map ${expanded?'map-expanded':''}`}>
    <div className="map-top"><div><span className="status-dot" />Audience relationships <span className="map-example">EXAMPLE MAP</span></div><Button size="icon" variant="ghost" title={expanded?'Close expanded map':'Expand map'} onClick={()=>setExpanded(!expanded)}>{expanded?<X/>:<Maximize2/>}</Button></div>
    <svg viewBox="0 0 760 490" className="graph-svg" aria-label="Interactive example audience relationship map"><g transform={`translate(${380-380*zoom} ${245-245*zoom}) scale(${zoom})`}>{edges.map((e,i)=><line key={i} x1={e.source.x} y1={e.source.y} x2={e.target.x} y2={e.target.y} className="graph-edge" />)}{nodes.map((n,i)=><g key={n.id} transform={`translate(${n.x} ${n.y})`} className={`graph-node node-${n.kind} ${selected===n.label?'selected':''}`} onClick={()=>setSelected(n.label)} role="button" tabIndex={0} aria-label={n.label} onKeyDown={e=>{if(e.key==='Enter')setSelected(n.label)}}><circle r={n.size+7} className="node-halo"/><circle r={n.size}/><text x={n.id==='0'?0:n.size+8} y={n.id==='0'?40:4} textAnchor={n.id==='0'?'middle':'start'} className={i<9?'node-label':'node-label small'}>{n.label}</text></g>)}</g></svg>
    {selectedNode&&<div className={`node-inspector inspector-${selectedNode.kind}`} role="region" aria-label="Node details"><header><h3>Node Details</h3><span className="node-category">{category}</span><Button variant="ghost" size="icon" onClick={()=>setSelected('')} title="Close node details" aria-label="Close node details"><X/></Button></header><div className="inspector-body"><dl className="node-metadata"><dt>Name</dt><dd>{selectedNode.label}</dd><dt>UUID</dt><dd className="node-uuid">00000000-0000-4000-8000-{selectedNode.id.padStart(12,'0')}</dd><dt>Created</dt><dd>Current session</dd></dl><section><h4>Properties</h4><dl className="node-metadata"><dt>name</dt><dd>{selectedNode.label}</dd><dt>entity_type</dt><dd>{category}</dd><dt>connections</dt><dd>{connections.length}</dd><dt>related_to</dt><dd>{connections.join(', ')||'Your video'}</dd></dl></section><section><h4>Summary</h4><p>{selectedNode.label} is an example {category.toLowerCase()} node in your video's audience network. It connects with {connections.slice(0,3).join(', ')||'your video'}{connections.length>3?' and other communities':''}.</p></section><section><h4>Labels</h4><div className="node-label-tags"><span>Entity</span><span>{category}</span><span>{selectedNode.label}</span></div></section><small>Example node · illustrative relationships</small></div></div>}
    <div className="map-bottom"><div className="map-legend">{['Creator','Audience','Topic','Platform'].map(x=><span key={x}><i className={`legend-${x.toLowerCase()}`}/>{x}</span>)}</div><div className="map-tools"><Button title="Zoom out" size="icon" variant="ghost" onClick={()=>setZoom(Math.max(.6,zoom-.15))}><Minus/></Button><span>{Math.round(zoom*100)}%</span><Button title="Zoom in" size="icon" variant="ghost" onClick={()=>setZoom(Math.min(1.6,zoom+.15))}><Plus/></Button><Button title="Reset map" size="icon" variant="ghost" onClick={()=>{setZoom(1);setRevision(revision+1)}}><RotateCcw/></Button></div></div>
  </div>
}