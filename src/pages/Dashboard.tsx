import { Link } from "react-router-dom";
import BarChart3D from "@/components/dashboard/BarChart3D";
import FloatingStatCards from "@/components/dashboard/FloatingStatCards";
import LiveFeedPanel from "@/components/dashboard/LiveFeedPanel";
import Starfield from "@/components/dashboard/Starfield";

const Dashboard = () => (
  <div className="relative min-h-screen">
    {/* Animated gradient mesh background */}
    <div className="gradient-mesh-bg" />
    <Starfield />

    <div className="relative z-10 max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 bounce-up bounce-up-1">
        <div>
          <h1 className="text-3xl font-bold text-foreground glow-text">Analytics Dashboard</h1>
          <p className="text-muted-foreground mt-1">Loan risk prediction insights</p>
        </div>
        <Link
          to="/"
          className="px-4 py-2 rounded-lg glass-card glass-card-hover text-sm text-foreground hover:text-primary transition-colors"
        >
          ← Predictor
        </Link>
      </div>

      {/* Floating stat cards — individually animated inside the component */}
      <FloatingStatCards />

      {/* Main content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mt-8">
        <div className="lg:col-span-3 bounce-up bounce-up-5">
          <BarChart3D />
        </div>
        <div className="lg:col-span-2 bounce-up bounce-up-6">
          <LiveFeedPanel />
        </div>
      </div>
    </div>
  </div>
);

export default Dashboard;

