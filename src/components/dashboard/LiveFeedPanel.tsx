import { useEffect, useState } from "react";

interface FeedEntry {
  id: number;
  name: string;
  age: number;
  amount: string;
  risk: "High" | "Low";
  score: number;
}

const NAMES = ["J. Martinez", "S. Patel", "A. Thompson", "M. Chen", "R. Williams", "K. Johnson", "D. Brown", "L. Kim", "N. Davis", "T. Wilson"];
const AMOUNTS = ["$12,000", "$45,000", "$8,500", "$32,000", "$18,750", "$55,000", "$22,000", "$6,800", "$40,000", "$15,300"];

let counter = 0;
function generateEntry(): FeedEntry {
  counter++;
  const isHigh = Math.random() > 0.65;
  return {
    id: counter,
    name: NAMES[Math.floor(Math.random() * NAMES.length)],
    age: 22 + Math.floor(Math.random() * 40),
    amount: AMOUNTS[Math.floor(Math.random() * AMOUNTS.length)],
    risk: isHigh ? "High" : "Low",
    score: isHigh ? 450 + Math.floor(Math.random() * 200) : 650 + Math.floor(Math.random() * 150),
  };
}

const LiveFeedPanel = () => {
  const [entries, setEntries] = useState<FeedEntry[]>(() =>
    Array.from({ length: 5 }, generateEntry)
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setEntries((prev) => [generateEntry(), ...prev.slice(0, 7)]);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="glass-card rounded-2xl p-6 overflow-hidden">
      <div className="flex items-center gap-2 mb-4">
        <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
        <h3 className="text-lg font-semibold text-foreground">Live Predictions</h3>
      </div>
      <div className="space-y-2 max-h-[360px] overflow-hidden">
        {entries.map((entry, i) => (
          <div
            key={entry.id}
            className={`flex items-center justify-between px-4 py-3 rounded-lg bg-secondary/50 ${i === 0 ? "slide-in-right" : ""}`}
          >
            <div className="flex flex-col">
              <span className="text-sm font-medium text-foreground">
                {entry.name}, {entry.age}
              </span>
              <span className="text-xs text-muted-foreground">
                Loan: {entry.amount} · Score: {entry.score}
              </span>
            </div>
            <span
              className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                entry.risk === "High"
                  ? "bg-destructive/20 text-destructive"
                  : "bg-success/20 text-success"
              }`}
            >
              {entry.risk === "High" ? "🔴 High" : "🟢 Low"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveFeedPanel;
