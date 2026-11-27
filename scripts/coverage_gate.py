import json
from pathlib import Path

totals = json.loads(Path("coverage.json").read_text())["totals"]
statements = totals["covered_lines"] / totals["num_statements"]
branches = totals["covered_branches"] / totals["num_branches"]
print(f"Statement {statements:.2%}, branch {branches:.2%}")
if statements < 0.95 or branches < 0.90:
    raise SystemExit(1)
