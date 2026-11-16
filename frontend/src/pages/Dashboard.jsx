import HealthStatus from "../components/HealthStatus";
import { useHealth } from "../hooks/useHealth";

export default function Dashboard() {
  const { health, error } = useHealth();

  return (
    <main className="page">
      <header>
        <p className="eyebrow">SLA Guardian AI</p>
        <h1>Project foundation</h1>
        <p className="subtitle">
          React, Vite, Tailwind CSS, and FastAPI are connected.
        </p>
      </header>
      <HealthStatus health={health} error={error} />
    </main>
  );
}
