import { useState, useRef, useEffect, useCallback } from "react";

interface PredictionFormProps {
  onPredict: (data: FormData, probability: number, isHighRisk: boolean) => void;
}

interface FormData {
  age: string;
  monthlyIncome: string;
  loanAmount: string;
  creditScore: string;
  employmentType: string;
  loanTerm: string;
  existingDebts: string;
}

const FIELDS: { key: keyof FormData; label: string; type: "number" | "select"; placeholder?: string; options?: string[] }[] = [
  { key: "age", label: "Age", type: "number", placeholder: "28" },
  { key: "monthlyIncome", label: "Monthly Income ($)", type: "number", placeholder: "5000" },
  { key: "loanAmount", label: "Loan Amount ($)", type: "number", placeholder: "25000" },
  { key: "creditScore", label: "Credit Score", type: "number", placeholder: "720" },
  { key: "employmentType", label: "Employment Type", type: "select", options: ["Full-time", "Part-time", "Self-employed", "Freelancer", "Unemployed"] },
  { key: "loanTerm", label: "Loan Term (months)", type: "number", placeholder: "36" },
  { key: "existingDebts", label: "Existing Debts ($)", type: "number", placeholder: "8000" },
];

const PredictionForm = ({ onPredict }: PredictionFormProps) => {
  const [form, setForm] = useState<FormData>({
    age: "", monthlyIncome: "", loanAmount: "", creditScore: "",
    employmentType: "Full-time", loanTerm: "", existingDebts: "",
  });
  const [loading, setLoading] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const fieldRefs = useRef<(HTMLDivElement | null)[]>([]);

  // Tilt effect
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const card = cardRef.current;
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `perspective(800px) rotateY(${x * 15}deg) rotateX(${-y * 15}deg)`;
    // Move specular highlight
    const highlight = card.querySelector<HTMLDivElement>(".specular");
    if (highlight) {
      highlight.style.background = `radial-gradient(circle at ${(x + 0.5) * 100}% ${(y + 0.5) * 100}%, hsla(239, 84%, 67%, 0.12) 0%, transparent 60%)`;
    }
  }, []);

  const handleMouseLeave = useCallback(() => {
    const card = cardRef.current;
    if (card) card.style.transform = "perspective(800px) rotateY(0deg) rotateX(0deg)";
  }, []);

  // Intersection Observer for staggered field reveal
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
          }
        });
      },
      { threshold: 0.1 }
    );
    fieldRefs.current.forEach((ref) => ref && observer.observe(ref));
    return () => observer.disconnect();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      // Mock prediction logic
      const credit = Number(form.creditScore) || 650;
      const dti = (Number(form.existingDebts) || 0) / Math.max(Number(form.monthlyIncome) || 1, 1);
      const loanRatio = (Number(form.loanAmount) || 0) / Math.max(Number(form.monthlyIncome) || 1, 1);
      let risk = 30 + (750 - credit) * 0.12 + dti * 15 + loanRatio * 2;
      if (form.employmentType === "Unemployed") risk += 25;
      if (form.employmentType === "Freelancer") risk += 10;
      risk = Math.max(5, Math.min(95, risk));
      const probability = Math.round(risk);
      onPredict(form, probability, probability > 50);
      setLoading(false);
    }, 1200);
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4">
      <div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="glass-card glass-card-hover rounded-2xl p-8 relative overflow-hidden transition-transform duration-150 ease-out"
        style={{ transformStyle: "preserve-3d" }}
      >
        {/* Specular highlight overlay */}
        <div className="specular absolute inset-0 pointer-events-none rounded-2xl" />

        <h2 className="text-2xl font-semibold text-foreground mb-6 text-center">
          Enter Loan Details
        </h2>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {FIELDS.map((field, i) => (
            <div
              key={field.key}
              ref={(el) => { fieldRefs.current[i] = el; }}
              className="field-reveal"
              style={{ transitionDelay: `${i * 80}ms` }}
            >
              <label className="block text-sm text-muted-foreground mb-1.5">{field.label}</label>
              {field.type === "select" ? (
                <select
                  value={form[field.key]}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  className="w-full rounded-lg border border-border bg-secondary px-3 py-2.5 text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                >
                  {field.options!.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <input
                  type="number"
                  placeholder={field.placeholder}
                  value={form[field.key]}
                  onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  className="w-full rounded-lg border border-border bg-secondary px-3 py-2.5 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                />
              )}
            </div>
          ))}

          <div
            ref={(el) => { fieldRefs.current[FIELDS.length] = el; }}
            className="field-reveal md:col-span-2 mt-2"
            style={{ transitionDelay: `${FIELDS.length * 80}ms` }}
          >
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold text-lg glow-border hover:opacity-90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <span className="inline-block w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Predict Risk"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PredictionForm;
