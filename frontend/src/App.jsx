import { useCallback, useEffect, useMemo, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, XAxis } from "recharts";
import { supabase } from "./lib/supabase";
import { predictTicket } from "./lib/api";

const OPEN_STATUSES = new Set(["open", "pending", "in_progress", "in-progress"]);
const isActive = (ticket) => OPEN_STATUSES.has(String(ticket.status || "").toLowerCase());
const datetime = (value) => value ? new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "Not assigned";
const shortId = (ticket) => ticket.external_ticket_id || ticket.id?.slice(0, 8) || "—";
const titleCase = (value) => String(value || "unknown").replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
const errorText = (error) => error?.message || "Something went wrong.";
const percent = (number) => `${(number * 100).toFixed(1)}%`;

function Brand() {
  return <div className="brand"><div className="brand-icon" aria-hidden="true">S</div><span>SLA Guardian</span></div>;
}
function Spinner({ small = false }) { return <span className={small ? "spinner spinner-sm" : "spinner"} aria-hidden="true" />; }

function Login({ onAuthenticated }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
      if (error) throw error;
      setPassword("");
      onAuthenticated(data.session);
    } catch (err) { setError(errorText(err)); }
    finally { setBusy(false); }
  }
  return <div className="login-wrap">
    <div className="login-top"><Brand /></div>
    <main className="login-card">
      <span className="eyebrow">SUPPORT OPERATIONS</span>
      <h1>Welcome back.</h1>
      <p className="muted">Sign in to review your team's support tickets and SLA deadlines.</p>
      <form onSubmit={submit} className="login-form">
        <label htmlFor="email">Work email</label>
        <input id="email" type="email" required autoComplete="username" placeholder="you@company.com" value={email} onChange={e => setEmail(e.target.value)} />
        <label htmlFor="password">Password</label>
        <input id="password" type="password" required autoComplete="current-password" placeholder="Enter your password" value={password} onChange={e => setPassword(e.target.value)} />
        {error && <p className="error" role="alert">{error}</p>}
        <button className="button button-primary login-submit" type="submit" disabled={busy}>{busy ? <><Spinner small /> Signing in...</> : "Sign in"}</button>
      </form>
      <p className="login-foot">Access is limited to authorized support team members.</p>
    </main>
    <div className="login-bottom">SLA Guardian · Research prototype</div>
  </div>;
}

function Badge({ value, type = "status" }) {
  const normalized = String(value || "unknown").toLowerCase();
  const className = type === "priority" ? `pill priority-${normalized}` : type === "risk" ? `pill risk-${normalized}` : `pill status-${normalized}`;
  return <span className={className}>{titleCase(value)}</span>;
}

function PredictionDetails({ prediction, ticketReference }) {
  if (!prediction) return <div className="empty-detail"><div className="detail-symbol">↗</div><h3>No prediction selected</h3><p>Choose an eligible ticket, then select <strong>Predict risk</strong> to see its estimated SLA breach risk.</p></div>;
  const value = prediction.breach_probability;
  const isProbability = typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= 1;
  const chartData = [{ name: "Breach risk", risk: isProbability ? Math.round(value * 1000) / 10 : 0, rest: isProbability ? 100 - Math.round(value * 1000) / 10 : 100 }];
  const riskColor = { high: "#b54735", medium: "#b07824", low: "#28734d" }[String(prediction.risk_band || "").toLowerCase()] || "#536479";
  return <div className="prediction-detail">
    <div className="detail-kicker">LATEST RESULT <span className="dot" /> <span>Current session only</span></div>
    <p className="detail-id">Ticket {ticketReference || prediction.ticket_id?.slice(0, 8)}</p>
    <div className="risk-display"><span className="risk-number">{isProbability ? percent(value) : "Unavailable"}</span>{prediction.risk_band && <Badge value={prediction.risk_band} type="risk" />}</div>
    <p className="muted detail-sub">Estimated probability of missing the resolution SLA.</p>
    {isProbability && <div className="risk-chart" aria-label={`Predicted breach probability ${percent(value)}`} role="img"><ResponsiveContainer width="100%" height={34}><BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 0, bottom: 0, left: 0 }} barSize={12}><XAxis type="number" domain={[0, 100]} hide /><Bar dataKey="risk" stackId="a" fill={riskColor} radius={[5, 0, 0, 5]} isAnimationActive={false} /><Bar dataKey="rest" stackId="a" fill="#e8edf3" radius={[0, 5, 5, 0]} isAnimationActive={false} /></BarChart></ResponsiveContainer><div className="chart-labels"><span>0%</span><span>100%</span></div></div>}
    <dl className="prediction-meta"><div><dt>Deadline</dt><dd>{datetime(prediction.sla_deadline)}</dd></div><div><dt>SLA breached at prediction</dt><dd>{prediction.sla_breached ? "Yes" : "No"}</dd></div><div><dt>Model</dt><dd>{prediction.model_version || "Unknown"}</dd></div><div><dt>Prediction status</dt><dd>{titleCase(prediction.prediction_status)}</dd></div></dl>
    <p className="research-note">Research-only estimate. This is not a guarantee of breach and should not be used as the sole basis for operational decisions.</p>
  </div>;
}

function Dashboard({ session, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [section, setSection] = useState("overview");
  const [prediction, setPrediction] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedReference, setSelectedReference] = useState(null);
  const [predicting, setPredicting] = useState(null);

  const loadData = useCallback(async (quiet = false) => {
    if (quiet) setRefreshing(true); else setLoading(true);
    setError("");
    try {
      const { data: profiles, error: profileError } = await supabase.from("profiles")
        .select("user_id,organization_id,role,display_name")
        .eq("user_id", session.user.id).limit(1);
      if (profileError) throw profileError;
      const found = profiles?.[0];
      if (!found?.organization_id || !["agent", "manager", "admin"].includes(found.role)) {
        throw new Error("Your account has no valid support-team profile. Contact your administrator.");
      }
      setProfile(found);
      // The explicit organization filter is useful UX; database RLS is the actual security boundary.
      const { data: rows, error: ticketsError } = await supabase.from("tickets")
        .select("id,external_ticket_id,organization_id,priority,category,status,created_at,sla_deadline,sla_policy_id")
        .eq("organization_id", found.organization_id)
        .order("created_at", { ascending: false }).limit(100);
      if (ticketsError) throw ticketsError;
      setTickets(rows || []);
    } catch (err) { setError(errorText(err)); }
    finally { setLoading(false); setRefreshing(false); }
  }, [session.user.id]);

  useEffect(() => { loadData(); }, [loadData]);
  const canPredict = ["admin", "manager"].includes(profile?.role);
  const activeCount = tickets.filter(isActive).length;
  const overdueCount = tickets.filter(t => isActive(t) && t.sla_deadline && new Date(t.sla_deadline) < new Date()).length;
  const filtered = useMemo(() => tickets.filter(t => {
    if (filter === "open" && !isActive(t)) return false;
    if (filter === "overdue" && !(isActive(t) && t.sla_deadline && new Date(t.sla_deadline) < new Date())) return false;
    const query = search.trim().toLowerCase();
    return !query || [shortId(t), t.category, t.priority, t.status].some(v => String(v || "").toLowerCase().includes(query));
  }), [tickets, filter, search]);

  async function handlePredict(ticket) {
    if (!canPredict) return;
    setSelectedId(ticket.id); setSelectedReference(shortId(ticket)); setPredicting(ticket.id); setError("");
    try { const result = await predictTicket(ticket.id); setPrediction(result); setSection("predictions"); }
    catch (err) { setError(`Ticket ${shortId(ticket)}: ${errorText(err)}`); }
    finally { setPredicting(null); }
  }
  async function logout() {
    const { error } = await supabase.auth.signOut();
    if (error) setError(errorText(error)); else onLogout();
  }

  return <div className="shell">
    <aside className="sidebar">
      <Brand />
      <div className="sidebar-group-label">WORKSPACE</div>
      <nav aria-label="Main navigation">
        {[["overview", "Overview"], ["tickets", "Tickets"], ["predictions", "Predictions"]].map(([key, label]) => <button key={key} type="button" className={`nav-item ${section === key ? "active" : ""}`} onClick={() => setSection(key)}>{label}</button>)}
      </nav>
      <div className="sidebar-bottom"><span className="avatar">{(profile?.display_name || session.user.email || "U").charAt(0).toUpperCase()}</span><div className="sidebar-user"><strong>{profile?.display_name || "Team member"}</strong><span>{profile ? titleCase(profile.role) : "Loading role"}</span></div><button type="button" onClick={logout} className="signout-button" title="Sign out">Sign out</button></div>
    </aside>
    <main className="content">
      <div className="topbar"><span>Support operations</span><span className="topbar-email">{session.user.email}</span></div>
      <div className="page-content">
        <div className="page-header"><div><p className="eyebrow">WORKSPACE</p><h1>{section === "overview" ? "Overview" : section === "tickets" ? "Tickets" : "Predictions"}</h1><p className="muted">{section === "overview" ? "A clear view of your team's support workload." : section === "tickets" ? "Review ticket status and upcoming SLA deadlines." : "Research-only SLA breach estimates for your tickets."}</p></div><button type="button" className="button button-secondary" disabled={refreshing || loading} onClick={() => loadData(true)}>{refreshing ? "Refreshing..." : "Refresh tickets"}</button></div>
        {error && <div className="error-banner" role="alert"><span>{error}</span><button type="button" onClick={() => setError("")}>Dismiss</button></div>}
        {loading ? <div className="loading-block"><Spinner /> Loading your workspace...</div> : <>
          {section === "overview" && <><div className="stats"><div className="stat"><span>Tickets in view</span><strong>{tickets.length}</strong><small>Up to 100 most recent visible tickets</small></div><div className="stat"><span>Open tickets</span><strong>{activeCount}</strong><small>Within the current ticket view</small></div><div className="stat"><span>Past SLA deadline</span><strong>{overdueCount}</strong><small>Open tickets with an expired deadline</small></div></div><div className="section-intro"><h2>Recent tickets</h2><button className="text-button" onClick={() => setSection("tickets")}>View all tickets →</button></div><TicketTable rows={tickets.slice(0, 6)} canPredict={canPredict} predicting={predicting} onPredict={handlePredict} /></>}
          {section === "tickets" && <><div className="table-toolbar"><input type="search" aria-label="Search tickets" placeholder="Search tickets" value={search} onChange={e => setSearch(e.target.value)} /><select aria-label="Filter tickets" value={filter} onChange={e => setFilter(e.target.value)}><option value="all">All tickets</option><option value="open">Open tickets</option><option value="overdue">Past deadline</option></select></div><TicketTable rows={filtered} canPredict={canPredict} predicting={predicting} onPredict={handlePredict} /><p className="table-hint">Showing {filtered.length} of {tickets.length} recently loaded tickets. Your Supabase access policies determine which tickets you can see.</p></>}
          {section === "predictions" && <div className="prediction-layout">
            <div className="panel prediction-panel">
              <div className="prediction-panel-header"><div><h2>Prediction details</h2><p className="muted panel-intro">{selectedReference ? `Selected ticket: ${selectedReference}` : "Select a ticket from the Tickets page."}</p></div><button type="button" className="button button-secondary" onClick={() => setSection("tickets")}>Browse tickets</button></div>
              <PredictionDetails prediction={prediction} ticketReference={selectedReference} />
            </div>
            <section className="prediction-about" aria-labelledby="prediction-about-heading"><h2 id="prediction-about-heading">About this prediction</h2><p>Estimated using the ticket's assigned SLA deadline and a research LightGBM model. Only managers and admins can request predictions. Results are kept in this browser session and are not saved to the database.</p></section>
          </div>}
        </>}
        <footer className="footer">SLA Guardian · Research prototype · Predictions are advisory only</footer>
      </div>
    </main>
  </div>;
}

function TicketTable({ rows, canPredict, predicting, onPredict }) {
  return <div className="table-card"><div className="table-scroll"><table><thead><tr><th>Ticket</th><th>Category</th><th>Priority</th><th>Status</th><th>SLA deadline</th><th className="action-col">Action</th></tr></thead><tbody>{rows.map(ticket => {
    const overdue = isActive(ticket) && ticket.sla_deadline && new Date(ticket.sla_deadline) < new Date();
    const eligible = canPredict && isActive(ticket) && ticket.sla_policy_id && ticket.sla_deadline && !overdue;
    return <tr key={ticket.id}><td className="ticket-code" title={ticket.id}>{shortId(ticket)}</td><td>{ticket.category || "—"}</td><td><Badge type="priority" value={ticket.priority} /></td><td><Badge value={ticket.status} /></td><td><span className={overdue ? "deadline-overdue" : ""}>{datetime(ticket.sla_deadline)}</span>{overdue && <span className="deadline-caption">Past deadline</span>}</td><td className="action-col"><button type="button" className="button button-table" onClick={() => onPredict(ticket)} disabled={!eligible || Boolean(predicting)} title={!canPredict ? "Manager or admin access required" : !eligible ? "Ticket must be open with an active assigned SLA" : "Request research-only prediction"}>{predicting === ticket.id ? "Predicting..." : "Predict risk"}</button></td></tr>;
  })}</tbody></table></div>{rows.length === 0 && <div className="empty-table">No tickets match this view.</div>}</div>;
}

export default function App() {
  const [session, setSession] = useState(null);
  const [checking, setChecking] = useState(true);
  useEffect(() => {
    let active = true;
    supabase.auth.getSession().then(({ data }) => { if (active) { setSession(data?.session || null); setChecking(false); } }).catch(() => { if (active) setChecking(false); });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, nextSession) => { if (active) { setSession(nextSession); setChecking(false); } });
    return () => { active = false; subscription.unsubscribe(); };
  }, []);
  if (checking) return <div className="boot"><Spinner /> Loading SLA Guardian...</div>;
  if (!session) return <Login onAuthenticated={setSession} />;
  return <Dashboard key={session.user.id} session={session} onLogout={() => setSession(null)} />;
}
