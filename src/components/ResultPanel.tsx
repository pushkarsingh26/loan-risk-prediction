import { useEffect, useRef, useState, useCallback } from "react";

interface ResultPanelProps {
  probability: number;
  isHighRisk: boolean;
  visible: boolean;
}

// Animated counter hook
function useCounter(target: number, duration: number, active: boolean) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (!active) { setValue(0); return; }
    const start = performance.now();
    let raf: number;
    const step = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      setValue(Math.round(eased * target));
      if (progress < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, active]);
  return value;
}

// SVG semicircular gauge
const RiskGauge = ({ percentage, isHighRisk, animate }: { percentage: number; isHighRisk: boolean; animate: boolean }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!animate) { setProgress(0); return; }
    const start = performance.now();
    let raf: number;
    const step = (now: number) => {
      const p = Math.min((now - start) / 1500, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setProgress(eased * percentage);
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [percentage, animate]);

  const r = 80;
  const cx = 100;
  const cy = 100;
  const circumference = Math.PI * r;
  const dashOffset = circumference - (progress / 100) * circumference;

  // Tick marks
  const ticks = Array.from({ length: 11 }, (_, i) => {
    const angle = Math.PI + (i / 10) * Math.PI;
    const inner = r - 8;
    const outer = r + 4;
    return {
      x1: cx + Math.cos(angle) * inner,
      y1: cy + Math.sin(angle) * inner,
      x2: cx + Math.cos(angle) * outer,
      y2: cy + Math.sin(angle) * outer,
      label: i * 10,
    };
  });

  // Needle
  const needleAngle = Math.PI + (progress / 100) * Math.PI;
  const needleLen = r - 16;
  const nx = cx + Math.cos(needleAngle) * needleLen;
  const ny = cy + Math.sin(needleAngle) * needleLen;

  const gaugeColor = isHighRisk ? "hsl(0, 72%, 51%)" : "hsl(142, 71%, 45%)";
  const glowFilter = isHighRisk ? "drop-shadow(0 0 6px hsla(0,72%,51%,0.6))" : "drop-shadow(0 0 6px hsla(142,71%,45%,0.6))";

  return (
    <svg viewBox="0 0 200 120" className="w-64 h-auto mx-auto">
      {/* Background arc */}
      <path
        d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none"
        stroke="hsla(230, 30%, 25%, 0.5)"
        strokeWidth="8"
        strokeLinecap="round"
      />
      {/* Foreground arc */}
      <path
        d={`M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`}
        fill="none"
        stroke={gaugeColor}
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={dashOffset}
        style={{ filter: glowFilter, transition: "stroke 0.3s" }}
      />
      {/* Tick marks */}
      {ticks.map((t, i) => (
        <g key={i}>
          <line x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} stroke="hsla(226,100%,94%,0.3)" strokeWidth={i % 5 === 0 ? 2 : 1} />
          {i % 5 === 0 && (
            <text x={t.x2 + Math.cos(Math.PI + (i / 10) * Math.PI) * 12} y={t.y2 + Math.sin(Math.PI + (i / 10) * Math.PI) * 12} textAnchor="middle" dominantBaseline="middle" fill="hsla(226,100%,94%,0.4)" fontSize="8">
              {t.label}
            </text>
          )}
        </g>
      ))}
      {/* Needle */}
      <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={gaugeColor} strokeWidth="2.5" strokeLinecap="round" style={{ filter: glowFilter }} />
      <circle cx={cx} cy={cy} r="4" fill={gaugeColor} style={{ filter: glowFilter }} />
    </svg>
  );
};

// Particle burst on canvas
const ParticleBurst = ({ isHighRisk, trigger }: { isHighRisk: boolean; trigger: boolean }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!trigger) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = canvas.offsetWidth * 2;
    canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);

    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;
    const color = isHighRisk ? [239, 68, 68] : [34, 197, 94];

    const particles = Array.from({ length: 80 }, () => ({
      x: w / 2,
      y: h / 2,
      vx: (Math.random() - 0.5) * 8,
      vy: (Math.random() - 0.5) * 8,
      life: 1,
      size: Math.random() * 3 + 1,
    }));

    const start = performance.now();
    let raf: number;

    const draw = (now: number) => {
      const elapsed = (now - start) / 1200;
      if (elapsed > 1) return;

      ctx.clearRect(0, 0, w, h);
      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.98;
        p.vy *= 0.98;
        p.life = 1 - elapsed;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${p.life})`;
        ctx.fill();
      });
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [trigger, isHighRisk]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ width: "100%", height: "100%" }}
    />
  );
};

// Animated SVG ring
const ProgressRing = ({ percentage, isHighRisk, animate }: { percentage: number; isHighRisk: boolean; animate: boolean }) => {
  const [offset, setOffset] = useState(283);
  const r = 45;
  const circumference = 2 * Math.PI * r;

  useEffect(() => {
    if (!animate) { setOffset(circumference); return; }
    const target = circumference - (percentage / 100) * circumference;
    const start = performance.now();
    const from = circumference;
    let raf: number;
    const step = (now: number) => {
      const p = Math.min((now - start) / 1200, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setOffset(from + (target - from) * eased);
      if (p < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [percentage, animate, circumference]);

  const color = isHighRisk ? "hsl(0, 72%, 51%)" : "hsl(142, 71%, 45%)";
  const glow = isHighRisk ? "drop-shadow(0 0 8px hsla(0,72%,51%,0.5))" : "drop-shadow(0 0 8px hsla(142,71%,45%,0.5))";

  return (
    <svg className="w-28 h-28" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r={r} fill="none" stroke="hsla(230,30%,25%,0.4)" strokeWidth="6" />
      <circle
        cx="50" cy="50" r={r} fill="none"
        stroke={color} strokeWidth="6" strokeLinecap="round"
        strokeDasharray={circumference} strokeDashoffset={offset}
        transform="rotate(-90 50 50)"
        style={{ filter: glow }}
      />
    </svg>
  );
};

const ResultPanel = ({ probability, isHighRisk, visible }: ResultPanelProps) => {
  const [flipped, setFlipped] = useState(false);
  const counter = useCounter(probability, 1000, flipped);

  useEffect(() => {
    if (visible) {
      const timeout = setTimeout(() => setFlipped(true), 200);
      return () => clearTimeout(timeout);
    }
    setFlipped(false);
  }, [visible]);

  if (!visible) return null;

  return (
    <div className="w-full max-w-2xl mx-auto px-4 mt-12" style={{ perspective: "1200px" }}>
      <div
        className={`relative w-full ${flipped ? "defy-gravity" : ""}`}
        style={{ transformStyle: "preserve-3d" }}
      >
        <div className="glass-card rounded-2xl p-8 relative overflow-hidden">
          <ParticleBurst isHighRisk={isHighRisk} trigger={flipped} />

          <div className="relative z-10 flex flex-col items-center gap-6">
            <h3 className="text-2xl font-bold text-foreground">Prediction Result</h3>

            {/* Risk Gauge */}
            <RiskGauge percentage={probability} isHighRisk={isHighRisk} animate={flipped} />

            <div className="flex items-center gap-6">
              {/* Progress Ring with counter */}
              <div className="relative flex items-center justify-center">
                <ProgressRing percentage={probability} isHighRisk={isHighRisk} animate={flipped} />
                <span className="absolute text-2xl font-bold text-foreground">
                  {counter}%
                </span>
              </div>

              <div className="text-center">
                <div className={`text-3xl font-bold ${isHighRisk ? "text-destructive" : "text-success"}`}>
                  {isHighRisk ? "🔴 High Risk" : "🟢 Low Risk"}
                </div>
                <p className="text-muted-foreground mt-1">
                  {isHighRisk
                    ? "This borrower profile indicates elevated default probability."
                    : "This borrower profile shows strong repayment likelihood."}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultPanel;
