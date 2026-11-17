# Phase 4 Evaluation Report — executed Colab run

**Dataset:** Provisional UCI IT incident history; illustrative 24/7 SLA labels only.
**Training cutoff:** 2016-05-03 05:59:00; **selection cutoff:** 2016-05-16 17:33:00
**Fit rows:** 12200; **calibration rows:** 3090; **selection validation rows:** 3221
**Selected model:** lightgbm_15leaves; **sigmoid calibration:** True
**Alert threshold:** 0.7; **research export gate:** True

## Selection-validation metrics
```json
{
  "n": 3221,
  "positive_support": 1191,
  "negative_support": 2030,
  "positive_prevalence": 0.36976094380627134,
  "average_precision": 0.6218812278110046,
  "roc_auc": 0.7655544663796205,
  "brier": 0.1897853828931317,
  "threshold": 0.7,
  "precision": 0.7425742574257426,
  "recall": 0.06297229219143577,
  "f1": 0.11609907120743033,
  "true_negatives": 2004,
  "false_alerts": 26,
  "missed_breaches": 1116,
  "true_alerts": 75,
  "alerts": 101
}
```

## Final out-of-time test metrics (evaluated once)
```json
{
  "n": 3348,
  "positive_support": 1237,
  "negative_support": 2111,
  "positive_prevalence": 0.3694743130227001,
  "average_precision": 0.6357394347456864,
  "roc_auc": 0.7832282837674773,
  "brier": 0.1833733817779763,
  "threshold": 0.7,
  "precision": 0.7207207207207207,
  "recall": 0.0646725949878739,
  "f1": 0.11869436201780416,
  "true_negatives": 2080,
  "false_alerts": 31,
  "missed_breaches": 1157,
  "true_alerts": 80,
  "alerts": 111
}
```

## Methodological limitations
- Illustrative 24/7 SLA policy
- Earliest observed event used as feature snapshot
- Reopened incidents excluded using historical outcomes
- Historical event fields may contain backfilled values
- Same-minute update ambiguity remains a source limitation
- Outcome-maturity filtering creates a cutoff-dependent cohort
- Historical IT incidents differ from commercial support tickets
- Provisional 24/7 SLA policy is not a verified contract
- Maturity-filtered validation is selection-biased
- No prospectively demonstrated breach reduction
- Potential timestamp tie at validation/test boundary
- Source priority strings require a production adapter in the next phase

These retrospective figures do not prove production benefit or verified contractual SLA accuracy.