import { Activity, AlertTriangle, CreditCard, TrendingDown } from "lucide-react";

const STATS = [
  { label: "Total Applications", value: "1,240", icon: Activity, glowColor: "hsla(239, 84%, 67%, 0.3)", delay: "0s" },
  { label: "High Risk %", value: "25%", icon: AlertTriangle, glowColor: "hsla(0, 72%, 51%, 0.3)", delay: "0.5s" },
  { label: "Avg Credit Score", value: "648", icon: CreditCard, glowColor: "hsla(38, 92%, 50%, 0.3)", delay: "1s" },
  { label: "Default Rate", value: "8.9%", icon: TrendingDown, glowColor: "hsla(173, 80%, 40%, 0.3)", delay: "1.5s" },
];

const FloatingStatCards = () => (
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    {STATS.map((stat, i) => (
      <div
        key={stat.label}
        className={`glass-card glass-card-hover rounded-xl p-5 bounce-up bounce-up-${i + 1}`}
        style={{
          boxShadow: `0 0 24px ${stat.glowColor}, inset 0 1px 0 hsla(0,0%,100%,0.05)`,
        }}
      >
        <div className="flex items-center gap-3 mb-3">
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center"
            style={{ background: stat.glowColor }}
          >
            <stat.icon className="w-5 h-5 text-foreground" />
          </div>
          <span className="text-sm text-muted-foreground">{stat.label}</span>
        </div>
        <p className="text-3xl font-bold text-foreground">{stat.value}</p>
      </div>
    ))}
  </div>
);

export default FloatingStatCards;
