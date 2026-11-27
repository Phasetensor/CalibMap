"""Portable records, provider imports and deterministic reports."""
from __future__ import annotations
import csv
import hashlib
import html
import io
import json
from dataclasses import asdict, replace
from datetime import datetime
from typing import Iterable
from . import Record


def normalize(row: Record) -> Record:
    factors={"s":1., "ms":1e-3,"us":1e-6,"µs":1e-6,"ns":1e-9}
    if row.unit not in factors:
        return row
    scale=factors[row.unit]
    return replace(row,unit="s",value=None if row.value is None else row.value*scale,
                   stderr=None if row.stderr is None else row.stderr*scale)


def encode(record: Record) -> dict:
    data=asdict(record)
    for key in ("calibrated","acquired","published"):
        if data[key] is not None:
            data[key]=data[key].isoformat()
    return data


def decode(data: dict) -> Record:
    fields=dict(data)
    fields["qubits"]=tuple(fields["qubits"])
    for key in ("calibrated","acquired","published"):
        if fields.get(key) is not None:
            fields[key]=datetime.fromisoformat(fields[key].replace("Z","+00:00"))
    return Record(**fields)


def export(records: Iterable[Record], fmt: str="json") -> str:
    data=[encode(r) for r in records]
    canonical=json.dumps(data,sort_keys=True,allow_nan=False,separators=(",",":"))
    if fmt=="json":
        return canonical
    if fmt=="html":
        return "<pre>"+html.escape(canonical)+"</pre>"
    if fmt!="csv":
        raise ValueError("Unknown record format")
    stream=io.StringIO()
    writer=csv.DictWriter(stream,fieldnames=list(Record.__dataclass_fields__))
    writer.writeheader()
    for row in data:
        writer.writerow({k:json.dumps(v,allow_nan=False) for k,v in row.items()})
    return stream.getvalue()


def load(text: str, fmt: str="json") -> tuple[Record,...]:
    if fmt=="json":
        rows=json.loads(text)
    elif fmt=="csv":
        rows=[{k:json.loads(v) for k,v in row.items()} for row in csv.DictReader(io.StringIO(text))]
    else:
        raise ValueError("Unsupported input format")
    return tuple(decode(row) for row in rows)


def fingerprint(records: Iterable[Record]) -> str:
    return hashlib.sha256(export(records).encode()).hexdigest()


def ibm_properties(properties, acquired: datetime, published=None) -> tuple[Record,...]:
    """Accept Runtime BackendProperties. The caller supplies actual availability evidence."""
    raw=properties.to_dict()
    rows=[]
    def append(param,qubits,gate):
        stamp=param["date"]
        if isinstance(stamp,str):
            stamp=datetime.fromisoformat(stamp.replace("Z","+00:00"))
        rows.append(normalize(Record(raw["backend_name"],param["name"],tuple(qubits),stamp,acquired,published,
                          param.get("value"),param.get("unit") or "1","IBM Runtime","provider_estimate",gate)))
    for i,params in enumerate(raw["qubits"]):
        for param in params:
            append(param,(i,),None)
    for item in raw["gates"]:
        for param in item["parameters"]:
            append(param,item["qubits"],item["gate"])
    return tuple(rows)
