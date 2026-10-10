import { useEffect, useRef } from 'react'

export function LogoMark({ className = '' }: { className?: string }) {
  return <svg className={className} viewBox="0 0 100 100" fill="none" aria-label="VIRALITY logo"><path d="M30 13a43 43 0 1 1 0 74 34 34 0 0 0 0-74" fill="currentColor" />{[26,35,44,53,62,71].map((y,i)=><path key={y} d={`M${12-i%2*5} ${y}H${43-i%2*4}`} stroke="currentColor" strokeWidth="4.5" strokeLinecap="round" />)}</svg>
}

export function BrandHalo() {
  const ref = useRef<HTMLCanvasElement>(null)
  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let frame = 0
    const styles = getComputedStyle(canvas)
    const color = styles.getPropertyValue('--halo').trim()
    const turnDuration = Number(styles.getPropertyValue('--halo-turn-ms')) || 90000
    canvas.width = 660; canvas.height = 660
    function draw(time: number) {
      if (!ctx || !canvas) return
      const size = 660
      ctx.clearRect(0,0,size,size)
      ctx.save()
      ctx.translate(330,330)
      ctx.rotate(reduced?0:time/turnDuration*Math.PI*2)
      ctx.translate(-330,-330)
      for(let x=35;x<630;x+=10) for(let y=35;y<630;y+=10) {
        const dx=x-330,dy=y-330,d=Math.hypot(dx,dy)
        const wave=reduced?0:Math.sin(time*.0005+Math.atan2(dy,dx)*3)*5
        const intensity=Math.exp(-Math.pow((d-235-wave)/35,2))
        if(intensity<.025) continue
        ctx.globalAlpha=intensity*.85
        ctx.fillStyle=color
        ctx.beginPath();ctx.arc(x,y,Math.max(.7,intensity*3.9),0,Math.PI*2);ctx.fill()
      }
      ctx.restore()
      if(!reduced) frame=requestAnimationFrame(draw)
    }
    frame=requestAnimationFrame(draw)
    return ()=>cancelAnimationFrame(frame)
  },[])
  return <><CursorGrid/><canvas ref={ref} className="brand-halo" aria-hidden="true" /></>
}

function CursorGrid() {
  const ref=useRef<HTMLCanvasElement>(null)
  useEffect(()=>{
    const canvas=ref.current
    if(!canvas)return
    const ctx=canvas.getContext('2d')
    if(!ctx)return
    const media=window.matchMedia('(prefers-reduced-motion: reduce)')
    const color=getComputedStyle(canvas).getPropertyValue('--grid-focus').trim()
    let frame=0,width=0,height=0,active=false,opacity=0
    let x=0,y=0,targetX=0,targetY=0
    function resize(){
      if(!canvas||!ctx)return
      width=window.innerWidth;height=window.innerHeight
      const ratio=Math.min(window.devicePixelRatio,2)
      canvas.width=width*ratio;canvas.height=height*ratio
      ctx.setTransform(ratio,0,0,ratio,0,0)
    }
    function draw(){
      if(!ctx)return
      frame=0
      ctx.clearRect(0,0,width,height)
      if(media.matches)return
      x+=(targetX-x)*.09;y+=(targetY-y)*.09
      opacity+=((active?1:0)-opacity)*.08
      if(opacity<.005&&!active)return
      ctx.strokeStyle=color;ctx.lineWidth=1
      const radius=220,offset=window.scrollY%48
      function point(px:number,py:number){
        const dx=px-x,dy=py-y,d=Math.hypot(dx,dy),focus=Math.max(0,1-d/radius)
        const bend=focus*focus*10
        return {x:px+(dx/Math.max(d,1))*bend,y:py+(dy/Math.max(d,1))*bend,alpha:focus*focus*opacity}
      }
      function segment(ax:number,ay:number,bx:number,by:number){
        if(!ctx)return
        const a=point(ax,ay),b=point(bx,by)
        ctx.globalAlpha=(a.alpha+b.alpha)/2
        if(ctx.globalAlpha<.005)return
        ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()
      }
      const left=Math.max(0,Math.floor((x-radius)/48)*48),right=Math.min(width,x+radius)
      const top=Math.max(-offset,Math.floor((y-radius+offset)/48)*48-offset),bottom=Math.min(height,y+radius)
      for(let px=left;px<=right;px+=48)for(let py=top;py<bottom;py+=8)segment(px,py,px,py+8)
      for(let py=top;py<=bottom;py+=48)for(let px=left;px<right;px+=8)segment(px,py,px+8,py)
      frame=requestAnimationFrame(draw)
    }
    function move(e:PointerEvent){
      if(e.pointerType==='touch'||media.matches)return
      targetX=e.clientX;targetY=e.clientY
      if(!active&&opacity<.005){x=targetX;y=targetY}
      active=true
      if(!frame)frame=requestAnimationFrame(draw)
    }
    function leave(){active=false}
    function preference(){active=false;opacity=0;ctx?.clearRect(0,0,width,height)}
    resize()
    window.addEventListener('resize',resize)
    window.addEventListener('pointermove',move)
    document.documentElement.addEventListener('pointerleave',leave)
    window.addEventListener('blur',leave)
    media.addEventListener('change',preference)
    return()=>{cancelAnimationFrame(frame);window.removeEventListener('resize',resize);window.removeEventListener('pointermove',move);document.documentElement.removeEventListener('pointerleave',leave);window.removeEventListener('blur',leave);media.removeEventListener('change',preference)}
  },[])
  return <canvas ref={ref} className="cursor-grid" aria-hidden="true"/>
}