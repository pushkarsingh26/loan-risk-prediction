import { useEffect, useRef } from "react";

/**
 * FX 04 — Starfield background
 * Canvas-based floating dots drifting upward to create a zero-gravity space vibe.
 * Uses multiple speed layers for parallax depth.
 */

interface Star {
  x: number;
  y: number;
  r: number;        // radius
  speed: number;    // upward speed
  opacity: number;
  drift: number;    // horizontal wobble amplitude
  phase: number;    // wobble phase offset
}

const STAR_COUNT = 120;
const COLORS = [
  [99, 102, 241],   // indigo (primary)
  [139, 92, 246],   // purple (accent)
  [45, 212, 191],   // teal
  [226, 232, 255],  // soft white-blue
];

const Starfield = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let stars: Star[] = [];
    let w = 0;
    let h = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio, 2);
      w = canvas.parentElement?.clientWidth ?? window.innerWidth;
      h = canvas.parentElement?.clientHeight ?? window.innerHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const createStar = (randomY = false): Star => ({
      x: Math.random() * w,
      y: randomY ? Math.random() * h : h + Math.random() * 40,
      r: 0.6 + Math.random() * 1.8,
      speed: 0.15 + Math.random() * 0.6,
      opacity: 0.15 + Math.random() * 0.55,
      drift: 0.3 + Math.random() * 0.8,
      phase: Math.random() * Math.PI * 2,
    });

    const init = () => {
      resize();
      stars = Array.from({ length: STAR_COUNT }, () => createStar(true));
    };

    const draw = (time: number) => {
      ctx.clearRect(0, 0, w, h);
      const t = time * 0.001;

      for (let i = 0; i < stars.length; i++) {
        const s = stars[i];

        // Move upward
        s.y -= s.speed;

        // Gentle horizontal wobble
        const wobbleX = Math.sin(t * 0.8 + s.phase) * s.drift;

        // Fade based on vertical position (fade in at bottom, fade out at top)
        const edgeFade = Math.min(
          s.y / (h * 0.15),         // fade in from bottom
          (h - s.y) / (h * 0.85),   // always visible until very top
          1
        );
        const alpha = Math.max(0, s.opacity * Math.max(0, edgeFade));

        // Pick color based on star index
        const color = COLORS[i % COLORS.length];

        // Draw glow
        ctx.beginPath();
        ctx.arc(s.x + wobbleX, s.y, s.r * 3, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha * 0.15})`;
        ctx.fill();

        // Draw core
        ctx.beginPath();
        ctx.arc(s.x + wobbleX, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha})`;
        ctx.fill();

        // Recycle stars that drift above the viewport
        if (s.y < -10) {
          stars[i] = createStar(false);
        }
      }

      animId = requestAnimationFrame(draw);
    };

    init();
    animId = requestAnimationFrame(draw);
    window.addEventListener("resize", resize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
      aria-hidden="true"
    />
  );
};

export default Starfield;
