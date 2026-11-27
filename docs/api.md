# Public API guide

| Import | Input | Output |
|---|---|---|
| calibmap.Record, as_of | Typed physical observation and a timezone-aware cutoff | Latest eligible revisions by physical identity |
| records.normalize, export, load | Compatible units or a sequence of records | Canonical seconds or round-trippable JSON/CSV |
| records.ibm_properties | IBM Runtime BackendProperties object and actual read time | Provider-reported estimates |
| history.timelines, stability, gate_changes | Records, historical cutoff or comparison epochs | Revision groups, trailing dispersion and directional changes |
| readout.Binary, interval, joint_inverse | Conditional assignment probabilities, trial counts or full joint calibration | Unclipped correction, exact binomial interval or joint inverse |
| series.decay_diagnostics | Increasing delays and measured amplitude | Exponential parameters, residuals, local standard errors and condition |
| series.monitor, segments | Ordered sequence and prespecified reference or segmentation penalty | Sequential flags or offline boundary indices |
| uncertainty.posterior, corrected_variance, propagate | Binomial observations or a specified joint covariance | Beta posterior, delta variance or seeded Gaussian draws |
| series.correlation, diagnostics.dependence | Timestamp-keyed series | Matched correlations, pairwise counts, covariance and PSD check |
| diagnostics.components, candidates, planning.shortest_path | Physical nodes and directed edges with one additive cost unit | Weak components, connected subsets or minimum cost path |
| planning.goodness, multinomial_mc | Held-out counts and fixed predicted probabilities | Residuals, discrepancy and conditional tests |
| planning.forecast | Increasing times, training observations, horizon and variance rates | Predicted future observation and two-sided interval |
| experiment.Criterion, evaluate | Canonical thresholds, records, topology, alarms, cutoff | Explained READY, UNKNOWN or NOT_READY verdict |
| reporting.Report | Inputs, assumptions, outputs, definitions and reproduction parameters | Immutable report with deterministic JSON, CSV or escaped HTML |

For each module import the listed symbol from the calibmap submodule named in the table. Calendrical records require explicit timezones. Numeric time-series APIs use a consistent caller-selected time unit. A process variance rate has units of metric squared per time unit. Change points and Gaussian monitoring looks are indexed by observation count.
