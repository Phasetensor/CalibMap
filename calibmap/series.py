"""Offline descriptive and monitoring statistics."""

from __future__ import annotations

from math import pi

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import norm, pearsonr, spearmanr


def vector(values: np.ndarray, minimum: int = 1) -> np.ndarray:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < minimum or not np.isfinite(x).all():
        raise ValueError("Expected a finite one-dimensional sample")
    return x


def describe(values: np.ndarray) -> dict[str, float]:
    x = vector(values, 2)
    median = np.median(x)
    return {
        "mean": float(x.mean()),
        "median": float(median),
        "variance": float(x.var(ddof=1)),
        "mad": float(np.median(abs(x - median))),
        "q05": float(np.quantile(x, 0.05)),
        "q95": float(np.quantile(x, 0.95)),
    }


def decay(times: np.ndarray, values: np.ndarray) -> tuple[float, float, float]:
    t, x = vector(times, 4), vector(values, 4)
    if t.shape != x.shape or np.any(np.diff(t) <= 0) or t[0] < 0 or np.ptp(x) == 0:
        raise ValueError("Decay needs increasing times and an identifiable amplitude")
    scale = t[-1] - t[0]

    def model(s: np.ndarray, a: float, tau: float, b: float) -> np.ndarray:
        return a * np.exp(-s / tau) + b

    params, _ = curve_fit(
        model,
        t / scale,
        x,
        p0=(x[0] - x[-1], 0.5, x[-1]),
        bounds=([-np.inf, 1e-12, -np.inf], np.inf),
        maxfev=10000,
    )
    return float(params[0]), float(params[1] * scale), float(params[2])


def monitor(
    values: np.ndarray, mean: float, sigma: float, alpha: float = 0.05, metrics: int = 1
) -> np.ndarray:
    """Two-sided Gaussian marginal alarms with summable alpha spending."""
    x = vector(values)
    if (
        not np.isfinite([mean, sigma]).all()
        or sigma <= 0
        or type(metrics) is not int
        or metrics < 1
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid prespecified Gaussian reference")
    t = np.arange(1, len(x) + 1, dtype=float)
    return abs(x - mean) / sigma > norm.isf(3 * alpha / (pi * pi * metrics * t * t))


def segments(values: np.ndarray, penalty: float, minimum: int = 2) -> tuple[int, ...]:
    """Exact retrospective least-squares partition, penalty per internal boundary."""
    x = vector(values)
    if (
        type(minimum) is not int
        or not 1 <= minimum <= len(x)
        or not 0 <= penalty < np.inf
    ):
        raise ValueError("Invalid segmentation constraints")
    x = x - x.mean()
    s = np.r_[0.0, x.cumsum()]
    q = np.r_[0.0, (x * x).cumsum()]
    cost = np.full(len(s), np.inf)
    cost[0] = -penalty
    prev = np.zeros(len(s), dtype=int)
    for end in range(minimum, len(s)):
        starts = np.arange(end - minimum + 1)
        scores = (
            cost[starts]
            + penalty
            + q[end]
            - q[starts]
            - (s[end] - s[starts]) ** 2 / (end - starts)
        )
        prev[end] = starts[np.argmin(scores)]
        cost[end] = scores.min()
    cuts = []
    at = int(prev[-1])
    while at:
        cuts.append(at)
        at = int(prev[at])
    return tuple(reversed(cuts))


def correlation(
    a: dict[float, float], b: dict[float, float], lag: float = 0.0
) -> dict[str, float]:
    """Exact timestamp match at t and t+lag. Missing pairs are dropped."""
    pairs = [
        (v, b[t + lag])
        for t, v in sorted(a.items())
        if t + lag in b and np.isfinite([v, b[t + lag]]).all()
    ]
    if len(pairs) < 3:
        raise ValueError("At least three aligned pairs required")
    x, y = np.array(pairs).T
    if min(np.ptp(x), np.ptp(y)) == 0:
        raise ValueError("Constant matched series")
    return {
        "overlap": len(x),
        "pearson": float(pearsonr(x, y)[0]),
        "spearman": float(spearmanr(x, y)[0]),
    }


def decay_diagnostics(times: np.ndarray, values: np.ndarray) -> dict:
    """OLS residuals and local uncertainty for iid Gaussian, equal-variance errors."""
    a, tau, b = decay(times, values)
    t = np.asarray(times)
    exponential = np.exp(-t / tau)
    residual = np.asarray(values) - (a * exponential + b)
    jac = np.column_stack((exponential, a * exponential * t / tau**2, np.ones(len(t))))
    norms = np.linalg.norm(jac, axis=0)
    condition = float(np.linalg.cond(jac / np.where(norms > 0, norms, 1)))
    identifiable = bool(condition < 1e6 and np.all(norms > 0))
    stderr = None
    if identifiable:
        inverse = np.linalg.pinv(jac)
        variance = float(residual @ residual / (len(t) - 3))
        stderr = np.sqrt(np.sum(inverse**2, axis=1) * variance).tolist()
    return {
        "parameters": (a, tau, b),
        "residuals": residual.tolist(),
        "stderr": stderr,
        "scaled_condition": condition,
        "locally_identifiable": identifiable,
    }
