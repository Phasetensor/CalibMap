# CalibMap

Offline quantum calibration analytics for PhaseTensor. Development branch. Use timezone-aware calibration, acquisition and publication timestamps to reconstruct historical evidence. Keep provider estimates, synthetic experiments and acquired measurements identifiable throughout analysis.

## Running the examples

With NumPy, SciPy and pytest installed, run the following from the checkout.

    python -m pytest
    PYTHONPATH=. python benchmarks/principal.py
    PYTHONPATH=. python benchmarks/interoperability.py

The interoperability example also needs ShotWeave 0.2.0 and BornLens 0.3.1. It uses independent random calibration and confirmatory draws, fixed physical qubit ordering and a 10,000-shot design budget. The examples incur no hardware charges.

## Methods

See [scientific design](docs/methodology.md) and [benchmark results](benchmarks/principal.json). Assignment matrices use observed rows and prepared columns. Converting a measured frequency back to prepared probability requires directional calibration and a well-conditioned matrix. The Gaussian monitoring thresholds require a prespecified mean and variance. Offline segmentation uses future observations and supports retrospective analysis only.

## Evidence and installation

The development package builds with python -m build. Install the optional interop extra for the integrated example or the ibm extra for IBM Runtime property objects. The public API and limits are indexed in [the module matrix](docs/traceability.md). [Reproduction instructions](docs/advanced.md) cover the three case studies and figures. The scientific-studies artifact in Actions contains the generated figures and numerical results from the same run.

The [API guide](docs/api.md) lists input and output contracts by module. Python 3.11–3.14 have been exercised in CI. IBM Runtime and interoperation workflows are tested separately on the environments recorded in the validation workflow.
