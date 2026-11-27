# Scientific design and acceptance

IBM Runtime BackendProperties exposes timestamped provider estimates. Qiskit Experiments supplies characterization experiments, while Aer constructs explicit simulation channels. Mitiq calibrates mitigation strategies. CalibMap's workflow carries historical availability and evidence into offline planning. Scalar gate error comparisons require matching protocol, gate, ordered operands and unit. VintageCheck is optional because collector and publication time can be checked directly.

References: [Runtime properties](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/models-backend-properties), [Aer noise models](https://qiskit.github.io/qiskit-aer/apidocs/aer_noise), [Mitiq calibrators](https://mitiq.readthedocs.io/en/stable/guide/calibrators.html).

| Area | Acceptance experiment |
|---|---|
| Data | Preserve calibrated, acquired and publication times across JSON/CSV |
| History | Exclude every observation unavailable at the inclusive cutoff |
| Qubit statistics | Match quantiles and variance on fixed irregular records |
| Gates | Preserve ordered operands and protocol when grouping |
| Readout | Recover binary probabilities by forward and inverse assignment |
| Coherence | Recover known exponential decay time within 0.1% on noiseless data |
| Drift | Control familywise alarms by spending alpha across prespecified metrics and looks under the Gaussian reference model |
| Change point | Match exhaustive squared-error partition objective |
| Uncertainty | Match a linear transformation of a correlated Gaussian vector |
| Correlation | Count only timestamp-matched pairs and detect indefinite covariance |
| Topology | Match exhaustive shortest simple paths for nonnegative edge costs |
| Noise | Separate impossible outcomes from sampling residuals |
| Forecast | Score predictions made exclusively from earlier observations |
| Readiness | Explain every missing, stale or failed criterion |
| Reporting | Identical evidence and parameters produce identical bytes |

## Measurement budgets and uncertainty

The integrated example simulates 3,000 calibrations in each preparation direction on two qubits (12,000 shots). The planning budget is 10,000 per confirmatory sample. Each of the two independent samples uses the same allocation; the total is 32,000 shots with no empirical pilot. ShotWeave receives point estimates. Its conditional variance omits acquisition uncertainty. BornLens compares raw observed Z outcomes with prespecified tolerance 0.12 and per-observable confidence 97.5%.

For contrast d = 1 − e0 − e1 the inverse gradient in observed frequency, e0, e1 order is (1, p−1, p)/d. Joint covariance retains calibration–measurement cross terms. The inverse can lie outside [0,1]. No clipping is applied. Large condition numbers invalidate perturbative interpretation, even before numerical inversion fails.

Under known Gaussian marginal means and variances, per-look two-sided error spending is 6α/(π² m t²) across m prespecified metrics. The union bound controls the probability of any false alarm even when the marginal observations are dependent. Estimating the reference from the monitored sequence invalidates this guarantee. The original benchmark counts a post-change hit regardless of earlier alarms. The scenario benchmark conditions on survival and reports early alarms and misses separately.

## Design limits and review evidence

- The temporal oracle selects the latest eligible physical epoch by exhaustive scan. Future publication excludes an observation even if calibration and acquisition precede the decision. At equal rank, conflicting evidence is rejected.
- The offline segmentation objective is the sum of squared deviations from each segment mean plus a cost for every interior boundary. A minimum segment length applies in observations. Variance shifts are stress tests for a mean-shift objective.
- Gate and qubit summaries use actual calibration epochs. Missing frequency among observed epochs and long gaps answer different questions. Without a declared acquisition schedule, a long gap does not determine how many provider calibrations occurred.
- Pairwise covariance uses matched finite observations; inconsistent pairwise deletion can yield an indefinite matrix. Holm adjustment uses the full prespecified family, including unidentified pairs conservatively. Shared trends and simultaneous recalibration can induce strong associations.
- Date matching requires the exact event timestamp. A nonzero lag shifts the second series by the requested lag in the timestamp units. No interpolation is implicit.
- For a fixed multinomial model the asymptotic reference uses one fewer degree of freedom than the number of positive categories. The sparse Monte Carlo alternative samples from the specified model with the original total. New parameter estimation requires a different calibration of the test.
- An uncertainty matrix is an explicit input. For a nearly singular readout matrix, derivatives may explode or the inverse may fail the condition limit. Gaussian propagation assumes the supplied parameterization is locally meaningful; transforms can reject out-of-domain draws. Callers should report such failures.
