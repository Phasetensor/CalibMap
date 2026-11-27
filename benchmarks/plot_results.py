"""Render the recorded simulation results without rerunning random experiments."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parent
data = json.loads((root / "scenarios.json").read_text())
fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout="constrained")
scenarios = list(data["drift"])
rates = [data["drift"][s]["conditional_detection"] for s in scenarios]
axes[0].bar(scenarios, rates, color="#276681")
axes[0].set(title="Detection among surviving paths", ylabel="Probability", ylim=(0, 1.06))
axes[0].tick_params(axis="x", rotation=30)
regimes = list(data["forecast"])
x = np.arange(len(regimes))
for i, method in enumerate(("last", "mean5", "ewma", "local_level")):
    axes[1].bar(x + (i - 1.5) * 0.18, [data["forecast"][s][method]["rmse"] for s in regimes], 0.18, label=method)
axes[1].set(xticks=x, xticklabels=regimes, title="Forward prediction", ylabel="RMSE")
axes[1].legend(fontsize=7)
methods = ["known_variance", "delta", "mc"]
axes[2].bar(["Known", "Delta", "Monte Carlo"], [data["readout"][s] * 1e6 for s in methods], color="#497a61")
axes[2].set(title="Readout correction variance", ylabel="Variance × 1,000,000")
fig.suptitle("CalibMap | Synthetic calibration studies")
fig.savefig(root / "study-results.svg", metadata={"Date": None})
