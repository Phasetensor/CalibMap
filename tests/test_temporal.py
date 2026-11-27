from dataclasses import replace
from datetime import timedelta
from random import Random

import pytest

from calibmap import as_of
from calibmap.history import stability, timelines
from calibmap.planning import readiness
from test_history import HistoryTests as _Fixtures

base = _Fixtures.row
del _Fixtures
day = timedelta(days=1)


def test_future_invariance_and_oracle():
    rng = Random(91)
    for _ in range(100):
        rows = []
        for i in range(20):
            epoch = base.calibrated + i * day
            rows.append(
                replace(
                    base,
                    calibrated=epoch,
                    acquired=epoch + rng.randrange(4) * day,
                    published=epoch + rng.randrange(5) * day,
                    value=i,
                )
            )
        cutoff = base.calibrated + rng.randrange(1, 22) * day
        known = [
            r
            for r in rows
            if all(t <= cutoff for t in (r.acquired, r.calibrated, r.published))
        ]
        rng.shuffle(rows)
        expected = (max(known, key=lambda r: r.calibrated),) if known else ()
        assert as_of(rows, cutoff) == expected == as_of(known, cutoff)


def test_mixed_units_and_protocol():
    later = replace(
        base,
        unit="s",
        value=0.0001,
        calibrated=base.calibrated + day,
        acquired=base.acquired + day,
    )
    other = replace(later, protocol="echo")
    rows = [later, base, other, base]
    assert set(as_of(rows, later.acquired)) == {later, other}
    assert len(timelines(rows, later.acquired)) == 2
    summaries = stability(rows, later.acquired, day * 3, day / 2)
    summary = summaries[base.identity("s")]
    assert summary["epochs"] == 2 and len(summary["gaps"]) == 1
    assert summary["statistics"]["mean"] == pytest.approx(0.00006)
    assert (
        readiness(rows, later.acquired, day, {base.identity("us"): 101})[0] == "READY"
    )


@pytest.mark.parametrize(
    "updates",
    [
        dict(kind="unknown"),
        dict(backend=""),
        dict(qubits=(-1,)),
        dict(qubits=(0, 0)),
        dict(calibrated=None),
        dict(published="invalid"),
        dict(acquired=base.acquired.replace(tzinfo=None)),
        dict(value=float("inf")),
        dict(stderr=-1),
        dict(sample_size=True),
    ],
)
def test_invalid_record(updates):
    with pytest.raises(ValueError):
        replace(base, **updates)
