from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest import TestCase

from calibmap import Record, as_of


class HistoryTests(TestCase):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    row = Record(
        "fixture", "T1", (0,), now, now, None, 20, "us", "fixture", "simulated"
    )

    def test_cutoff(self):
        future = self.now + timedelta(days=1)
        self.assertEqual(
            as_of([self.row, replace(self.row, published=future)], self.now),
            (self.row,),
        )

    def test_conflict(self):
        with self.assertRaises(ValueError):
            as_of([self.row, replace(self.row, value=30)], self.now)

    def test_ordered_gates(self):
        rows = [replace(self.row, gate="cx", qubits=q) for q in [(0, 1), (1, 0)]]
        self.assertEqual(set(as_of(rows, self.now)), set(rows))

    def test_unknown(self):
        row = replace(self.row, value=None)
        self.assertIsNone(as_of([row], self.now)[0].value)
