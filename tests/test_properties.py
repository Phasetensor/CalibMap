from dataclasses import replace
from datetime import UTC, datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from calibmap import Record, as_of


@given(st.lists(st.integers(0, 20), min_size=1, max_size=40), st.integers(0, 20))
def test_no_future_publication_changes_snapshot(epochs, cutoff):
    start = datetime(2025, 1, 1, tzinfo=UTC)
    step = timedelta(hours=1)
    at = start + cutoff * step
    base = Record(
        "fixture", "error", (1,), start, start, None, 0, "1", "generator", "synthetic"
    )
    known = [replace(base, calibrated=start + e * step, value=e) for e in epochs]
    future = [replace(r, published=at + step, value=100) for r in known]
    snapshot = as_of(known, at)
    assert as_of(reversed(future + known), at) == snapshot
    eligible = [r for r in known if r.calibrated <= at]
    assert snapshot == (
        (max(eligible, key=lambda r: r.calibrated),) if eligible else ()
    )
