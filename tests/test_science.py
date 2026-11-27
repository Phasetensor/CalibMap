from datetime import timedelta
from itertools import combinations
import numpy as np
import pytest
from calibmap.records import load, export, normalize, fingerprint, ibm_properties
from calibmap.series import segments, decay, correlation, describe, monitor
from calibmap.readout import Binary, delta, interval
from calibmap.planning import forecast, readiness, shortest_path, goodness
from test_history import HistoryTests as _Fixtures

row = _Fixtures.row
del _Fixtures


@pytest.mark.parametrize("fmt", ["json", "csv"])
def test_round_trip(fmt):
    assert load(export([row], fmt), fmt) == (row,)
    assert fingerprint([row]) == fingerprint(load(export([row])))
    assert normalize(row).value == pytest.approx(20e-6)


def test_exhaustive_partition():
    rng = np.random.default_rng(25)
    for n in range(2, 10):
        x = rng.normal(size=n)

        def objective(cuts):
            groups = np.split(x, cuts)
            return sum(((g - g.mean()) ** 2).sum() for g in groups) + 0.5 * len(cuts)

        candidates = [
            c
            for k in range(n)
            for c in combinations(range(1, n), k)
            if min(np.diff((0,) + c + (n,))) >= 2
        ]
        assert objective(segments(x, 0.5)) == pytest.approx(
            min(map(objective, candidates))
        )


def test_formulas():
    r = Binary(0.1, 0.3)
    y = (r.matrix @ np.array([0.65, 0.35]))[1]
    assert r.invert(y) == pytest.approx((0.35, 1 / 0.6**2))
    assert r.asymmetry == pytest.approx(-0.2)
    assert interval(0, 10)[1] == pytest.approx(1 - 0.025**0.1)
    assert delta(np.array([1, 2]), np.array([[1, 0.5], [0.5, 2]])).item() == 11
    t = np.linspace(0, 10, 22)
    assert decay(t, 2 * np.exp(-t / 3) + 0.2) == pytest.approx((2, 3, 0.2), rel=1e-6)
    assert describe(np.array([1, 2, 3]))["variance"] == 1
    assert monitor(np.array([0.0, 10.0]), 0, 1).tolist() == [False, True]
    assert correlation({0: 1, 2: 3, 3: 4}, {1: 2, 3: 4, 4: 5}, 1)[
        "pearson"
    ] == pytest.approx(1)


def test_planning():
    assert shortest_path({(1, 2): 3, (1, 3): 1, (3, 2): 1}, 1, 2) == (2, (1, 3, 2))
    assert goodness(np.array([50, 50]), np.array([0.5, 0.5]))["p_value"] == 1
    assert goodness(np.array([1, 9]), np.array([0.0, 1.0]))["impossible"]
    m, lower, upper = forecast(np.array([1, 3, 6]), np.ones(3), 2, 0.1, 1)
    assert lower < m == 1 < upper
    key = (
        row.backend,
        row.metric,
        row.qubits,
        row.gate,
        row.unit,
        row.source,
        row.kind,
    )
    for records, age, limit, expected in [
        ([row], 1, 20, "READY"),
        ([], 1, 20, "UNKNOWN"),
        ([row], 0, 20, "NOT_READY"),
        ([row], 2, 19, "NOT_READY"),
    ]:
        assert (
            readiness(
                records,
                row.acquired + timedelta(days=1),
                timedelta(days=age),
                {key: limit},
            )[0]
            == expected
        )


def test_adapter():
    class Properties:
        def to_dict(self):
            p = dict(name="T1", date=row.calibrated.isoformat(), unit="us", value=20)
            return dict(
                backend_name="synthetic",
                qubits=[[p]],
                gates=[
                    dict(
                        gate="cx",
                        qubits=[1, 0],
                        parameters=[dict(p, name="gate_length")],
                    )
                ],
            )

    a, b = ibm_properties(Properties(), row.acquired)
    assert a.value == pytest.approx(20e-6)
    assert b.qubits == (1, 0) and b.gate == "cx"


@pytest.mark.parametrize(
    "call",
    [
        lambda: Binary(1.1, 0),
        lambda: Binary(0.4, 0.6).invert(0.2),
        lambda: interval(2, 1),
        lambda: delta(np.ones(2), np.diag([1, -1])),
        lambda: forecast([0, 0], [1, 2], 1, 0, 1),
        lambda: segments([], 1),
        lambda: segments([1], -1),
        lambda: decay([0, 1, 2, 3], [1] * 4),
        lambda: shortest_path({}, 1, 2),
        lambda: shortest_path({(1, 2): -1}, 1, 2),
        lambda: goodness([1, 2], [0.1, 0.1]),
        lambda: correlation({}, {}),
        lambda: monitor([1], 0, 0),
        lambda: load("", "html"),
        lambda: export([], "pdf"),
    ],
)
def test_invalid(call):
    with pytest.raises(ValueError):
        call()
