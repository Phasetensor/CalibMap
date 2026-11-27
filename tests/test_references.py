from itertools import permutations

import numpy as np
import pytest
from scipy.stats import binomtest, chisquare

from calibmap.planning import goodness, multinomial_mc, shortest_path
from calibmap.series import decay_diagnostics


def test_multinomial_reference():
    observed = np.array([11, 22, 27])
    p = np.array([0.2, 0.3, 0.5])
    assert goodness(observed, p)["p_value"] == pytest.approx(
        chisquare(observed, 60 * p).pvalue
    )
    sparse = multinomial_mc(np.array([1, 7]), np.array([0.5, 0.5]), 10000, 71)
    assert sparse["p_value"] is None
    assert abs(sparse["mc_p"] - binomtest(1, 8).pvalue) < 0.015
    assert multinomial_mc([1, 7], [0, 1], 20, 2)["mc_p"] == 0
    with pytest.raises(ValueError):
        multinomial_mc([1, 7], [0, 1], 0, 2)


def test_paths_against_all_simple_paths():
    rng = np.random.default_rng(107)
    for _ in range(50):
        edges = {
            (a, b): int(rng.integers(0, 6))
            for a, b in permutations(range(4), 2)
            if rng.random() < 0.6
        }
        costs = []
        for n in range(3):
            for via in permutations([1, 2], n):
                path = (0, *via, 3)
                links = list(zip(path, path[1:]))
                if all(link in edges for link in links):
                    costs.append(sum(edges[link] for link in links))
        if costs:
            assert shortest_path(edges, 0, 3)[0] == min(costs)
        else:
            with pytest.raises(ValueError):
                shortest_path(edges, 0, 3)


def test_noisy_decay():
    rng = np.random.default_rng(100)
    t = np.linspace(0, 4, 100)
    y = 0.7 * np.exp(-t / 1.2) + 0.15 + rng.normal(0, 0.003, len(t))
    r = decay_diagnostics(t, y)
    assert r["locally_identifiable"] and abs(r["parameters"][1] - 1.2) < 0.04
    assert 0 < r["stderr"][1] < 0.03
    assert np.mean(r["residuals"]) == pytest.approx(0, abs=1e-7)
