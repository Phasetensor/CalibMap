"""Grouped revision history and irregular-time diagnostics."""
from __future__ import annotations
from datetime import datetime,timedelta
from typing import Iterable
import numpy as np
from . import Record
from .records import normalize
from .series import describe


def timelines(records: Iterable[Record], at: datetime) -> dict[tuple,tuple[Record,...]]:
    """All available revisions, separate by backend, ordered operands, metric, source and unit."""
    if at.utcoffset() is None:
        raise ValueError("Timezone required")
    groups:dict[tuple,set[Record]]={}
    for item in records:
        r=normalize(item)
        if max(r.calibrated,r.acquired,r.published or r.acquired)>at:
            continue
        key=r.identity(r.unit)
        groups.setdefault(key,set()).add(r)
    return {k:tuple(sorted(v,key=lambda r:(r.calibrated,max(r.acquired,r.published or r.acquired),r.acquired,repr(r)))) for k,v in groups.items()}


def stability(records: Iterable[Record], at: datetime, window: timedelta, gap: timedelta) -> dict:
    """Descriptive dispersion on latest available revisions at distinct physical epochs."""
    if min(window,gap)<=timedelta():
        raise ValueError("Positive windows required")
    result={}
    for key,rows in timelines(records,at).items():
        selected={}
        for r in rows:
            if at-r.calibrated<=window:
                old=selected.get(r.calibrated)
                if old and (old.acquired,old.published)==(r.acquired,r.published) and old!=r:
                    raise ValueError("Conflicting revision")
                selected[r.calibrated]=r
        values=[r.value for r in selected.values() if r.value is not None]
        epochs=list(selected)
        result[key]=dict(epochs=len(epochs),missing=sum(r.value is None for r in selected.values()),
                         age_seconds=(at-rows[-1].calibrated).total_seconds(),
                         gaps=[(a,b) for a,b in zip(epochs,epochs[1:]) if b-a>gap],
                         standard_errors=[r.stderr for r in selected.values()],
                         statistics=describe(np.asarray(values)) if len(values)>=2 else None)
    return result
