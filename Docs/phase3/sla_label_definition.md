# Phase 3 SLA label definition

> **Provisional research assumption only.** This is not a contractual SLA
> definition and has not been validated against customer policy or production
> timestamps.

## Provisional SLA targets

The notebook and manifest use an illustrative **24/7 elapsed-time policy**:

| Priority | Provisional resolution target |
|---|---:|
| `1 - Critical` | 4 hours |
| `2 - High` | 8 hours |
| `3 - Moderate` | 24 hours |
| `4 - Low` | 72 hours |

The targets are assumptions for research. They do not account for business
hours, holidays, pauses, customer waiting time, calendars, or tenant-specific
contracts.

## Label construction

For an eligible incident:

```text
deadline = opened_at + provisional_sla_hours(priority)
y_breach = 1 if resolved_at > deadline
y_breach = 0 otherwise
```

The notebook uses `opened_at` for the deadline, `resolved_at` for the observed
outcome, and the earliest selected event's `snapshot_at` for prediction time.
Eligible snapshots must be before the deadline and have a resolution after the
snapshot.

## Eligibility and cohort rules

The revised provisional audit requires:

- no observed reopen (`reopen_count == 0`);
- final state in `Resolved` or `Closed`;
- first state in `New` or `Active`;
- valid timestamps;
- `opened_at <= snapshot_at < deadline`;
- `resolved_at > snapshot_at`;
- a safe initial observation when earliest timestamps are tied.

The final safe feature cohort contains **22,320 incidents**, with **11,514
non-breaches** and **10,806 breaches** in the notebook's exported research
table.

## Label availability

The notebook defines an audit-only `label_known_at`:

- for `y_breach = 1`, the provisional label is treated as known at `deadline`;
- for `y_breach = 0`, the label is treated as known at `resolved_at`.

This supports cutoff-aware research splits. It does not claim that a real
production system will observe or publish labels at exactly those times.

## Known limitations

- SLA targets are illustrative and unverified.
- Source timezone is explicitly `unverified`.
- Reopened incidents are excluded, creating selection bias.
- Historical event rows can contain future outcome values.
- Same-minute earliest events can conflict.
- The label is a research target, not a measured contractual breach outcome.
