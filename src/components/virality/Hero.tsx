import { useEffect, useState } from "react";
import CrystalizedBall from "@/components/CrystalizedBall";

export function Hero() {
  // canvas can't render on the server (TanStack Start does SSR), so mount on the client only
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="hero-ball" aria-hidden="true">
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
  );
}