"""Offline calibration records and publication-aware historical queries."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True)
class Record:
    backend: str
    metric: str
    qubits: tuple[int, ...]
    calibrated: datetime
    acquired: datetime
    published: datetime | None
    value: float | None
    unit: str
    source: str
    kind: str
    gate: str | None = None
    stderr: float | None = None
    sample_size: int | None = None

    protocol: str | None = None

    def identity(self, unit: str) -> tuple:
        key = (
            self.backend,
            self.metric,
            self.qubits,
            self.gate,
            unit,
            self.source,
            self.kind,
        )
        return key if self.protocol is None else (*key, self.protocol)

    def __post_init__(self) -> None:
        if not all(
            isinstance(v, str) and v.strip()
            for v in (self.backend, self.metric, self.source, self.unit)
        ):
            raise ValueError("Backend, metric, source and unit are required")
        if self.kind not in {"measured", "provider_estimate", "simulated", "synthetic"}:
            raise ValueError("Unknown evidence kind")
        if (
            not isinstance(self.qubits, tuple)
            or len(set(self.qubits)) != len(self.qubits)
            or any(type(q) is not int or q < 0 for q in self.qubits)
        ):
            raise ValueError("Expected distinct nonnegative physical qubits")
        if not all(isinstance(v, datetime) for v in (self.acquired, self.calibrated)):
            raise ValueError("Calibration and acquisition timestamps required")
        for timestamp in (self.calibrated, self.acquired, self.published):
            if timestamp is not None and (
                not isinstance(timestamp, datetime) or timestamp.utcoffset() is None
            ):
                raise ValueError("Expected timezone-aware timestamp")
        if self.value is not None and not isfinite(self.value):
            raise ValueError("Expected finite value or missing observation")
        if self.stderr is not None and (not isfinite(self.stderr) or self.stderr < 0):
            raise ValueError("Invalid standard error")
        if self.sample_size is not None and (
            type(self.sample_size) is not int or self.sample_size < 1
        ):
            raise ValueError("Invalid sample size")


def as_of(records: Iterable[Record], at: datetime) -> tuple[Record, ...]:
    """Return latest observations available to the collector by the cutoff."""
    if at.utcoffset() is None:
        raise ValueError("Expected timezone-aware cutoff")
    from .records import normalize

    latest: dict[tuple, tuple[tuple, set[Record]]] = {}
    for row in records:
        available = max(row.calibrated, row.acquired, row.published or row.acquired)
        if available > at:
            continue
        key = row.identity(normalize(row).unit)
        rank = (row.calibrated, available, row.acquired)
        if key not in latest or rank > latest[key][0]:
            latest[key] = (rank, {row})
        elif rank == latest[key][0]:
            latest[key][1].add(row)
    snapshot = []
    for key in sorted(latest, key=repr):
        rows = latest[key][1]
        if len(rows) == 1:
            snapshot.append(next(iter(rows)))
            continue
        equivalents = {normalize(row) for row in rows}
        if len(equivalents) != 1:
            raise ValueError("Conflicting observations at identical priority")
        snapshot.append(equivalents.pop())
    return tuple(snapshot)
