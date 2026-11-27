"""Grouped revision history and irregular-time diagnostics."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta

import numpy as np

from . import Record
from .records import normalize
from .series import describe


def timelines(
    records: Iterable[Record], at: datetime
) -> dict[tuple, tuple[Record, ...]]:
    """All available revisions, separate by backend, ordered operands, metric, source and unit."""
    if at.utcoffset() is None:
        raise ValueError("Timezone required")
    groups: dict[tuple, set[Record]] = {}
    for item in records:
        r = normalize(item)
        if max(r.calibrated, r.acquired, r.published or r.acquired) > at:
            continue
        key = r.identity(r.unit)
        groups.setdefault(key, set()).add(r)
    return {
        k: tuple(
            sorted(
                v,
                key=lambda r: (
                    r.calibrated,
                    max(r.acquired, r.published or r.acquired),
                    r.acquired,
                    repr(r),
                ),
            )
        )
        for k, v in groups.items()
    }


def stability(
    records: Iterable[Record], at: datetime, window: timedelta, gap: timedelta
) -> dict:
    """Descriptive dispersion on latest available revisions at distinct physical epochs."""
    if min(window, gap) <= timedelta():
        raise ValueError("Positive windows required")
    result = {}
    for key, rows in timelines(records, at).items():
        selected: dict[datetime, Record] = {}
        for r in rows:
            if at - r.calibrated <= window:
                old = selected.get(r.calibrated)
                if (
                    old
                    and (old.acquired, old.published) == (r.acquired, r.published)
                    and old != r
                ):
                    raise ValueError("Conflicting revision")
                selected[r.calibrated] = r
        values = [r.value for r in selected.values() if r.value is not None]
        epochs = list(selected)
        result[key] = {
            "epochs": len(epochs),
            "missing": sum(r.value is None for r in selected.values()),
            "age_seconds": (at - rows[-1].calibrated).total_seconds(),
            "gaps": [(a, b) for a, b in zip(epochs, epochs[1:]) if b - a > gap],
            "standard_errors": [r.stderr for r in selected.values()],
            "statistics": describe(np.asarray(values)) if len(values) >= 2 else None,
        }
    return result


def gate_changes(records: Iterable[Record], earlier: datetime, later: datetime) -> tuple[dict, ...]:
    """Compare matched ordered gates across as-of epochs in canonical units."""
    from . import as_of

    if later < earlier:
        raise ValueError("Reversed epochs")
    rows = tuple(normalize(r) for r in records if r.gate is not None)
    before, after = ({r.identity(r.unit): r for r in as_of(rows, t)} for t in (earlier, later))
    comparisons = []
    for key in sorted(before.keys() | after.keys(), key=repr):
        left, right = before.get(key), after.get(key)
        change = None
        if left and right and left.value is not None and right.value is not None:
            change = right.value - left.value
        comparisons.append({"key": key, "earlier": left, "later": right, "difference": change})
    return tuple(comparisons)
