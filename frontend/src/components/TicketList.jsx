export default function TicketList({ tickets }) {
  return (
    <section className="card">
      <h2>Recent tickets</h2>
      {tickets.length === 0 ? (
        <p>No tickets returned.</p>
      ) : (
        <div className="ticket-list">
          {tickets.map((ticket) => (
            <article className="ticket" key={ticket.id}>
              <div>
                <strong>{ticket.subject}</strong>
                <small>
                  {ticket.id} · {ticket.status}
                </small>
              </div>
              <span className={ticket.breach_risk >= 0.5 ? "risk high" : "risk"}>
                {Math.round(ticket.breach_risk * 100)}% risk
              </span>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
