"""Seeded simulation under known Gaussian null and independent binomial sampling."""

import json
import resource
import sys
import time

import numpy as np

from calibmap.readout import interval
from calibmap.series import monitor, segments

rng = np.random.default_rng(4701)
start = time.perf_counter()
n = 10000
x = rng.normal(size=(n, 40))
false = np.array([monitor(path, 0, 1).any() for path in x])
x[:, 20:] += 4
alarms = np.array([monitor(path, 0, 1)[20:] for path in x])
hits = alarms.any(axis=1)
k = rng.binomial(100, 0.1, n)
bounds = np.array([interval(count, 100) for count in range(101)])
lo, hi = bounds[k].T


def rate(mask):
    p = float(mask.mean())
    return {"rate": p, "monte_carlo_se": float(np.sqrt(p * (1 - p) / len(mask)))}


cuts = [segments(v, 12) for v in x[:200]]
print(
    json.dumps(
        {
            "seed": 4701,
            "replications": n,
            "false_alarm": rate(false),
            "power": rate(hits),
            "conditional_delay_mean": float(alarms[hits].argmax(axis=1).mean()),
            "readout_coverage": rate((lo <= 0.1) & (0.1 <= hi)),
            "readout_rmse": float(np.sqrt(np.mean((k / 100 - 0.1) ** 2))),
            "readout_bias": float(np.mean(k / 100 - 0.1)),
            "exact_change_only": float(np.mean([c == (20,) for c in cuts])),
            "segmentation_replications": len(cuts),
            "seconds": time.perf_counter() - start,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            * (1 if sys.platform == "darwin" else 1024),
        },
        indent=2,
    )
)
