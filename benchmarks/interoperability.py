"""Synthetic independent calibration, planning and held-out Z comparison."""
import json
import numpy as np
from bornlens import Sample,compare
from shotweave import Readout,optimal_allocation
from calibmap.readout import Binary,interval

rng=np.random.default_rng(512)
channels=[Binary(.03,.06),Binary(.19,.12)]
weights=[]
calibration=[]
for q,channel in enumerate(channels):
    counts=[int(rng.binomial(3000,p)) for p in (channel.e0,channel.e1)]
    fitted=Binary(*(x/3000 for x in counts))
    _,amplification=fitted.invert(.5)
    _,conditional=Readout(fitted.e0,fitted.e1).correct(.5,.25)
    np.testing.assert_allclose(conditional,.25*amplification)
    weights.append(np.sqrt(conditional))
    calibration.append(dict(qubit=q,counts=counts,simultaneous_intervals=[interval(x,3000,.05/4) for x in counts]))
allocation=optimal_allocation(10000,weights)
assert sum(allocation)==10000
out=[]
for q,(channel,n) in enumerate(zip(channels,allocation)):
    observed=channel.e0+channel.contrast*.4
    a,b=rng.binomial(n,observed,size=2)
    label=("IZ","ZI")[q]
    comparison=compare(Sample(label,n-int(a),int(a)),Sample(label,n-int(b),int(b)),tolerance=.12,confidence=.975)
    out.append(comparison.verdict)
print(json.dumps(dict(seed=512,evidence="synthetic",physical_qubits=[0,1],allocation=allocation,calibration=calibration,held_out_observed_Z=out),indent=2))
