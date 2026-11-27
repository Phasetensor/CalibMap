"""Pairwise dependence and gate-specific connectivity diagnostics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import combinations

import numpy as np
from scipy.stats import pearsonr


def dependence(series: Mapping[str, Mapping[float, float]]) -> dict:
    """Exact-time pairwise deletion. Holm p-values assume valid individual Pearson tests."""
    labels = sorted(series)
    n = len(labels)
    if not n:
        raise ValueError("At least one series required")
    covariance = np.full((n, n), np.nan)
    overlap = np.zeros((n, n), dtype=int)
    tests = []
    for i, a in enumerate(labels):
        for j in range(i, n):
            b = labels[j]
            times = sorted(series[a].keys() & series[b].keys())
            pairs = [
                (series[a][t], series[b][t])
                for t in times
                if np.isfinite([series[a][t], series[b][t]]).all()
            ]
            overlap[i, j] = overlap[j, i] = len(pairs)
            if len(pairs) < 2:
                continue
            x, y = np.asarray(pairs).T
            covariance[i, j] = covariance[j, i] = np.cov(x, y)[0, 1]
            if i != j and len(x) >= 3 and min(np.ptp(x), np.ptp(y)) > 0:
                tests.append((float(pearsonr(x, y)[1]), a, b))
    adjusted = {}
    previous = 0.0
    for k, (p, a, b) in enumerate(sorted(tests)):
        previous = min(1.0, max(previous, (n * (n - 1) // 2 - k) * p))
        adjusted[a, b] = previous
    psd = None
    if np.isfinite(covariance).all():
        tolerance = 16 * np.finfo(float).eps * n * np.max(abs(covariance))
        psd = bool(np.linalg.eigvalsh(covariance).min() >= -tolerance)
    return {
        "labels": labels,
        "covariance": covariance,
        "overlap": overlap,
        "psd": psd,
        "holm": adjusted,
    }


def components(
    nodes: Iterable[int], edges: Iterable[tuple[int, int]]
) -> tuple[tuple[int, ...], ...]:
    """Weak components of a directed coupling graph, including isolated qubits."""
    adjacent: dict[int, set[int]] = {node: set() for node in nodes}
    for a, b in edges:
        if a not in adjacent or b not in adjacent:
            raise ValueError("Edge endpoint absent from device")
        adjacent[a].add(b)
        adjacent[b].add(a)
    pending = set(adjacent)
    result = []
    while pending:
        stack = [min(pending)]
        found = set()
        while stack:
            node = stack.pop()
            if node not in found:
                found.add(node)
                stack.extend(adjacent[node] - found)
        pending -= found
        result.append(tuple(sorted(found)))
    return tuple(result)


def candidates(nodes: Iterable[int], edges: Iterable[tuple[int, int]], size: int):
    """Enumerate weakly connected subsets. Intended for small device regions."""
    physical = tuple(sorted(set(nodes)))
    links = tuple(edges)
    if type(size) is not int or not 1 <= size <= len(physical):
        raise ValueError("Invalid candidate size")
    components(physical, links)
    for group in combinations(physical, size):
        subset = [(a, b) for a, b in links if a in group and b in group]
        if len(components(group, subset)) == 1:
            yield group
