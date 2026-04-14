import { useState } from "react";
import { Link } from "react-router-dom";
import ThreeHero from "@/components/ThreeHero";
import PredictionForm from "@/components/PredictionForm";
import ResultPanel from "@/components/ResultPanel";

const Index = () => {
  const [result, setResult] = useState<{ probability: number; isHighRisk: boolean } | null>(null);

  return (
    <div className="min-h-screen">
      <div className="float-up float-up-1">
        <ThreeHero />
      </div>

      {/* Nav to dashboard */}
      <div className="flex justify-center -mt-4 mb-4 relative z-20 float-up float-up-2">
        <Link
          to="/dashboard"
          className="px-5 py-2 rounded-lg glass-card glass-card-hover text-sm text-foreground hover:text-primary transition-colors"
        >
          📊 Dashboard →
        </Link>
      </div>
      <div className="py-12">
        <div className="float-up float-up-3">
          <PredictionForm
            onPredict={(_data, probability, isHighRisk) => {
              setResult(null);
              setTimeout(() => setResult({ probability, isHighRisk }), 100);
            }}
          />
        </div>

        <div className="float-up float-up-4">
          <ResultPanel
            probability={result?.probability ?? 0}
            isHighRisk={result?.isHighRisk ?? false}
            visible={!!result}
          />
        </div>

        <div className="text-center mt-16 pb-8 float-up float-up-5">
          <p className="text-muted-foreground text-sm">
            This is a demonstration model. Not intended for actual financial decisions.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Index;
