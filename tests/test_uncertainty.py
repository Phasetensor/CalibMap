from itertools import product

import numpy as np
import pytest
from scipy.stats import beta

from calibmap.readout import Binary, delta
from calibmap.uncertainty import corrected_variance, independent_assignment, posterior, propagate


def correct(x):
    q, e0, e1 = x
    return (q - e0) / (1 - e0 - e1)


def test_correction_gradient_against_central_differences():
    point = np.array([.44, .12, .21])
    basis = np.eye(3) * 1e-6
    grad = np.array([(correct(point + d) - correct(point - d)) / 2e-6 for d in basis])
    cov = np.array([[3., 1., -.2], [1., 2., .6], [-.2, .6, 1.]]) * 1e-6
    estimate = corrected_variance(point[0], Binary(*point[1:]), cov)
    assert estimate == pytest.approx(grad @ cov @ grad, rel=1e-9)
    draws = propagate(correct, point, cov, 10000, 47)
    assert draws.var(ddof=1) == pytest.approx(estimate, rel=.05)


@pytest.mark.parametrize("k,n", [(0, 1), (1, 1), (4, 10), (100, 1000)])
def test_beta_posterior(k, n):
    result = posterior(k, n, (2, 3))
    a, b = result["shape"]
    assert result["mean"] == pytest.approx(beta.mean(a, b))
    assert beta.cdf(result["credible"], a, b) == pytest.approx([.025, .975])


def test_tensor_assignments_against_enumeration():
    models = (Binary(.1, .3), Binary(.05, .15))
    matrix = independent_assignment(models)
    states = tuple(product(range(2), repeat=2))
    for i, obs in enumerate(states):
        for j, prep in enumerate(states):
            assert matrix[i,j] == pytest.approx(np.prod([m.matrix[o,p] for m,o,p in zip(models,obs,prep)]))


@pytest.mark.parametrize("fn", [
    lambda: posterior(0, 1, (0, 1)), lambda: independent_assignment(()),
    lambda: propagate(sum, [0], [[1]], 1, 2),
    lambda: delta([[1]], [[-1e-15]]),
    lambda: delta([[1]], [[np.nan]]),
    lambda: delta([[1]], [[1,2],[2,1]]),
    lambda: delta([], np.empty((0,0))),
    lambda: corrected_variance(.3, Binary(.4,.6), np.eye(3)),
])
def test_invalid(fn):
    with pytest.raises(ValueError):
        fn()


def test_unclipped_inverse_and_negative_contrast():
    assert Binary(.2, .2).invert(.1)[0] < 0
    assert Binary(.8, .7).invert(.55)[0] == pytest.approx(.5)
