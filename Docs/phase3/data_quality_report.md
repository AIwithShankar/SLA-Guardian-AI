# Phase 3 data quality report

> **Status: provisional research documentation.** These findings describe the
> executed Colab notebook and `data/processed/dataset_manifest.json`. They are
> not evidence that the dataset is production-ready or that a model has been
> trained.

## Source and observed scope

- Source named by the manifest: **UCI Incident Management Process Enriched Event Log**.
- Raw event table observed in the notebook: **141,712 rows and 36 columns**.
- Unique incident IDs: **24,918**.
- Exact duplicate rows: **0**.
- Raw date range for `opened_at`: **2016-02-29 01:16** through **2017-02-16 14:17**.
- Raw date range for `sys_updated_at`: **2016-02-29 01:23** through **2017-02-18 15:00**.
- `sys_created_at` missing values: **53,076**.
- `resolved_at` missing values: **3,141**.
- No timestamp parse failures were reported using `%d/%m/%Y %H:%M`.
- Five rows had `sys_updated_at` earlier than `opened_at`; no rows had
  `resolved_at` earlier than `opened_at`.

## Incident-level consistency findings

The notebook reports:

- 275 incidents with `reopen_count > 0`.
- 383 incidents with changing priority.
- 1,184 incidents with changing category.
- 1,556 incidents without a resolution timestamp.
- 1,515 incidents excluded by the combined future priority/category-change
  screening in the revised audit.
- 2,212 incidents with tied earliest `sys_updated_at` timestamps.
- 848 incidents with any conflict among tied earliest observations.
- 93 incidents in the revised provisional cohort with ambiguous initial
  observations; the final safe feature cohort contained 22,320 incidents.
- 9,318 incidents with repeated update timestamps.

The event log contains outcome information on rows before that outcome was
known at the event timestamp: 87,471 event rows across 22,894 incidents had
`resolved_at > sys_updated_at`. The notebook also found 742 `Resolved` or
`Closed` event rows before `resolved_at`, affecting 558 incidents.

## Exported provisional artifacts

The manifest records these files and SHA-256 hashes:

| File | Role | Manifest count |
|---|---|---:|
| `train_provisional.csv` | Chronological training partition | 15,623 |
| `validation_provisional.csv` | Chronological validation partition | 3,349 |
| `test_provisional.csv` | Chronological test partition | 3,348 |
| `train_cutoff_eligible.csv` | Training rows whose labels are known by validation start | 15,447 |
| `validation_cutoff_eligible.csv` | Validation rows whose labels are known by test start | 3,221 |

The exported files are **provisional research artifacts**, not approved
training data. The manifest status is `provisional_research_dataset`.

## Preprocessing decisions recorded in the notebook

1. Load the event CSV as strings with `keep_default_na=False`.
2. Treat `""`, `"?"`, `"NULL"`, `"null"`, and `"None"` as missing tokens for
   audit and feature preparation.
3. Parse timestamps with the explicit format `%d/%m/%Y %H:%M`.
4. Sort events by `number` and `sys_updated_at`, using stable ordering.
5. Use the earliest observed event as the provisional prediction snapshot.
6. Exclude reopened incidents, incidents with missing resolution, invalid
   chronology, and unsuitable initial states during the conservative cohort
   construction.
7. Preserve category missing values as `"Unknown"` in the exported feature
   data.
8. Retain one row per incident and assert unique `ticket_id`, binary labels,
   non-negative ticket age, and positive remaining SLA time.
9. Split chronologically by `snapshot_at`; see
   [split_strategy.md](./split_strategy.md) for cutoff and maturity handling.

## Required cautions

### Historical data leakage

The source is an event log in which fields such as `resolved_at`, `closed_at`,
`closed_code`, and final state can appear on earlier event rows. The notebook
demonstrates this directly through the 87,471 future-resolution event rows and
the 742 resolved/closed rows before resolution. These fields must not be used
as prediction features. Even fields selected from the earliest event may be
backfilled or historically rewritten; the manifest therefore lists
backfilled historical fields as a limitation.

### Future outcome availability

The breach outcome is not known at snapshot time for every row. The notebook
defines `label_known_at` as the deadline for breaches and the resolution time
for on-time outcomes, then filters training and validation rows at the next
period boundary. This is a research control, not proof that operational
label publication will follow the same timing.

### Reopened-ticket selection bias

The provisional cohort excludes incidents with observed reopens (`275`
incidents). This removes a difficult and potentially informative class using
historical outcome information. Any resulting dataset may underrepresent
reopened workflows and should not be generalized to them without a separate
evaluation.

### Unverified timezone assumptions

The manifest explicitly records `source_timezone: "unverified"`. The notebook
parses naive timestamps and applies an illustrative 24/7 duration policy.
Cross-system comparisons, business-hour SLAs, daylight-saving behavior, and
tenant-local time semantics remain unverified.

## Decision

Use these artifacts only for research, data-contract review, and future
label/feature design. Do not treat the reported cohort or label rates as
production performance, model quality, or a validated business SLA.
