import csv
import io
import json
import numpy as np
import pytest
from calibmap.diagnostics import dependence,components,candidates
from calibmap.reporting import Report


def test_pairwise_covariance_can_be_indefinite():
    s={"a":{0:0,1:1,4:0,5:1},"b":{0:0,1:1,2:0,3:1},"c":{2:0,3:1,4:1,5:0}}
    result=dependence(s)
    assert result["psd"] is False
    assert result["overlap"][0].tolist()==[4,2,2]
    s["d"]={7:3}
    assert dependence(s)["psd"] is None


def test_correlations():
    x=dict(enumerate(range(10)))
    s={"x":x,"y":{k:-v for k,v in x.items()},"constant":{k:1 for k in x}}
    r=dependence(s)
    assert r["holm"]["x","y"] < 1e-10
    assert r["psd"]
    with pytest.raises(ValueError):
        dependence({})


def test_connectivity():
    edges=[(2,1),(2,3)]
    assert components(range(4),edges)==((0,),(1,2,3))
    assert list(candidates(range(4),edges,2))==[(1,2),(2,3)]
    with pytest.raises(ValueError):
        components([1],edges)
    with pytest.raises(ValueError):
        list(candidates([1],[],0))


def test_report_formats():
    args=dict(definitions={},assumptions=["<script>"],missing=[],parameters={"seed":2},
              results={"a":np.array([np.nan,np.inf]),"b":np.float32(2)})
    report=Report.create([],**args)
    data=json.loads(report.render("json"))
    assert data["results"]["a"]==[{"undefined":"nan"},{"undefined":"inf"}]
    assert "<script>" not in report.render("html")
    rows=list(csv.reader(io.StringIO(report.render("csv"))))
    assert {k:json.loads(v) for k,v in rows[1:]}==data
    assert report==Report.create([],**args)
    with pytest.raises(ValueError):
        report.render("txt")
    with pytest.raises(ValueError):
        Report.create([],**dict(args,results={1:2}))
