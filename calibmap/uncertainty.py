"""Uncertainty propagation under explicitly supplied calibration assumptions."""

from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.stats import beta

from .readout import Binary, delta, interval


def posterior(
    k: int, n: int, prior: tuple[float, float] = (1.0, 1.0), alpha: float = 0.05
) -> dict:
    interval(k, n, alpha)
    if len(prior) != 2 or not all(0 < x < np.inf for x in prior):
        raise ValueError("Positive finite beta prior required")
    a, b = k + prior[0], n - k + prior[1]
    return {
        "shape": (a, b),
        "mean": a / (a + b),
        "credible": tuple(beta.ppf([alpha / 2, 1 - alpha / 2], a, b)),
    }


def corrected_variance(
    observed: float, assignment: Binary, covariance: np.ndarray
) -> float:
    """Joint covariance order is observed frequency, e0, e1."""
    p, _ = assignment.invert(observed)
    j = np.array([1.0, p - 1, p]) / assignment.contrast
    return float(delta(j, covariance).item())


def propagate(
    transform: Callable, mean: np.ndarray, cov: np.ndarray, draws: int, seed: int
) -> np.ndarray:
    """Gaussian parameter simulation. The transform receives one parameter vector at a time."""
    mu = np.asarray(mean, dtype=float)
    if mu.ndim != 1 or not np.isfinite(mu).all() or type(draws) is not int or draws < 2:
        raise ValueError("Invalid mean or replicate count")
    delta(np.eye(len(mu)), cov)
    eigenvalues, axes = np.linalg.eigh(cov)
    factor = axes * np.sqrt(np.maximum(eigenvalues, 0))
    normals = np.random.default_rng(seed).standard_normal((draws, len(mu)))
    samples = mu + np.einsum("ij,kj->ik", normals, factor)
    return np.asarray([transform(x) for x in samples])


def independent_assignment(models: tuple[Binary, ...]) -> np.ndarray:
    """Tensor factors in supplied order, first physical qubit most significant."""
    if not models:
        raise ValueError("Explicit qubit order required")
    matrix = np.ones((1, 1))
    for model in models:
        matrix = np.kron(matrix, model.matrix)
    return matrix
