import { useEffect, useRef } from "react";

type Preset = "plasma" | "crystal" | "ember";
interface Props {
  preset?: Preset;
  color?: string;
  size?: number;
  crackle?: number;
  fill?: number;
  interactive?: boolean;
  hoverStrength?: number;
}

const PRESETS = {
  plasma: { speed: 1, jag: 0.16, core: 0.9 },
  crystal: { speed: 0.55, jag: 0.08, core: 0.6 },
  ember: { speed: 0.8, jag: 0.22, core: 1 },
};

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

type Bolt = { born: number; life: number; pts: [number, number][]; w: number };

export default function CrystalizedBall({
  preset = "plasma",
  color = "#F25BD0",
  size = 0.7,
  crackle = 0.85,
  fill = 0.5,
  interactive = true,
  hoverStrength = 0.7,
}: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;

    const cfg = PRESETS[preset] ?? PRESETS.plasma;
    const [r, g, b] = hexToRgb(color);
    const rgba = (a: number) => `rgba(${r},${g},${b},${a})`;
    const tint = (a: number) =>
      `rgba(${Math.round(r + (255 - r) * 0.75)},${Math.round(g + (255 - g) * 0.75)},${Math.round(b + (255 - b) * 0.75)},${a})`;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const TAU = Math.PI * 2;
    const count = Math.round(5 + crackle * 16);
    const bolts: Bolt[] = [];
    const mouse = { x: 0, y: 0, tx: 0, ty: 0, on: false };
    let W = 0, H = 0, raf = 0;

    function resize() {
      const rect = canvas!.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = rect.width;
      H = rect.height;
      canvas!.width = W * dpr;
      canvas!.height = H * dpr;
      ctx!.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (reduce) frame(1500);
    }

    function makeBolt(now: number, R: number): Bolt {
      let a = Math.random() * TAU;
      if (interactive && mouse.on && Math.random() < hoverStrength) {
        a = Math.atan2(mouse.ty, mouse.tx) + (Math.random() - 0.5) * 0.9;
      }
      const dx = Math.cos(a), dy = Math.sin(a);
      const segs = 9 + Math.floor(Math.random() * 6);
      const pts: [number, number][] = [[0, 0]];
      for (let i = 1; i <= segs; i++) {
        const d = (R * i) / segs;
        const off = (Math.random() - 0.5) * R * cfg.jag * (i < segs ? 1 : 0.2);
        pts.push([dx * d - dy * off, dy * d + dx * off]);
      }
      return { born: now, life: 350 + Math.random() * 700, pts, w: 0.6 + Math.random() * 1.4 };
    }

    function frame(ms: number) {
      const t = (ms / 1000) * cfg.speed;
      mouse.x += (mouse.tx - mouse.x) * 0.06;
      mouse.y += (mouse.ty - mouse.y) * 0.06;
      const R = (Math.min(W, H) * size) / 2;
      const breathe = 1 + Math.sin(t * 1.4) * 0.015;
      const par = interactive ? 0.05 * hoverStrength : 0;
      const cx = W / 2 + (mouse.on ? mouse.x * par : 0);
      const cy = H / 2 + (mouse.on ? mouse.y * par : 0);

      ctx!.clearRect(0, 0, W, H);
      ctx!.save();
      ctx!.translate(cx, cy);

      // outer glow
      let gr = ctx!.createRadialGradient(0, 0, R * 0.6, 0, 0, R * 1.7);
      gr.addColorStop(0, rgba(0.28 * cfg.core));
      gr.addColorStop(1, rgba(0));
      ctx!.fillStyle = gr;
      ctx!.beginPath();
      ctx!.arc(0, 0, R * 1.7, 0, TAU);
      ctx!.fill();

      // glass body
      gr = ctx!.createRadialGradient(-R * 0.25, -R * 0.3, R * 0.05, 0, 0, R * breathe);
      gr.addColorStop(0, rgba(0.2 + fill * 0.55));
      gr.addColorStop(0.7, rgba(0.1 + fill * 0.25));
      gr.addColorStop(1, rgba(0.4));
      ctx!.fillStyle = gr;
      ctx!.beginPath();
      ctx!.arc(0, 0, R * breathe, 0, TAU);
      ctx!.fill();
      ctx!.strokeStyle = rgba(0.6);
      ctx!.lineWidth = 1.5;
      ctx!.stroke();

      // lightning inside the sphere
      ctx!.save();
      ctx!.beginPath();
      ctx!.arc(0, 0, R * breathe, 0, TAU);
      ctx!.clip();
      ctx!.lineJoin = "round";
      for (let i = 0; i < count; i++) {
        let bo = bolts[i];
        if (!bo) bo = bolts[i] = makeBolt(ms - Math.random() * 600, R);
        else if (ms - bo.born > bo.life) bo = bolts[i] = makeBolt(ms, R);
        const age = (ms - bo.born) / bo.life;
        const a = Math.sin(age * Math.PI) * (0.6 + 0.4 * Math.sin(ms * 0.04 + i));
        if (a <= 0) continue;
        ctx!.beginPath();
        bo.pts.forEach(([x, y], k) => (k ? ctx!.lineTo(x, y) : ctx!.moveTo(x, y)));
        ctx!.strokeStyle = rgba(0.35 * a);
        ctx!.lineWidth = bo.w * 5;
        ctx!.stroke();
        ctx!.strokeStyle = tint(a);
        ctx!.lineWidth = bo.w;
        ctx!.stroke();
      }
      gr = ctx!.createRadialGradient(0, 0, 0, 0, 0, R * 0.35);
      gr.addColorStop(0, tint(0.85));
      gr.addColorStop(1, rgba(0));
      ctx!.fillStyle = gr;
      ctx!.beginPath();
      ctx!.arc(0, 0, R * 0.35, 0, TAU);
      ctx!.fill();
      ctx!.restore();
      ctx!.restore();

      if (!reduce) raf = requestAnimationFrame(frame);
    }

    function onMove(e: PointerEvent) {
      const rect = canvas!.getBoundingClientRect();
      mouse.tx = e.clientX - (rect.left + rect.width / 2);
      mouse.ty = e.clientY - (rect.top + rect.height / 2);
      mouse.on =
        e.clientX >= rect.left && e.clientX <= rect.right && e.clientY >= rect.top && e.clientY <= rect.bottom;
    }

    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
    resize();
    if (interactive) window.addEventListener("pointermove", onMove);
    if (!reduce) raf = requestAnimationFrame(frame);

    return () => {
      cancelAnimationFrame(raf);
      ro.disconnect();
      window.removeEventListener("pointermove", onMove);
    };
  }, [preset, color, size, crackle, fill, interactive, hoverStrength]);

  return <canvas ref={ref} aria-hidden="true" style={{ width: "100%", height: "100%", display: "block" }} />;
}