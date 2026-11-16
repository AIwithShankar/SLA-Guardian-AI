SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 1
PRODUCT ARCHITECTURE / PHASE 1
SLA Guardian AI
MVP Product Requirements Document
Product: B2B customer-support resolution-SLA breach predictor
Stack: React / Vite / Tailwind / Recharts; FastAPI; managed Supabase PostgreSQL; scikit-learn / LightGBM /
SHAP; Google Colab
Execution constraint: Solo developer using a 4GB RAM Intel Celeron machine; no Docker, local database,
local LLM, or heavy local training.
STATUS
SCOPE
Document type
Proposed requirements and architecture; not implemented software
Includes
Roles, workflows, SLA rules, data contracts, diagrams, APIs, security, metrics, tests, backlog
Out of scope
Application code, trained model, measured performance, dataset claims, external integrations
Guiding principle: Separate contractual SLA computation, machine learning inference, and alert decisions.
Never fabricate historical data, model scores, metrics, deployed integrations, or passing tests.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 2
1. Product vision
SLA Guardian AI helps customer-support teams identify tickets likely to miss contractual resolution deadlines
before they become overdue. Agents monitor ticket deadlines; managers see risk scores, contributing
factors, and in-app alerts; administrators manage imports and SLA configuration.
Core value: Support proactive ticket prioritization using predictive intelligence rather than reacting only
after missed deadlines. The product is decision support, not automatic remediation.
Conventional ticket tracker
SLA Guardian AI
Shows current status
Estimates future breach risk
Displays deadlines
Computes remaining contractual SLA time
Highlights already-overdue work
Highlights eligible tickets at future risk
Manual prioritization
Interpretable risk factors
Historical reports
Predictive monitoring and manager interventions
2. Technology and engineering scope
 Component
Technology
Responsibility
Frontend
React + Vite + Tailwind CSS + Recharts
UI, tables, charts, forms
Backend
FastAPI + Python + Pydantic
Business logic, validation, API, authorization
Persistence + identity
Managed Supabase PostgreSQL + Auth
Ticket, tenant, user, policy and alert records
ML inference
scikit-learn or LightGBM + SHAP
Probability, risk band, explanation
Training
Google Colab
Preprocessing, evaluation, model export
Notifications
FastAPI rules + PostgreSQL
Deduplicated in-app manager alerts
Architecture choice: A modular monolith: FastAPI provides one deployable backend with small modules for
SLA calculation, feature construction, versioned inference and alerts. Do not add Docker, Redis, Celery,
Kubernetes, external notification providers, or local training to the MVP.
3. Users, roles and access
 • Agent: monitor assigned tickets, see SLA status and prediction/explanation, update permitted ticket state.
 • Manager/team lead: see organizational tickets, investigate risk, review and acknowledge manager alerts,
 view team analytics.
• Admin: manage organization members, imports, SLA policy settings, all tickets and analytics.
 
Capability
Agent
Manager
Admin
Assigned tickets
Yes
Yes
Yes
All organization tickets
No
Yes
Yes


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 3
Capability
Agent
Manager
Admin
Update authorized ticket state
Assigned
Yes
Yes
View prediction
Assigned
Yes
Yes
View analytics
Own
Team/all
All
Acknowledge alerts
No
Yes
Yes
Import CSV
No
No
Yes
Manage SLA policies / roles
No
No
Yes
Tenant boundary: access must always be restricted by authenticated organization_id. For the MVP, manager
visibility is organization-wide if there is no team hierarchy.
4. Core workflows
 • Import: Admin uploads CSV; server validates, normalizes and persists records while reporting row errors.
 • Assessment: Eligible open tickets are mapped to approved point-in-time ML features and scored by a
 specific model version.
• Agent review: Tickets page shows remaining SLA time, eligible breach-risk probability and explanation
 where available.
• Manager action: A high-risk eligible prediction triggers a deduplicated in-app alert for the manager.
 • Monitoring: Dashboard aggregates ticket states, true SLA breaches, predicted high-risk tickets and alerts.
 
5. User stories and acceptance criteria
 ID
Story
Accept when
US-01
Admin uploads CSV
Valid records imported; invalid rows explained
US-02
Agent sees assigned tickets
Authorized, paginated records only
US-03
Agent sees deadline
Calculated from assigned SLA policy
US-04
Manager sees high-risk tickets
Eligible tickets show model score and band
US-05
Manager understands prediction
Available feature contributions displayed
US-06
Manager receives alert
Single active alert per ticket/rule
US-07
Admin monitors analytics
Aggregate counts match authorized records
US-08
Reviewer uses demo
Clearly labeled synthetic data, no fabricated ML claims
6. MVP feature boundary
Required: CSV import; ticket list and details; SLA deadline and time remaining; breach-risk prediction; risk
band; explanation; in-app manager alert; basic analytics; simple synthetic demo mode; role-based access.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 4
Excluded: Zendesk/Freshdesk/Salesforce integration; Slack, email or SMS alerts; chatbot; sentiment
analysis; automatic assignment/remediation; retraining pipeline; business-hour or holiday calendar;
reopened-ticket logic; mobile app; multi-region setup.
Definition of demo completion: A reviewer can load tickets, inspect correctly computed deadlines, view
legitimately generated predictions if an approved model exists, see explanations, acknowledge alerts and
examine analytics. Synthetic data validates a workflow, not real-world ML accuracy.
7. System architecture
Layer 1: deterministic SLA: Create an exact deadline/status from timestamps and policy; no ML. Layer 2:
prediction: Estimate future breach probability for eligible currently unbreached tickets, report model
version and explanations. Layer 3: alert rules: Independently apply thresholds, eligibility and deduplication
to stored risk assessments.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 5
8. Request sequence: ticket inspection and risk
refresh
The ticket page initially displays the latest stored prediction. The system does not infer afresh on each page
refresh. The explicit predict action authorizes the user, fetches current features, calculates and stores a
versioned prediction, then evaluates alerts.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 6
9. SLA policy specification
 Policy dimension
MVP assumption
Objective
Resolution SLA only
Clock
24 hours / 7 days
Timestamp standard
Persist UTC timestamps
Start
created_at
Targets
Admin configurable per priority
Pause / business hours
Not supported
Resolution
resolved_at stops clock
Reopened tickets
Not supported
Policy changes
Existing ticket retains assigned deadline
Policy selection
organization + priority
Illustrative policy defaults - not customer-validated
Priority
Target
Critical
4 hours
High
8 hours
Medium
24 hours
Low
72 hours
Formula: deadline = created_at + resolution target. For open tickets: remaining time = deadline - current
UTC time. A ticket is breached if still unresolved after its deadline, or if its resolution timestamp exceeds that
deadline. An already overdue open ticket is no longer eligible for a prediction of a future breach.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 7
10. Explicit data contract
10A. CSV import
CSV field
Type
Required
Meaning
external_ticket_id
string
Yes
Organization-scoped identifier
created_at
ISO-8601 datetime
Yes
Clock start
priority
enum
Yes
critical / high / medium / low
status
enum
Yes
open / in_progress / resolved
assigned_agent_id
string
No
Existing agent mapping
category
string
No
Support issue category
resolved_at
ISO-8601 datetime
If resolved
Timestamp of resolution
last_updated_at
ISO-8601 datetime
No
Additional historical timestamp
Use (organization_id, external_ticket_id) for deterministic upserts; reject duplicate IDs within one uploaded
CSV. Unknown agents remain unassigned until mapped. organization_id is derived from authenticated
context; never trust a CSV-provided tenant ID.
external_ticket_id,created_at,priority,status,assigned_agent_id,category,resolved_at
10B. Candidate ML feature schema
Feature
Type
Leakage guard
priority
categorical
Value known at prediction time
category
categorical
Value known at prediction time
ticket_age_hours
float
Compute using snapshot time
remaining_sla_hours
float
Use deterministic SLA service at snapshot
created_hour
integer
Creation-time value
created_weekday
integer
Creation-time value
agent_open_ticket_count
integer
Only with genuine historical snapshots
previous_agent_breach_rate
float
Only events completed before snapshot
The last two features are optional and must not be derived retroactively using today's workload. Historical
ticket outcomes alone may not include the intermediate snapshots needed for faithful training.
10C. Target and eligibility
For an eligible open, unbreached ticket at prediction time t: y=1 if it eventually misses the resolution
deadline; y=0 if it resolves within the deadline. Train on completed outcomes. Do not label still-unresolved
tickets with unknown outcomes as negatives; exclude tickets already breached at time t.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 8
Data dependency: Current ticket records permit the UI and deterministic deadline calculation, but they do
not automatically constitute a legitimate supervised training dataset.
10D. Prediction response contract (illustrative)
{
  "ticket_id": "example-ticket-id",
  "model_version": "v1",
  "prediction_timestamp": "2026-11-14T07:30:00Z",
  "sla_deadline": "2026-11-15T07:30:00Z",
  "breach_probability": 0.82,
  "risk_band": "high",
  "top_factors": [{"feature": "remaining_sla_hours", "contribution": 0.21}],
  "prediction_status": "available"
}
The JSON is a schema illustration, not an actual prediction. A contribution is a model-explanation quantity, not
automatically a probability increase. For unavailable model/features, return an explicit prediction_status and no
synthetic probability.
11. ML strategy and explainability
Baseline: Logistic Regression with scikit-learn preprocessing. Candidate: LightGBM, evaluated under
identical time-aware validation. Train in Google Colab and run CPU inference locally or on a lightweight
hosted backend.
 • Audit ticket history and reconstruct valid point-in-time features.
 • Split data chronologically; guard against the same ticket leaking into different evaluation partitions.
 • Fit preprocessing using training data only.
 • Evaluate PR-AUC, recall, precision, calibration and alert lead time on suitable holdouts.
 • Calibrate probability estimates if validation justifies calibration.
 • Export the trusted model with preprocessing, feature schema, model/dependency versions, evaluation
 metadata and checksum.
• Load one approved artifact in FastAPI and persist the top explanation contributions per prediction.
 
Probability
Provisional UI band
Below 0.30
Low
0.30 to below 0.70
Medium
0.70 or more
High
These thresholds are provisional design values, not learned or optimized cutoffs. SHAP explanations describe
model contribution, not proof of causal drivers. Verify model artifacts and package compatibility; do not load
arbitrary user-uploaded pickle/joblib files.
12. Alert decision rules
Create a manager alert only when (a) ticket is open and not already breached, (b) model is approved and
prediction is available, (c) probability reaches the alert threshold, initially 70%, and (d) no equivalent active
alert exists.
Alert lifecycle: active -> acknowledged -> resolved. Ticket closure resolves active/acknowledged alerts. In
MVP, acknowledging does not automatically re-open an alert at each subsequent prediction. Manager sees
in-app notifications; no external delivery is implied.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 9
13. Database table shortlist
 Table
Minimum relevant fields
organizations
id, name, created_at
profiles
user_id, organization_id, role, display_name
sla_policies
id, organization_id, priority, target_minutes, version
tickets
id, organization_id, external_ticket_id, assigned_agent_id, priority, status, category, created_at,
resolved_at, sla_policy_id, sla_deadline
model_versions
id, version, artifact_checksum, feature_schema_version, status, activated_at
predictions
id, ticket_id, model_version_id, probability, risk_band, explanation_json, predicted_at
alerts
id, ticket_id, prediction_id, rule_type, state, acknowledged_by, created_at
import_jobs
id, organization_id, uploaded_by, row_count, imported_count, error_summary, created_at
Enforce organization-scoped uniqueness for external ticket IDs, foreign keys, filter indexes and uniqueness of
equivalent active alerts. Keep model binaries outside PostgreSQL; persist only artifact metadata. Verify
identity in FastAPI and enforce tenant/role access on every protected database operation. Keep all Supabase
secret/server keys off the frontend.
14. REST API contract
 Verb
Endpoint
Access
GET
/health
Public
GET
/api/v1/me
Signed in
POST
/api/v1/imports/tickets
Admin
GET
/api/v1/imports/{id}
Admin
GET
/api/v1/tickets
Authorized roles
GET
/api/v1/tickets/{id}
Authorized user
PATCH
/api/v1/tickets/{id}
Authorized user
POST
/api/v1/tickets/{id}/predict
Manager / Admin
GET
/api/v1/tickets/{id}/predictions
Authorized user
GET
/api/v1/alerts
Manager / Admin
PATCH
/api/v1/alerts/{id}/acknowledge
Manager / Admin
GET
/api/v1/analytics/summary
Signed in
GET
/api/v1/sla-policies
Signed in
PUT
/api/v1/sla-policies/{id}
Admin


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 10
All protected endpoints require identity verification, role checks, organization checks, schema validation and
consistent error responses. Automated rescoring, if added, should be a protected backend operation rather
than an unrestricted public route. Apply size/row limits to uploaded CSVs.
15. Frontend pages
 Page
MVP content
Dashboard
Ticket counts, high-risk tickets, breached counts, risk distribution; Recharts
Tickets
Paginated search/filter table plus ticket details
Alerts
Manager alert inbox and acknowledgment
Imports
Admin upload/validation summary and errors
SLA settings
Admin priority-to-resolution-target policy
Demo mode
Explicitly synthetic fixture workflow
Login / account
Supabase-authenticated access and role-aware navigation
Keep predicted future breaches visually distinct from confirmed contractual breaches. Display empty states,
loading states and an explicit model-unavailable state.
16. Nonfunctional requirements
 Domain
Proposed acceptance target
Latency
Ordinary paginated API reads under 1 sec, network dependent; benchmark in deployment
Inference
Target under 500 ms/ticket after model warmup, subject to measurement
CSV size
Initial 5MB or 5,000 row ceiling
Memory
Only lightweight Vite and FastAPI development locally
Reliability
Model inference failure must not hide ticket/deadline data
Security
HTTPS in deployment; validated JWT; RBAC; tenant scope
Maintainability
Typed schemas, small Python modules, simple React components
Accessibility
Keyboard support, contrast, textual risk labels
Observability
Structured error/inference/import logs, no sensitive payloads
Reproducibility
Pinned dependencies, versioned features/preprocessing
These targets are proposals, not achieved benchmark results.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 11
17. Privacy and security risk register
 Risk
Mitigation
PII exposure through CSV
Exclude names, emails and ticket bodies from MVP schema
Cross-tenant leakage
Scope every query/write by authenticated organization
Secret disclosure
Server-only environment variables and .gitignore
CSV injection
Treat input as data; sanitize exported spreadsheet cells
Resource exhaustion
Enforce size/row and parser limits
Feature/label leakage
Use point-in-time features and chronological evaluation
Misleading explanations
Do not frame SHAP attributions as causal
Unsafe model artifact
Trust/checksum verify model files
Sensitive operational logs
Avoid raw CSV, credentials, and auth tokens
18. Success and validation metrics
 Measurement
How to evaluate
CSV correctness
All valid fixture rows imported; invalid rows reported
SLA correctness
Defined boundary conditions pass automated tests
Access isolation
Unauthorized and cross-tenant test requests rejected
Prediction coverage
Share of eligible tickets with valid saved assessments
PR-AUC
Held-out historical data, after class prevalence audited
Recall / precision at alert threshold
Held-out outcomes and false-alert burden
Probability calibration
Predicted vs observed breach rate in bins
Alert lead time
Time from first qualifying alert to deadline
Product effectiveness
Prospective deployment study; not assumed from demo
Do not claim a quantified breach reduction without an appropriate evaluation in a real deployment.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 12
19. Test plan - planned, not executed
 Test
Scenario
Expected
SLA-01
10:00 UTC creation + 4-hour policy
14:00 UTC deadline
SLA-02
Open ticket reaches deadline
Confirmed breach, no future-risk scoring
SLA-03
Resolved before deadline
Not breached
CSV-01
Required column missing
Validation error for row/import
CSV-02
Duplicate external ticket ID
Deterministic documented handling
AUTH-01
Agent accesses unassigned ticket
403 or non-disclosing 404
AUTH-02
User accesses other tenant
No private data revealed
ML-01
Approved model + valid features
Probability in [0,1]
ML-02
Model not available
Explicit unavailable status
ML-03
Predict already-breached ticket
Ineligible request rejected
ALERT-01
Eligible high-risk ticket
Single active alert
ALERT-02
Repeat assessment
No duplicate active alert
ALERT-03
Acknowledgment
State becomes acknowledged
UI-01
No tickets
Useful empty state
UI-02
No model
Still show deterministic deadline
Use pytest for backend units and API tests; add a small set of React component tests when UI components
exist. Perform database authorization/integration tests in a dedicated Supabase test project. None of these
tests have been executed for this document.
20. Prioritized backlog - 24 small issues
P0: Foundation
Issue
Task
01
Initialize monorepo and environment templates
02
Create FastAPI /health and tests
03
Create React/Vite/Tailwind app shell
04
Configure Supabase project and schema
05
Implement authentication and RBAC


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 13
P1: Functional core
Issue
Task
06
Implement SLA calculator and boundary tests
07
Create CSV schema validation
08
Implement bounded CSV import
09
Create paginated tickets API
10
Build ticket list/detail views
11
Create admin SLA policy settings
P2: Predictive ML
Issue
Task
12
Audit historical labels and snapshots
13
Build Colab preprocessing notebook
14
Train and evaluate baseline model
15
Evaluate LightGBM and calibration
16
Export trusted versioned artifact
17
Implement FastAPI inference service
18
Store explanation and risk bands
P3: Alerts and delivery
Issue
Task
19
Implement manager alert rules
20
Add deduplication and acknowledgment
21
Build manager alert inbox
22
Create analytics API and charts
23
Create safe synthetic demo fixtures
24
Perform security/integration/deployment tests
ML readiness gate: Issues 13-18 require defensible labeled data. If unavailable, complete deterministic
workflows and expose a clear model_unavailable state. The synthetic demo may use illustrative risk data
only if prominently labeled simulated.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 14
21. Proposed repository structure
sla-guardian-ai/
  frontend/
    src/{api,components,pages,hooks}/
    src/App.jsx
    package.json
  backend/
    app/{api,schemas,services,repositories}/
    app/services/{sla.py,predictor.py,alerts.py}
    app/main.py
    tests/
    requirements.txt
  ml/{notebooks,artifacts}/
  supabase/migrations/
  docs/{PRD.md,architecture.md,data-contract.md}
  .env.example
  .gitignore
  README.md
Directory structure is proposed only. No source files or configured services are claimed to exist.
22. Phase 1 execution, commands and commit
Plan: Approve the requirements, save the architecture diagrams and data contract, check that the
documents have content, then commit. Code, model training, database migration and dependency
installation are explicitly deferred.
Files to create: docs/PRD.md, docs/architecture.md and docs/data-contract.md.
Windows PowerShell - create structure
mkdir sla-guardian-ai
cd sla-guardian-ai
git init
New-Item -ItemType Directory -Path docs
New-Item -ItemType File -Path docs/PRD.md
New-Item -ItemType File -Path docs/architecture.md
New-Item -ItemType File -Path docs/data-contract.md
Paste the approved specifications into these Markdown files, then run:
Get-ChildItem docs
Get-Content docs/PRD.md -TotalCount 10
Get-Content docs/architecture.md -TotalCount 10
Get-Content docs/data-contract.md -TotalCount 10
Expected: Three Markdown files are present and their first lines display actual document content. Empty
placeholder files do not satisfy acceptance criteria.
Git commit
git add docs/
git commit -m "docs: define SLA Guardian AI MVP requirements and architecture"
git status
Expected: Successful documentation commit and clean working tree, assuming Git is configured. No
automated tests are claimed to have run.


SLA GUARDIAN AI
MVP PRODUCT REQUIREMENTS DOCUMENT
Version 1.0  |  14 November 2026  |  Phase 1
Page 15
23. Risks, exclusions and next phase
 Dependency / risk
MVP action
No historical labels
Build ticket workflow first; do not invent ML quality
No point-in-time features
Reduce feature set; do not use current values as history
Complex contract calendar
Explicitly 24/7 SLA only
4GB RAM laptop
Use Colab and managed cloud services
Slow model startup
Load one approved version at backend startup
Tenant-specific differences
Begin with one validated model, revisit later
Hosting cost
Verify actual free-tier quotas before deployment
Import idempotency
Organization-scoped IDs and documented conflict behavior
Decisions required before training: Actual historical ticket columns, ticket-resolution outcomes,
timestamp quality, access to prediction-time feature snapshots, and SLA policy assumptions.
Next recommended build phase: Project Foundation: Git setup, Vite/React/Tailwind shell, minimal FastAPI
health endpoint, environment variable templates and one smoke test. Do not combine this with the
database, CSV import or ML in a single change.
Reference documentation
 • FastAPI file uploads: https://fastapi.tiangolo.com/tutorial/request-files/
 • Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
 • scikit-learn model persistence: https://scikit-learn.org/stable/model_persistence.html
 Document status: Phase 1 specification drafted; implementation, datasets, test results and deployed
integrations have not been verified or claimed.
