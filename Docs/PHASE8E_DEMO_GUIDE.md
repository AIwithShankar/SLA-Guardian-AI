# SLA Guardian AI — Two-minute interview demo

## Before recording or presenting

- Open the [live website](https://sla-guardian-ai.vercel.app) and confirm the [backend health endpoint](https://sla-guardian-ai.onrender.com/health) responds; free Render hosting can sleep between requests.
- Use an authorized **non-sensitive demo account**. Do not reveal its password, JWT, API keys, or customer data.
- Ensure a fresh, eligible demo ticket has an assigned SLA policy and deadline in the future; expired tickets correctly disable predictions.
- Keep backup screenshots of a successful prediction because a cloud cold start can interrupt a timed demo.

## Spoken script (about two minutes)

**0:00–0:20 — Problem**

"Customer-support teams have deadlines for resolving tickets, but dashboards often show that a ticket breached its SLA only after the deadline. SLA Guardian AI is my research prototype for estimating which open tickets might be at risk before that happens."

**0:20–0:45 — Product**

"This is the live React dashboard. Users authenticate with Supabase. The ticket list is scoped to their organization, and managers can see priorities, statuses, and SLA deadlines. The design is intentionally simple so support managers can find the next action quickly."

**0:45–1:10 — Live prediction**

"I'll open an eligible ticket and request an SLA risk estimate. React sends the user's access token and ticket ID to FastAPI. The API verifies the token, checks the user's trusted role and organization, validates the assigned SLA, and loads the approved LightGBM artifact. The result shows a breach probability and risk level."

**1:10–1:35 — ML**

"The research model uses six features: ticket priority, category, ticket age, remaining SLA hours, creation hour, and weekday. It was trained in Colab with LightGBM and probability calibration. On the held-out research test set, ROC-AUC was about 0.783 and average precision about 0.636. At the 0.70 high-risk threshold, precision was around 72%, but recall only around 6.5%, which is an important limitation."

**1:35–1:55 — Engineering and security**

"I used Supabase PostgreSQL with row-level security for tenant isolation, FastAPI on Render, and React on Vercel. I checked the model's checksum and dependency versions before loading it. My tests included role restrictions and cross-organization access denial, and 41 backend automated tests passed."

**1:55–2:05 — Honest closing**

"This is a deployed research MVP, not a production-validated system. Predictions are advisory and not persisted. A next step would be prospective validation and better recall before real customer use."

## Non-technical explanation (30 seconds)

"Think of it as an early-warning dashboard for customer-support tickets. Every ticket has a deadline. Instead of waiting until that deadline is missed, a manager can ask the system how likely the ticket is to be late, then decide whether to pay closer attention. The score is an estimate, not a guarantee."

## Common interviewer questions

**Q: Why LightGBM instead of an LLM?**  
A: The prediction uses a small set of structured ticket features, making a gradient-boosted tabular model a better fit for this research problem. An LLM is not needed to compute the breach probability.

**Q: How do you prevent one company from seeing another company's tickets?**  
A: Supabase Row Level Security controls database access; the backend resolves the authenticated user's trusted organization and performs tenant-scoped lookups. A cross-tenant prediction attempt was denied during testing.

**Q: Can an Agent call the prediction API directly?**  
A: No. Hiding the button is only UX; the FastAPI service enforces role authorization. The test Agent received HTTP 403.

**Q: Why the research disclaimer?**  
A: The dataset and SLA labels are provisional, not validated on current production workloads. The high-risk threshold has low recall, and a probability score should not automatically drive interventions.

**Q: How is the model protected from accidental replacement?**  
A: The backend loads a versioned artifact from a trusted path, verifies its SHA-256 hash and declared dependency versions, and rejects mismatches.

**Q: What would you build next?**  
A: Prospective validation, organization-specific SLA configuration and adaptation, persisted prediction history, risk monitoring, more useful recall, and an operational alert workflow—but only after evidence supports them.

## Resume-ready project entry

**SLA Guardian AI | React, FastAPI, Supabase, LightGBM, Vercel, Render**  
- Built and deployed a research-stage support-ticket SLA breach prediction dashboard with Supabase Auth/RLS and FastAPI-based LightGBM inference.  
- Implemented tenant-scoped ticket access, Manager/Admin prediction authorization, and checksum-verified model loading; verified 41 backend automated tests.  
- Evaluated on a held-out research test set (ROC-AUC ~0.783, average precision ~0.636); documented low recall at the 0.70 high-risk threshold and non-production limitations.

Do not imply the model has reduced real-world breaches or been production-validated.
