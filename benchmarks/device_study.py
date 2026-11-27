"""Seeded offline device diagnostics. All measurements in this study are synthetic."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from calibmap import Record
from calibmap.diagnostics import dependence
from calibmap.experiment import Criterion, evaluate
from calibmap.history import stability
from calibmap.planning import forecast, shortest_path
from calibmap.readout import Binary
from calibmap.series import decay_diagnostics, monitor, segments

rng = np.random.default_rng(138)
t = np.cumsum(rng.integers(1,4,40))
x = rng.normal(0,1,len(t))
x[20:] += 4
base = datetime(2025,1,1,tzinfo=timezone.utc)
rows=[]
for i,(dt,y) in enumerate(zip(t,x)):
    stamp=base+timedelta(hours=int(dt))
    rows.append(Record("fixture","gate_error",(0,1),stamp,stamp,None,.02+.002*y,"1","fixture","synthetic","cx"))
latest=rows[-1]
key=latest.identity("1")
rolling=[stability(rows,r.acquired,timedelta(hours=15),timedelta(hours=5))[key]["statistics"] for r in rows]
fig,axes=plt.subplots(3,3,figsize=(12,9),layout="constrained")
ax=axes.flat
ax[0].plot(t,[r.value for r in rows],".-")
ax[0].set(title="Directed CX error timeline",xlabel="Hours")
ax[1].plot(t,[s["mad"] if s else np.nan for s in rolling])
ax[1].set(title="15-hour rolling MAD",xlabel="Hours")
ax[2].hist([r.value for r in rows],bins=9)
ax[2].set(title="Gate error estimates",ylabel="Count")
im=ax[3].imshow(Binary(.07,.13).matrix,vmin=0,vmax=1)
fig.colorbar(im,ax=ax[3])
ax[3].set(title="Assignment probability",xlabel="Prepared",ylabel="Observed")
delay=np.linspace(0,60,50)
signal=.78*np.exp(-delay/18)+.12+rng.normal(0,.01,len(delay))
fit=decay_diagnostics(delay,signal)
a,tau,b=fit["parameters"]
ax[4].scatter(delay,signal,s=8)
ax[4].plot(delay,a*np.exp(-delay/tau)+b)
ax[4].set(title="Synthetic relaxation",xlabel="Delay (µs)")
ax[5].plot(t,x)
alarms=monitor(x,0,1)
ax[5].scatter(t[alarms],x[alarms],marker="x",label="Alarm")
for boundary in segments(x,12):
    ax[5].axvline(t[boundary],linestyle="--")
ax[5].set(title="Online alarms and offline boundaries",xlabel="Hours")
pair=dependence({"A":dict(zip(t,x)),"B":dict(zip(t,x+rng.normal(size=len(t))))})
sd=np.sqrt(np.diag(pair["covariance"]))
ax[6].imshow(pair["covariance"]/np.outer(sd,sd),vmin=-1,vmax=1,cmap="coolwarm")
ax[6].set(title="Aligned correlation",xticks=[0,1],xticklabels=pair["labels"])
edges={(0,1):.1,(1,2):.1,(0,2):.4}
_,path=shortest_path(edges,0,2)
positions=np.array([[0,0],[1,1],[2,0]])
for u,v in edges:
    ax[7].annotate("",xy=positions[v],xytext=positions[u],arrowprops={"arrowstyle":"->","color":"green" if (u,v) in zip(path,path[1:]) else "gray"})
for i,(xx,yy) in enumerate(positions):
    ax[7].text(xx,yy,str(i))
ax[7].set(title="Minimum calibrated path",xlim=(-.2,2.2),ylim=(-.2,1.2))
pred=[forecast(t[:i],x[:i],t[i]-t[i-1],.1,1) for i in range(5,len(x))]
mean,low,high=np.array(pred).T
ax[8].plot(t[5:],x[5:],".",label="Held out")
ax[8].plot(t[5:],mean)
ax[8].fill_between(t[5:],low,high,alpha=.25)
ax[8].set(title="Future observation intervals",xlabel="Hours")
result=evaluate(rows,latest.acquired,timedelta(days=1),[Criterion(key,upper=.03)])
fig.suptitle(f"Synthetic device diagnostics | Readiness for error ≤ 0.03: {result.status}")
fig.savefig(Path(__file__).with_name("device-study.svg"),metadata={"Date":None})
