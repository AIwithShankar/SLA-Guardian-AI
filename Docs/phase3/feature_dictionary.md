# Phase 3 feature dictionary

> **All features below are provisional research inputs.** The dictionary is
> based on the notebook's `feature_columns` and exported columns. No model was
> trained in this phase.

## Approved provisional model inputs

| Feature | Type / units | Construction in notebook | Availability and risk |
|---|---|---|---|
| `priority` | categorical string | Priority from the earliest selected event; values include `1 - Critical`, `2 - High`, `3 - Moderate`, and `4 - Low` | Intended to be available at snapshot; tied earliest events had 15 priority conflicts before safe-cohort filtering |
| `category` | categorical string | Category from the earliest selected event; missing `?` or empty values become `Unknown` | Intended to be available at snapshot; tied earliest events had 7 category conflicts before safe-cohort filtering |
| `ticket_age_hours` | numeric hours | `snapshot_at - opened_at` | Derived from parsed naive timestamps; timezone is unverified |
| `remaining_sla_hours` | numeric hours | `deadline - snapshot_at` | Depends on the provisional 24/7 SLA policy and unverified timezone assumption |
| `created_hour` | integer 0–23 | Hour extracted from `opened_at` | Calendar feature from a naive timestamp; timezone and local-calendar semantics are unverified |
| `created_weekday` | integer weekday | `opened_at.dt.dayofweek` | Calendar feature from a naive timestamp; timezone and local-calendar semantics are unverified |

## Identifiers and audit metadata

The exported files also retain metadata used for auditing and splitting:

- `ticket_id`: incident identifier copied from `number`; asserted unique in the
  final feature cohort.
- `opened_at`: parsed opening timestamp.
- `snapshot_at`: earliest selected `sys_updated_at`.
- `resolved_at`: observed resolution timestamp, used for outcome labeling and
  maturity audits, **not an input feature**.
- `deadline`: `opened_at + sla_hours`, based on the provisional policy.
- `y_breach`: provisional binary target; see
  [sla_label_definition.md](./sla_label_definition.md).

## Excluded from model inputs

The notebook's approved `feature_columns` list excludes outcome or
post-snapshot fields such as `resolved_at`, `closed_at`, `closed_code`,
`resolved_by`, final state, and any `label_known_at` field. Those fields remain
available only for audit, label construction, or split maturity checks.

The notebook also does not establish that raw event-log fields are immutable
snapshots. Backfilled values and same-minute update ties must be resolved
before production feature generation.
