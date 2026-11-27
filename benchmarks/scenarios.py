"""Independent offline scenarios. Run from the checkout with PYTHONPATH=."""

import json
import platform

import numpy as np
import scipy
from scipy.stats import binomtest

from calibmap.planning import forecast
from calibmap.readout import Binary
from calibmap.series import monitor, segments
from calibmap.uncertainty import corrected_variance, propagate

rng = np.random.default_rng(1047)
results = {
    "seed": 1047,
    "python": platform.python_version(),
    "numpy": np.__version__,
    "scipy": scipy.__version__,
}
scenarios = {}
for label, shift in {
    "null": 0,
    "small": 0.5,
    "large": 4,
    "gradual": np.linspace(0, 3, 20),
    "variance": 0,
}.items():
    paths = rng.normal(size=(10000, 40))
    paths[:, 20:] += shift
    if label == "variance":
        paths[:, 20:] *= 2
    alarms = np.array([monitor(path, 0, 1) for path in paths])
    eligible = ~alarms[:, :20].any(axis=1)
    post = alarms[eligible, 20:]
    hit = post.any(axis=1)
    cuts = [segments(x, 12) for x in paths[:200]]
    locations = [min(abs(c - 20) for c in cut) for cut in cuts if cut]
    ci = binomtest(int(hit.sum()), len(hit)).proportion_ci()
    scenarios[label] = dict(
        eligible=int(eligible.sum()),
        early_alarms=int((~eligible).sum()),
        missed=int((~hit).sum()),
        conditional_detection=float(hit.mean()),
        ci=list(ci),
        mean_delay=float(post[hit].argmax(axis=1).mean()) if hit.any() else None,
        segmented_paths=sum(bool(c) for c in cuts),
        segmentation_total=len(cuts),
        nearest_boundary_error=float(np.mean(locations)) if locations else None,
    )
results["drift"] = scenarios
forecasts = {}
for name in ("stationary", "drift", "shift"):
    errors = {k: [] for k in ("last", "mean5", "ewma", "local_level")}
    covered, widths = [], []
    for _ in range(100):
        times = np.cumsum(rng.integers(1, 4, size=36))
        series = rng.normal(size=36)
        if name == "drift":
            series += 0.025 * times
        if name == "shift":
            series[23:] += 3
        for k in range(15, len(times), 3):
            train = series[:k]
            prediction, lo, hi = forecast(
                times[:k], train, times[k] - times[k - 1], 0.05, 1
            )
            smooth = train[0]
            for v in train[1:]:
                smooth = 0.3 * v + 0.7 * smooth
            for method, p in zip(
                errors, (train[-1], np.mean(train[-5:]), smooth, prediction)
            ):
                errors[method].append(p - series[k])
            covered.append(lo <= series[k] <= hi)
            widths.append(hi - lo)
    forecasts[name] = {
        k: dict(
            mae=float(np.mean(np.abs(v))), rmse=float(np.sqrt(np.mean(np.square(v))))
        )
        for k, v in errors.items()
    }
    forecasts[name]["future_observation_interval"] = dict(
        coverage=float(np.mean(covered)), mean_width=float(np.mean(widths))
    )
results["forecast"] = forecasts
point = np.array([0.44, 0.12, 0.21])
cov = np.array([[3.0, 1.0, -0.2], [1.0, 2.0, 0.6], [-0.2, 0.6, 1.0]]) * 1e-6


def correction(x):
    return Binary(*x[1:]).invert(x[0])[0]


draws = propagate(correction, point, cov, 10000, 1047)
model = Binary(*point[1:])
results["readout"] = dict(
    replicates=len(draws),
    known_variance=float(cov[0, 0] / model.contrast**2),
    delta=corrected_variance(point[0], model, cov),
    mc=float(draws.var(ddof=1)),
    condition=float(np.linalg.cond(model.matrix)),
    near_singular_condition=float(np.linalg.cond(Binary(0.49, 0.5099999).matrix)),
)
print(json.dumps(results, indent=2, allow_nan=False))
