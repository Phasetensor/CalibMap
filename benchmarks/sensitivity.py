"""Reference uncertainty, correlated looks and forecast-horizon sensitivity."""

import json

import numpy as np

from calibmap.planning import forecast
from calibmap.series import monitor

rng = np.random.default_rng(941)
n = 10000
joint_hits = 0
estimated_hits = 0
for _ in range(n):
    x = rng.normal(size=24)
    y = 0.8 * x + 0.6 * rng.normal(size=24)
    joint_hits += bool(
        monitor(x, 0, 1, metrics=2).any() or monitor(y, 0, 1, metrics=2).any()
    )
    ref = rng.normal(size=12)
    estimated_hits += bool(monitor(x, ref.mean(), ref.std(ddof=1)).any())


def frequency(hits):
    p = hits / n
    return {
        "hits": hits,
        "replicates": n,
        "rate": p,
        "mc_se": float(np.sqrt(p * (1 - p) / n)),
    }


output = {
    "seed": 941,
    "two_correlated_metrics": frequency(joint_hits),
    "estimated_reference_heuristic": frequency(estimated_hits),
}
forecasts = []
for horizon in (1, 3, 8):
    for assumed_process, assumed_noise in ((0.25, 1), (0.01, 1), (0.25, 0.2)):
        errors, covered, widths = [], [], []
        for _ in range(500):
            t = np.r_[0, np.cumsum(rng.integers(1, 5, size=18))]
            latent = np.r_[
                0, np.cumsum(rng.normal(size=len(t) - 1) * np.sqrt(0.25 * np.diff(t)))
            ]
            training = latent + rng.normal(size=len(t))
            outcome = (
                latent[-1] + rng.normal(scale=np.sqrt(0.25 * horizon)) + rng.normal()
            )
            pred, lo, hi = forecast(
                t, training, horizon, assumed_process, assumed_noise
            )
            errors.append(pred - outcome)
            covered.append(lo <= outcome <= hi)
            widths.append(hi - lo)
        p = float(np.mean(covered))
        forecasts.append(
            {
                "horizon": horizon,
                "process_rate": assumed_process,
                "observation_variance": assumed_noise,
                "n": len(errors),
                "mae": float(np.mean(np.abs(errors))),
                "rmse": float(np.sqrt(np.mean(np.square(errors)))),
                "future_coverage": p,
                "coverage_mc_se": float(np.sqrt(p * (1 - p) / len(errors))),
                "width": float(np.mean(widths)),
            }
        )
output["irregular_local_level"] = forecasts
print(json.dumps(output, indent=2))
