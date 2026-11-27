"""Calibrated graph, held-out noise diagnostics, forecasting and planning."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta
from heapq import heappop, heappush

import numpy as np
from scipy.stats import chi2, norm

from . import Record, as_of
from .series import vector


def shortest_path(
    edges: dict[tuple[int, int], float], start: int, end: int
) -> tuple[float, tuple[int, ...]]:
    """Costs must share a user-defined additive objective and unit."""
    neighbors: dict[int, list[tuple[int, float]]] = {}
    for (a, b), weight in edges.items():
        if not 0 <= weight < np.inf:
            raise ValueError("Costs must be finite and nonnegative")
        neighbors.setdefault(a, []).append((b, weight))
    queue: list[tuple[float, tuple[int, ...]]] = [(0.0, (start,))]
    visited = set()
    while queue:
        cost, path = heappop(queue)
        node = path[-1]
        if node in visited:
            continue
        if node == end:
            return cost, path
        visited.add(node)
        for successor, weight in neighbors.get(node, []):
            heappush(queue, (cost + weight, path + (successor,)))
    raise ValueError("Unreachable target")


def goodness(counts: np.ndarray, probabilities: np.ndarray) -> dict:
    """Fixed, externally specified multinomial model. Sparse cells suppress asymptotic p."""
    x, p = vector(counts, 2), vector(probabilities, 2)
    if (
        x.shape != p.shape
        or (x < 0).any()
        or (x != np.floor(x)).any()
        or x.sum() == 0
        or (p < 0).any()
        or not np.isclose(p.sum(), 1.0, rtol=0, atol=1e-12)
    ):
        raise ValueError("Invalid multinomial data")
    expected = x.sum() * p
    mask = p > 0
    residual = x - expected
    impossible = bool(np.any(x[~mask] > 0))
    stat = (
        float("inf")
        if impossible
        else float(np.sum(residual[mask] ** 2 / expected[mask]))
    )
    pv = None
    if impossible:
        pv = 0.0
    elif mask.sum() > 1 and min(expected[mask]) >= 5:
        pv = float(chi2.sf(stat, mask.sum() - 1))
    return {
        "residual": residual.tolist(),
        "statistic": stat,
        "p_value": pv,
        "impossible": impossible,
    }


def forecast(
    times: np.ndarray,
    values: np.ndarray,
    horizon: float,
    process_rate: float,
    observation_var: float,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    """Local-level model, known variance rates, diffuse initial level at first observation."""
    t, x = vector(times), vector(values)
    if (
        t.shape != x.shape
        or np.any(np.diff(t) <= 0)
        or not all(np.isfinite([horizon, process_rate, observation_var]))
        or horizon <= 0
        or process_rate < 0
        or observation_var <= 0
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid time series or model")
    level, var = x[0], observation_var
    for dt, y in zip(np.diff(t), x[1:]):
        var += process_rate * dt
        gain = var / (var + observation_var)
        level += gain * (y - level)
        var = (1 - gain) * var
    width = norm.isf(alpha / 2) * np.sqrt(
        var + process_rate * horizon + observation_var
    )
    return float(level), float(level - width), float(level + width)


def readiness(
    records: Iterable[Record],
    at: datetime,
    max_age: timedelta,
    upper_bounds: dict[tuple, float],
) -> tuple[str, dict]:
    """Keys are (backend, metric, qubits, gate, unit, source, kind)."""
    if (
        max_age < timedelta()
        or not upper_bounds
        or not np.isfinite(list(upper_bounds.values())).all()
    ):
        raise ValueError("Explicit criteria and nonnegative maximum age required")
    from .records import normalize

    latest = {}
    for row in as_of(records, at):
        canonical = normalize(row)
        for key in upper_bounds:
            if row.identity(key[4]) != key:
                continue
            probe = normalize(
                Record(
                    row.backend,
                    row.metric,
                    row.qubits,
                    row.calibrated,
                    row.acquired,
                    row.published,
                    1.0,
                    key[4],
                    row.source,
                    row.kind,
                )
            )
            if probe.unit == canonical.unit and probe.value is not None:
                from dataclasses import replace

                latest[key] = replace(
                    canonical,
                    value=None
                    if canonical.value is None
                    else canonical.value / probe.value,
                    unit=key[4],
                )
    outcomes = {}
    for key, limit in upper_bounds.items():
        observation = latest.get(key)
        if observation is None or observation.value is None:
            outcomes[key] = "missing evidence"
        elif at - observation.calibrated > max_age:
            outcomes[key] = "stale"
        elif observation.value > limit:
            outcomes[key] = "above threshold"
        else:
            outcomes[key] = "pass"
    reasons = set(outcomes.values())
    state = (
        "NOT_READY"
        if reasons & {"stale", "above threshold"}
        else "UNKNOWN"
        if "missing evidence" in reasons
        else "READY"
    )
    return state, outcomes


def multinomial_mc(
    counts: np.ndarray, probabilities: np.ndarray, draws: int, seed: int
) -> dict:
    """Plus-one Monte Carlo test with a prespecified fixed multinomial null."""
    result = goodness(counts, probabilities)
    if type(draws) is not int or draws < 1:
        raise ValueError("Positive replicate count required")
    p = np.asarray(probabilities, dtype=float)
    n = int(np.sum(counts))
    result["total_variation"] = float(np.sum(abs(np.asarray(counts) / n - p)) / 2)
    if result["impossible"]:
        result["mc_p"] = 0.0
        return result
    mask = p > 0
    expected = n * p[mask]
    sim = np.random.default_rng(seed).multinomial(n, p, size=draws)[:, mask]
    simulated_stat = np.sum((sim - expected) ** 2 / expected, axis=1)
    result["mc_p"] = (1 + int(np.sum(simulated_stat >= result["statistic"]))) / (
        1 + draws
    )
    return result
