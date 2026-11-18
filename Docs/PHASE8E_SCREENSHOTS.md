# Phase 8E — Screenshot checklist

Take fresh screenshots directly from the deployed website at https://sla-guardian-ai.vercel.app. Use a non-sensitive demonstration account and synthetic ticket data.

| Suggested filename | What to capture | Important check |
| --- | --- | --- |
| `01-login.png` | Unfilled login form | No email/password exposed |
| `02-overview.png` | Overview metrics and primary navigation | No browser DevTools or private user data |
| `03-tickets.png` | Ticket table with priority, status, and SLA deadline | Synthetic demo tickets only |
| `04-prediction.png` | Successful prediction showing probability, band, and disclaimer | Research-only notice clearly visible |

Save the four files in `docs/screenshots/` and add these links to the main README after capture:

```markdown
![Login page](docs/screenshots/01-login.png)
![Ticket overview](docs/screenshots/02-overview.png)
![Organization-scoped tickets](docs/screenshots/03-tickets.png)
![SLA breach prediction](docs/screenshots/04-prediction.png)
```

For neat presentation: use browser zoom at 100%, desktop width around 1366–1440 pixels for overview/tickets/prediction, crop browser chrome, and avoid capturing source-code windows or debug errors. A separate mobile screenshot can be added if useful. Do not publish passwords, access tokens, Supabase API secrets, authorization headers, or real customer information.

**Status:** Screenshot checklist prepared; latest deployed screenshots must still be captured by the repository owner. Earlier conversation screenshots may reflect a prior UI revision and should not be mislabeled as current production captures.
