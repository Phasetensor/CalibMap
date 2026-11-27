"""Binary assignment with observed rows and prepared columns."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import beta


def interval(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Equal-tailed Clopper-Pearson interval for independent Bernoulli trials."""
    if (
        type(k) is not int
        or type(n) is not int
        or not 0 <= k <= n
        or n < 1
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid binomial experiment")
    return (
        float(beta.ppf(alpha / 2, k, n - k + 1)) if k else 0.0,
        float(beta.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.0,
    )


@dataclass(frozen=True)
class Binary:
    e0: float
    e1: float

    def __post_init__(self) -> None:
        if not all(0 <= p <= 1 for p in (self.e0, self.e1)):
            raise ValueError("Expected directional probabilities")

    @property
    def matrix(self) -> np.ndarray:
        return np.array([[1 - self.e0, self.e1], [self.e0, 1 - self.e1]])

    @property
    def contrast(self) -> float:
        return 1 - self.e0 - self.e1

    @property
    def asymmetry(self) -> float:
        return self.e0 - self.e1

    def invert(
        self, observed: float, max_condition: float = 1e6
    ) -> tuple[float, float]:
        """Unclipped inverse and conditional variance amplification."""
        if not 0 <= observed <= 1 or not 1 <= max_condition < np.inf:
            raise ValueError("Invalid observation or condition limit")
        if np.linalg.cond(self.matrix) > max_condition:
            raise ValueError("Ill-conditioned assignment")
        return (observed - self.e0) / self.contrast, 1 / self.contrast**2


def delta(jacobian: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    j, c = np.atleast_2d(jacobian), np.atleast_2d(covariance)
    if (
        j.ndim != 2
        or not j.size
        or c.shape != (j.shape[1], j.shape[1])
        or not all(np.isfinite(x).all() for x in (j, c))
    ):
        raise ValueError("Incompatible finite Jacobian and covariance required")
    tolerance = 16 * np.finfo(float).eps * len(c) * np.max(np.abs(c))
    if np.max(np.abs(c - c.T)) > tolerance or np.linalg.eigvalsh(c).min() < -tolerance:
        raise ValueError("Covariance must be positive semidefinite and symmetric")
    return j @ c @ j.T


def joint_inverse(
    matrix: np.ndarray, observed: np.ndarray, max_condition: float = 1e6
) -> np.ndarray:
    """Invert a supplied full joint assignment on an explicitly ordered outcome basis."""
    a = np.asarray(matrix, dtype=float)
    q = np.asarray(observed, dtype=float)
    if (
        q.ndim != 1
        or len(q) < 2
        or len(q) & (len(q) - 1)
        or a.shape != (len(q), len(q))
    ):
        raise ValueError("Expected a square assignment on binary joint outcomes")
    if (
        not np.isfinite(a).all()
        or not np.isfinite(q).all()
        or np.any(a < 0)
        or np.any(q < 0)
    ):
        raise ValueError("Expected finite nonnegative probabilities")
    if not np.allclose(a.sum(axis=0), 1, rtol=0, atol=1e-12) or not np.isclose(
        q.sum(), 1, rtol=0, atol=1e-12
    ):
        raise ValueError("Columns and observed distribution must each sum to one")
    if not 1 <= max_condition < np.inf or np.linalg.cond(a) > max_condition:
        raise ValueError("Invalid condition bound or ill-conditioned assignment")
    return np.linalg.solve(a, q)
