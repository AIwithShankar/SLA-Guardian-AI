import { useEffect, useState } from "react";
import HealthStatus from "../components/HealthStatus";
import TicketList from "../components/TicketList";
import { getHealth, getTickets } from "../services/api";

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getHealth(), getTickets()])
      .then(([healthResponse, ticketResponse]) => {
        setHealth(healthResponse);
        setTickets(ticketResponse.items);
      })
      .catch((requestError) => setError(requestError.message));
  }, []);

  return (
    <main className="page">
      <header>
        <p className="eyebrow">SLA Guardian AI</p>
        <h1>Support operations overview</h1>
        <p className="subtitle">
          Scaffolding dashboard connected to the FastAPI mock API.
        </p>
      </header>
      <HealthStatus health={health} error={error} />
      <TicketList tickets={tickets} />
    </main>
  );
}
