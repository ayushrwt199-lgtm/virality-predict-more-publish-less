import { useEffect, useState } from "react";
import CrystalizedBall from "@/components/CrystalizedBall";

export function Hero({ name = "Virality" }: { name?: string }) {
  // canvas/WebGL can't render on the server, so mount on the client only
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <section className="hero">
      <div className="hero-ball">
        {mounted && (
          <CrystalizedBall
            preset="plasma"
            color="#F25BD0"
            size={0.7}
            crackle={0.85}
            fill={0.5}
            interactive
            hoverStrength={0.7}
          />
        )}
      </div>
      <h1 className="hero-title">{name}</h1>
    </section>
  );
}
