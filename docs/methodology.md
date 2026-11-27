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
