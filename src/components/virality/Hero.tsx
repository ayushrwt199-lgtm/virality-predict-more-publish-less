import { useEffect, useRef, useState } from "react";
import { CursorGrid } from "@/components/virality/brand";

/**
 * HalftoneRing — a canvas-drawn circular halftone dot pattern that
 * slowly rotates, matching the reference hero design (purple dots
 * arranged in a ring, fading in/out at the edges).
 */
export function Hero() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <>
      <CursorGrid />
      <div className="hero-halo-wrap" aria-hidden="true">
        {mounted && <HalftoneRing />}
      </div>
    </>
  );
}

function HalftoneRing() {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    const size = 660;
    canvas.width = size;
    canvas.height = size;

    const cx = size / 2;
    const cy = size / 2;
    const ringRadius = 234;
    const color = "oklch(0.58 0.26 285)";

    let frame = 0;

    function draw(time: number) {
      if (!ctx || !canvas) return;
      ctx.clearRect(0, 0, size, size);
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(reduced ? 0 : (time / 140000) * Math.PI * 2);
      ctx.translate(-cx, -cy);

      const step = 10;
      for (let x = 25; x < size - 25; x += step) {
        for (let y = 25; y < size - 25; y += step) {
          const dx = x - cx;
          const dy = y - cy;
          const d = Math.hypot(dx, dy);

          // Gaussian ring falloff (centered around radius 234)
          const distFromRing = d - ringRadius;
          const intensity = Math.exp(
            -Math.pow(distFromRing / 36, 2)
          );

          if (intensity < 0.02) continue;

          // Subtle harmonic wave
          const wave = reduced
            ? 0
            : Math.sin(time * 0.0003 + Math.atan2(dy, dx) * 3) * 0.08;

          const alpha = Math.min(0.85, intensity * (0.8 + wave));
          const dotSize = Math.max(0.7, intensity * 3.8);

          ctx.globalAlpha = alpha;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(x, y, dotSize, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      ctx.restore();
      if (!reduced) frame = requestAnimationFrame(draw);
    }

    frame = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <canvas
      ref={ref}
      className="hero-halftone-canvas"
      aria-hidden="true"
      style={{
        position: "absolute",
        width: "600px",
        height: "600px",
        maxWidth: "92vw",
        maxHeight: "92vw",
        pointerEvents: "none",
        opacity: 0.88,
      }}
    />
  );
}