"""Offline integration against an IBM Runtime object shipped with the fake provider."""

from datetime import datetime, timezone
from importlib.metadata import version

from qiskit_ibm_runtime.fake_provider import FakeAthensV2

from calibmap.records import export, ibm_properties, load

props = FakeAthensV2().properties()
acquired = datetime.now(timezone.utc)
rows = ibm_properties(props, acquired)
assert rows and all(r.published is None and r.acquired == acquired for r in rows)
assert load(export(rows)) == rows
print(version("qiskit-ibm-runtime"), props.backend_name, len(rows), acquired.isoformat())
