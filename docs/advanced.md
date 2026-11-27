# Reproducing the scientific studies

Run from the installed checkout. All examples use synthetic inputs and fixed pseudorandom seeds.

    PYTHONPATH=. python benchmarks/principal.py
    PYTHONPATH=. python benchmarks/scenarios.py
    PYTHONPATH=. python benchmarks/interoperability.py

The first experiment reproduces the original 40-look benchmark through public monitor, segmentation and interval APIs. The second evaluates five drift regimes, counts early alarms and misses, compares four forecasts under temporal train/test separation and propagates a full joint covariance. It uses 200 retrospective segmentations per regime because dynamic programming scales quadratically in series length. Forecast errors are pooled across rolling origins and are dependent within a trajectory.

The integration study requires shotweave==0.2.0 and bornlens==0.3.1. Shot allocation uses an explicit rightmost-qubit-zero Pauli convention. The shot budgets and the distinction between conditional measurement variance and calibration variance are described in methodology.md.

Use reports by passing records, metric definitions, assumptions, missing evidence and analysis outputs to reporting.Report.create. Convert tuple-keyed or dated analysis outputs to explicitly named fields before serialization. All thresholds in experiment.evaluate use canonical units (seconds for known time units).
