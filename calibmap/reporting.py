"""Deterministic reports over calibration inputs and declared analysis results."""

from __future__ import annotations
import csv
from dataclasses import dataclass
import html
import io
import json
import math
from typing import Iterable, Mapping
import numpy as np
from . import Record
from .records import encode, fingerprint


def _portable(value):
    if isinstance(value, np.ndarray):
        return _portable(value.tolist())
    if isinstance(value, np.generic):
        return _portable(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return {"undefined": str(value)}
    if isinstance(value, Mapping):
        if not all(isinstance(k, str) for k in value):
            raise ValueError("Report fields require explicit string labels")
        return {k: _portable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_portable(v) for v in value]
    return value


@dataclass(frozen=True)
class Report:
    """Canonical JSON fixes the report at creation time."""

    canonical: str

    @classmethod
    def create(
        cls,
        records: Iterable[Record],
        *,
        definitions: Mapping,
        assumptions: Iterable[str],
        results: Mapping,
        missing: Iterable[str],
        parameters: Mapping,
    ) -> Report:
        rows = tuple(records)
        data = dict(
            version="0.1.0.dev0",
            backends=sorted({r.backend for r in rows}),
            records=[encode(r) for r in rows],
            input_sha256=fingerprint(rows),
            definitions=definitions,
            assumptions=list(assumptions),
            results=results,
            missing=list(missing),
            parameters=parameters,
        )
        return cls(
            json.dumps(
                _portable(data), allow_nan=False, sort_keys=True, separators=(",", ":")
            )
        )

    def render(self, fmt: str) -> str:
        if fmt == "json":
            return self.canonical
        if fmt == "html":
            return (
                "<article><h1>Calibration report</h1><pre>"
                + html.escape(self.canonical)
                + "</pre></article>"
            )
        if fmt != "csv":
            raise ValueError("Report format must be json, csv or html")
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["section", "json_value"])
        for key, value in json.loads(self.canonical).items():
            writer.writerow([key, json.dumps(value, allow_nan=False, sort_keys=True)])
        return stream.getvalue()
