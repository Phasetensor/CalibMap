# Module evidence for the development branch

All numerical evidence here comes from offline data. A reference test verifies the stated property only. No production release has been issued by this project workflow.

| Module | Public entry point and source | Current evidence | Scope limit |
|---|---|---|---|
| Data | Record, records.load/export/ibm_properties | JSON/CSV round trips and representative provider fixture in test_science | Live acquisition untested |
| History | as_of, history.timelines | Randomized future invariance and chronological oracle in test_temporal | Availability depends on supplied timestamps |
| Qubit stability | history.stability, series.describe | Fixed quantiles, variance, temporal window and gap checks | Descriptive uncertainty only |
| Gates | history.timelines/stability | Ordered operand and mixed-protocol tests | Provider protocols must be identified |
| Readout | readout.Binary/interval | Forward inversion, conditioning and binomial boundary checks | Preparation and measurement effects may be confounded |
| Coherence | series.decay | Recovery of known noiseless decay in test_science | Weakly identified parameters require further investigation |
| Online drift | series.monitor | 10,000 trajectories per scenario in scenarios.json | Gaussian marginal assumptions with known reference |
| Offline change point | series.segments | Exhaustive small-instance oracle and 200 paths per scenario | Penalized mean changes indexed by observations |
| Calibration uncertainty | uncertainty.posterior/propagate/corrected_variance | Central differences and 10,000 Gaussian draws in test_uncertainty | Local linearization for smooth transforms |
| Correlation | series.correlation, diagnostics.dependence | Negative, sparse, constant and indefinite pairwise examples | Pearson p-values require independent paired observations across time |
| Topology | planning.shortest_path, diagnostics.components/candidates | Directed paths and connected subsets tested | Candidate enumeration scales combinatorially |
| Noise model | planning.goodness | Exact null statistic and impossible-outcome tests | Fixed model, sparse asymptotic tests withheld |
| Forecast | planning.forecast | Walk-forward comparisons with last, rolling mean and smoothing | Future-observation interval assumes specified process and observation variances |
| Readiness | experiment.evaluate, planning.readiness | Criterion provenance, failed/unknown precedence, stale and conflicting records | Supplied topology and alarms must be available at decision time |
| Reports | reporting.Report | JSON/CSV equivalence, escaping, undefined values and deterministic construction | Caller supplies results, metric definitions and assumptions |

### Consolidation evidence

The IBM provider integration ran on the real Runtime object for the bundled Athens snapshot. gate_changes compares snapshots for matched directed gates. joint_inverse accepts an explicitly supplied joint assignment. Tests compare correlated inversion with a known joint distribution, graph distances with exhaustive path enumeration, sparse goodness-of-fit with an exact binomial test, and covariance propagation with central differences. The temporal property test uses Hypothesis. Scientific scripts and additional reference tests live under benchmarks/ and tests/test_references.py respectively.
