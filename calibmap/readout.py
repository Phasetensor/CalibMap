"""Binary assignment with observed rows and prepared columns."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy.stats import beta


def interval(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Equal-tailed Clopper-Pearson interval for independent Bernoulli trials."""
    if type(k) is not int or type(n) is not int or not 0 <= k <= n or n < 1 or not 0 < alpha < 1:
        raise ValueError("Invalid binomial experiment")
    return (float(beta.ppf(alpha / 2, k, n-k+1)) if k else 0.0,
            float(beta.ppf(1-alpha/2, k+1, n-k)) if k < n else 1.0)


@dataclass(frozen=True)
class Binary:
    e0: float
    e1: float

    def __post_init__(self) -> None:
        if not all(0 <= p <= 1 for p in (self.e0, self.e1)):
            raise ValueError("Expected directional probabilities")

    @property
    def matrix(self) -> np.ndarray:
        return np.array([[1-self.e0, self.e1], [self.e0, 1-self.e1]])

    @property
    def contrast(self) -> float:
        return 1-self.e0-self.e1

    @property
    def asymmetry(self) -> float:
        return self.e0-self.e1

    def invert(self, observed: float, max_condition: float = 1e6) -> tuple[float, float]:
        """Unclipped inverse and conditional variance amplification."""
        if not 0 <= observed <= 1 or not 1 <= max_condition < np.inf:
            raise ValueError("Invalid observation or condition limit")
        if np.linalg.cond(self.matrix) > max_condition:
            raise ValueError("Ill-conditioned assignment")
        return (observed-self.e0)/self.contrast, 1/self.contrast**2


def delta(jacobian: np.ndarray, covariance: np.ndarray) -> np.ndarray:
    j, c = np.atleast_2d(jacobian), np.atleast_2d(covariance)
    if c.shape != (j.shape[1], j.shape[1]) or not all(np.isfinite(x).all() for x in (j,c)):
        raise ValueError("Incompatible finite Jacobian and covariance required")
    if not np.allclose(c,c.T) or np.linalg.eigvalsh(c).min() < -1e-12:
        raise ValueError("Covariance must be positive semidefinite and symmetric")
    return j @ c @ j.T
