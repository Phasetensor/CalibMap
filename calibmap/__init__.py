"""Offline calibration records and publication-aware historical queries."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable, Optional, Tuple


@dataclass(frozen=True)
class Record:
    backend: str
    metric: str
    qubits: Tuple[int, ...]
    calibrated: datetime
    acquired: datetime
    published: Optional[datetime]
    value: Optional[float]
    unit: str
    source: str
    kind: str
    gate: Optional[str] = None
    stderr: Optional[float] = None
    sample_size: Optional[int] = None

    def __post_init__(self) -> None:
        if not all((self.backend, self.metric, self.source, self.unit)):
            raise ValueError("Backend, metric, source and unit are required")
        if self.kind not in {"measured", "provider_estimate", "simulated"}:
            raise ValueError("Unknown evidence kind")
        if len(set(self.qubits)) != len(self.qubits) or any(
            type(q) is not int or q < 0 for q in self.qubits
        ):
            raise ValueError("Expected distinct nonnegative physical qubits")
        for timestamp in (self.calibrated, self.acquired, self.published):
            if timestamp is not None and timestamp.utcoffset() is None:
                raise ValueError("Expected timezone-aware timestamp")
        if self.value is not None and not isfinite(self.value):
            raise ValueError("Expected finite value or missing observation")
        if self.stderr is not None and (not isfinite(self.stderr) or self.stderr < 0):
            raise ValueError("Invalid standard error")
        if self.sample_size is not None and (
            type(self.sample_size) is not int or self.sample_size < 1
        ):
            raise ValueError("Invalid sample size")


def as_of(records: Iterable[Record], at: datetime) -> Tuple[Record, ...]:
    """Return latest observations available to the collector by the cutoff."""
    if at.utcoffset() is None:
        raise ValueError("Expected timezone-aware cutoff")
    latest = {}
    for row in records:
        available = max(row.calibrated, row.acquired, row.published or row.acquired)
        if available > at:
            continue
        key = (row.backend, row.metric, row.qubits, row.gate, row.unit, row.source, row.kind)
        rank = (row.calibrated, available, row.acquired)
        if key not in latest or rank > latest[key][0]:
            latest[key] = (rank, {row})
        elif rank == latest[key][0]:
            latest[key][1].add(row)
    if any(len(rows) > 1 for _, rows in latest.values()):
        raise ValueError("Conflicting observations at identical priority")
    return tuple(next(iter(latest[key][1])) for key in sorted(latest, key=repr))
