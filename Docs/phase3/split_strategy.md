# Phase 3 split strategy

> **Status: provisional research split.** No model training or performance
> evaluation was performed.

## Chronological partitioning

The notebook sorts the final provisional records by `snapshot_at` and
`ticket_id` using stable ordering, then assigns:

- first 70% to training;
- next 15% to validation;
- final 15% to test.

The resulting full partition sizes are:

| Partition | Rows | Breach rate recorded by notebook |
|---|---:|---:|
| Train | 15,623 | 0.5294 |
| Validation | 3,349 | 0.3876 |
| Test | 3,348 | 0.3695 |

The validation period starts at **2016-05-03 05:59:00** and the test period
starts at **2016-05-16 17:33:00**.

## Outcome-maturity filtering

The notebook treats a label as known at `deadline` for breaches and at
`resolved_at` for on-time outcomes. It then retains rows whose `label_known_at`
is no later than the next partition boundary:

| Cutoff-eligible partition | Rows | Label counts |
|---|---:|---|
| Training by validation start | 15,447 | 7,317 non-breach; 8,130 breach |
| Validation by test start | 3,221 | 2,030 non-breach; 1,191 breach |

The test partition remains the full chronological test observation window in
the notebook. Its recorded label counts are **2,111 non-breach** and **1,237
breach** across 3,348 rows.

## Isolation and limitations

The notebook asserts disjoint `ticket_id` sets across train, validation, and
test and reports `Split isolation: PASS`.

This strategy is preferred to a random row split because the source contains
multiple event rows per incident and future outcomes on earlier rows. It still
depends on the provisional snapshot construction and cannot remove backfill,
same-minute ordering, timezone, or selection-bias risks. The full partitions
and cutoff-eligible files must therefore remain labeled as provisional.
