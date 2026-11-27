from dataclasses import replace
from datetime import timedelta

import pytest

from calibmap.experiment import Criterion, evaluate
from test_history import HistoryTests as _Fixtures

row = _Fixtures.row
del _Fixtures
key=row.identity("s")
day=timedelta(days=1)


def assess(rows,criteria,**kwargs):
    return evaluate(rows,row.acquired,day,criteria,**kwargs)


def test_evidence_and_precedence():
    policy=Criterion(key,lower=1e-6,upper=30e-6,max_stderr=5e-6)
    result=assess([row],[policy],required_gates=[("cx",1,0)],available_gates=set(),require_drift=True)
    assert result.status=="NOT_READY"
    assert {c["status"] for c in result.checks}=={"UNKNOWN","READY","NOT_READY"}
    assert assess([replace(row,stderr=1)],[policy],drift_alarms=set(),required_qubits=[0],device_qubits={0}).status=="READY"
    assert assess([row],[policy],drift_alarms={key}).status=="NOT_READY"
    assert assess([row],[Criterion(key,lower=.1)]).status=="NOT_READY"


@pytest.mark.parametrize("rows", [[],[replace(row,value=None)],[row,replace(row,value=50)]])
def test_unknown(rows):
    assert assess(rows,[Criterion(key,upper=1)],required_qubits=[0]).status=="UNKNOWN"


@pytest.mark.parametrize("criteria", [[],[Criterion(key,lower=2,upper=1)],[Criterion(key,max_stderr=-1)],[Criterion(key,upper=float("inf"))]])
def test_invalid(criteria):
    with pytest.raises(ValueError):
        assess([row],criteria)
