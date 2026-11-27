"""Seeded simulation under known Gaussian null and independent binomial sampling."""
import json
import resource
import sys
import time
import numpy as np
from scipy.stats import beta,norm
from calibmap.series import segments

rng=np.random.default_rng(4701)
start=time.perf_counter()
n=10000
x=rng.normal(size=(n,40))
t=np.arange(1,41)
critical=norm.isf(3*.05/(np.pi**2*t*t))
false=np.any(abs(x)>critical,axis=1)
x[:,20:]+=4
alarms=np.abs(x[:,20:])>critical[20:]
hits=alarms.any(axis=1)
k=rng.binomial(100,.1,n)
lo=np.where(k==0,0,beta.ppf(.025,k,101-k))
hi=np.where(k==100,1,beta.ppf(.975,k+1,100-k))
def rate(mask):
    p=float(mask.mean())
    return dict(rate=p,monte_carlo_se=float(np.sqrt(p*(1-p)/len(mask))))
cuts=[segments(v,12) for v in x[:200]]
print(json.dumps(dict(seed=4701,replications=n,false_alarm=rate(false),power=rate(hits),
    conditional_delay_mean=float(alarms[hits].argmax(axis=1).mean()),
    readout_coverage=rate((lo<=.1)&(.1<=hi)),readout_rmse=float(np.sqrt(np.mean((k/100-.1)**2))),
    readout_bias=float(np.mean(k/100-.1)),exact_change_only=float(np.mean([c==(20,) for c in cuts])),
    segmentation_replications=len(cuts),seconds=time.perf_counter()-start,
    peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=="darwin" else 1024)),indent=2))
