# Reproducing the scientific studies

Run from the installed checkout. All examples use synthetic inputs and fixed pseudorandom seeds.

    PYTHONPATH=. python benchmarks/principal.py
    PYTHONPATH=. python benchmarks/scenarios.py
    PYTHONPATH=. python benchmarks/interoperability.py

The first experiment reproduces the original 40-look benchmark through public monitor, segmentation and interval APIs. The second evaluates five drift regimes, counts early alarms and misses, compares four forecasts under temporal train/test separation and propagates a full joint covariance. It uses 200 retrospective segmentations per regime because dynamic programming scales quadratically in series length. Forecast errors are pooled across rolling origins and are dependent within a trajectory.

The integration study requires shotweave==0.2.0 and bornlens==0.3.1. Shot allocation uses an explicit rightmost-qubit-zero Pauli convention. The shot budgets and the distinction between conditional measurement variance and calibration variance are described in methodology.md.

Use reports by passing records, metric definitions, assumptions, missing evidence and analysis outputs to reporting.Report.create. Convert tuple-keyed or dated analysis outputs to explicitly named fields before serialization. All thresholds in experiment.evaluate use canonical units (seconds for known time units).

## Provider integration and graphics

The provider integration imports FakeAthensV2 from the installed IBM Runtime package and calls its public properties method. Runtime 0.52.1 yielded 101 timestamped records for the bundled ibmq_athens device snapshot. The acquisition timestamp denotes reading the offline object. The provider publication timestamp remains unknown. This procedure submits no jobs.

Set MPLBACKEND=Agg and run benchmarks/plot_results.py and benchmarks/device_study.py with the package installed. The studies job attaches SVG figures and the numerical inputs from the same run. Device diagnostics use a separate deterministic synthetic trajectory with seed 138.

## Additional API conventions

gate_changes compares only matching metric, protocol, source, backend, gate and ordered operands. Numeric time quantities use seconds. joint_inverse accepts a full column-stochastic assignment calibrated in the same joint basis as the observed distribution. Marginal readout does not determine this input. Both binary and joint inversion return unconstrained estimates, including negative values when observations lie outside the calibrated image.

decay_diagnostics uses a residual variance estimate and the local Jacobian of a single exponential with offset. Errors assume equal-variance independent measurements. A large column-scaled condition number suppresses standard errors. A Ramsey envelope, echo envelope and T1 population curve require separate protocols. A single exponential may be inadequate for oscillatory or multi-component signals.

multinomial_mc simulates the prespecified multinomial null, using a plus-one tail estimate for sparse cells. Its p-value is conditional on the supplied model. Parameter estimation and held-out assessment should use independent observations.

The sensitivity study (benchmarks/sensitivity.py) monitors two correlated Gaussian metrics with shared alpha, then repeats monitoring with a short independently estimated reference, which is heuristic. Its forecast experiments use independent trajectories with irregular observation times and known ground truth. Forecast horizons of 1, 3 and 8 are scored under correct and misspecified variance rates. The checked-in JSON includes Monte Carlo standard errors for coverage.

## Artifact provenance

Development distributions come from the packaging job. Its SHA256SUMS was calculated before the clean wheel and source installation checks. Rebuilding an sdist at another time can change archive timestamps. Use the retained files when comparing digests. Public release digests become available only after the approved stable publication.
