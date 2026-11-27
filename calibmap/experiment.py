"""Evidence-level readiness checks for a declared experiment."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta

from . import Record, as_of
from .records import normalize


@dataclass(frozen=True)
class Criterion:
    key: tuple
    lower: float | None = None
    upper: float | None = None
    max_stderr: float | None = None


@dataclass(frozen=True)
class Decision:
    status: str
    checks: tuple[dict, ...]


def evaluate(
    records: Iterable[Record],
    at: datetime,
    age: timedelta,
    criteria: Iterable[Criterion],
    *,
    required_qubits: Iterable[int] = (),
    required_gates: Iterable[tuple] = (),
    device_qubits: set[int] | None = None,
    available_gates: set[tuple] | None = None,
    drift_alarms: set[tuple] | None = None,
    require_drift: bool = False,
) -> Decision:
    """Topology and alarms must describe the device as known at the cutoff. Thresholds use canonical units."""
    from math import isfinite

    if age < timedelta() or at.utcoffset() is None:
        raise ValueError("Invalid cutoff or maximum age")
    rows = tuple(normalize(r) for r in records)
    checks = []

    def add(name, key, expected, actual, stamp, status, reason):
        checks.append(
            {
                "criterion": name,
                "key": key,
                "required": expected,
                "actual": actual,
                "calibrated": stamp.isoformat() if stamp else None,
                "status": status,
                "reason": reason,
            }
        )

    for name, required, known in (
        ("qubit", required_qubits, device_qubits),
        ("gate", required_gates, available_gates),
    ):
        for item in required:
            if known is None:
                add(name, item, True, None, None, "UNKNOWN", "inventory unavailable")
            else:
                present = item in known
                add(
                    name,
                    item,
                    True,
                    present,
                    None,
                    "READY" if present else "NOT_READY",
                    "present" if present else "absent",
                )
    for criterion in criteria:
        key = criterion.key
        if any(
            v is not None and not isfinite(v)
            for v in (criterion.lower, criterion.upper, criterion.max_stderr)
        ):
            raise ValueError("Finite bounds required")
        if (
            criterion.lower is not None
            and criterion.upper is not None
            and criterion.lower > criterion.upper
        ):
            raise ValueError("Reversed bounds")
        if criterion.max_stderr is not None and criterion.max_stderr < 0:
            raise ValueError("Negative standard error bound")
        try:
            matches = as_of((r for r in rows if r.identity(r.unit) == key), at)
        except ValueError:
            add(
                "record",
                key,
                "unique revision",
                None,
                None,
                "UNKNOWN",
                "conflicting revisions",
            )
            continue
        if not matches:
            add(
                "record",
                key,
                "available",
                None,
                None,
                "UNKNOWN",
                "no available observation",
            )
            continue
        r = matches[0]
        for name, value, limit, lower in (
            (
                "age_seconds",
                (at - r.calibrated).total_seconds(),
                age.total_seconds(),
                False,
            ),
            ("lower", r.value, criterion.lower, True),
            ("upper", r.value, criterion.upper, False),
            ("stderr", r.stderr, criterion.max_stderr, False),
        ):
            if limit is None:
                continue
            if value is None:
                add(name, key, limit, None, r.calibrated, "UNKNOWN", "missing value")
            else:
                passed = value >= limit if lower else value <= limit
                add(
                    name,
                    key,
                    limit,
                    value,
                    r.calibrated,
                    "READY" if passed else "NOT_READY",
                    "within bound" if passed else "outside bound",
                )
        if r.value is None:
            add(
                "value",
                key,
                "observed",
                None,
                r.calibrated,
                "UNKNOWN",
                "missing observation",
            )
        if require_drift or drift_alarms is not None:
            alarm = None if drift_alarms is None else key in drift_alarms
            status = "UNKNOWN" if alarm is None else "NOT_READY" if alarm else "READY"
            add(
                "drift",
                key,
                False,
                alarm,
                r.calibrated,
                status,
                "alarm inventory" if alarm is not None else "missing alarm evidence",
            )
    if not checks:
        raise ValueError("At least one criterion required")
    statuses = {c["status"] for c in checks}
    return Decision(
        "NOT_READY"
        if "NOT_READY" in statuses
        else "UNKNOWN"
        if "UNKNOWN" in statuses
        else "READY",
        tuple(checks),
    )
