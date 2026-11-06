import contextlib
import csv
import datetime as dt
import io
import json
import tempfile
import unittest
from pathlib import Path

from _load import load_script

tr = load_script("jobhunt-tracker", "tracker.py")

TODAY = dt.date(2026, 11, 7)


class CoreTests(unittest.TestCase):
    def test_add_assigns_ids_and_dates(self):
        rows = []
        a = tr.add(rows, "Acme", "Analyst", TODAY)
        b = tr.add(rows, "Beta", "Lead", TODAY, stage="saved")
        self.assertEqual((a["id"], b["id"]), ("1", "2"))
        self.assertEqual(a["applied_date"], "2026-11-07")
        self.assertEqual(b["applied_date"], "")

    def test_add_validation(self):
        with self.assertRaises(tr.TrackerError):
            tr.add([], "Acme", "Analyst", TODAY, stage="dreaming")
        with self.assertRaises(tr.TrackerError):
            tr.add([], " ", "Analyst", TODAY)
        with self.assertRaises(tr.TrackerError):
            tr.add([], "Acme", "Analyst", TODAY, applied="07/11/2026")

    def test_update_tracks_furthest_stage(self):
        rows = []
        tr.add(rows, "Acme", "Analyst", TODAY, applied="2026-10-01")
        tr.update(rows, "1", TODAY, stage="interview")
        row = tr.update(rows, "1", TODAY, stage="rejected", append_note="no feedback")
        self.assertEqual(row["stage"], "rejected")
        self.assertEqual(row["furthest_stage"], "interview")
        self.assertEqual(row["last_contact"], "2026-11-07")
        self.assertIn("2026-11-07: no feedback", row["notes"])

    def test_saved_then_rejected_counts_as_sent(self):
        rows = []
        tr.add(rows, "Acme", "Analyst", TODAY, stage="saved")
        row = tr.update(rows, "1", TODAY, stage="ghosted")
        self.assertEqual(row["furthest_stage"], "applied")
        self.assertEqual(row["applied_date"], "2026-11-07")

    def test_update_unknown_id(self):
        with self.assertRaises(tr.TrackerError):
            tr.update([], "9", TODAY, stage="screen")

    def test_stats(self):
        rows = []
        tr.add(rows, "A", "r", TODAY, applied="2026-10-01")             # applied, quiet 37 days
        tr.add(rows, "B", "r", TODAY, applied="2026-11-01")             # applied, quiet 6 days
        tr.add(rows, "C", "r", TODAY, applied="2026-10-01")
        tr.update(rows, "3", TODAY, stage="interview", last_contact="2026-10-20")  # quiet 18
        tr.add(rows, "D", "r", TODAY, applied="2026-10-01")
        tr.update(rows, "4", TODAY, stage="rejected")
        tr.add(rows, "E", "r", TODAY, stage="saved")
        s = tr.stats(rows, TODAY, stale_days=10)
        self.assertEqual(s["total"], 5)
        self.assertEqual(s["sent"], 4)
        self.assertEqual(s["responses"], 2)  # interview + rejected
        self.assertEqual(s["response_rate_pct"], 50.0)
        self.assertEqual(s["funnel"]["applied"], 4)
        self.assertEqual(s["funnel"]["screen"], 1)
        self.assertEqual(s["funnel"]["interview"], 1)
        self.assertEqual(s["funnel"]["offer"], 0)
        self.assertEqual([r["company"] for r in s["stale"]], ["A", "C"])
        self.assertEqual(s["stale"][0]["days_quiet"], 37)
        md = tr.stats_markdown(s)
        self.assertIn("Response rate: 50.0%", md)
        self.assertIn("Needs a follow-up", md)

    def test_stats_empty(self):
        s = tr.stats([], TODAY)
        self.assertEqual(s["response_rate_pct"], 0.0)
        self.assertEqual(s["stale"], [])

    def test_markdown_escapes_pipes(self):
        out = tr.table([{"company": "A|B", "role": "x\ny"}], ["company", "role"])
        self.assertIn("A\\|B", out)
        self.assertIn("x y", out)


class FileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = str(Path(self.tmp.name) / "jobhunt" / "applications.csv")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = tr.main(["--file", self.file, "--today", "2026-11-07", *args])
        return code, out.getvalue(), err.getvalue()

    def test_round_trip(self):
        self.assertEqual(self.cli("add", "--company", "Acme, Inc.", "--role", "Nurse", "--notes", 'said "soon"')[0], 0)
        self.assertEqual(self.cli("update", "1", "--stage", "screen")[0], 0)
        with open(self.file, encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(list(rows[0].keys()), tr.COLUMNS)
        self.assertEqual(rows[0]["company"], "Acme, Inc.")
        self.assertEqual(rows[0]["notes"], 'said "soon"')
        self.assertEqual(rows[0]["stage"], "screen")
        leftovers = [p.name for p in Path(self.file).parent.iterdir() if p.suffix == ".tmp"]
        self.assertEqual(leftovers, [])

    def test_list_and_stats_json(self):
        self.cli("add", "--company", "Acme", "--role", "Teacher", "--applied", "2026-10-01")
        self.cli("add", "--company", "Beta", "--role", "Teacher", "--stage", "saved")
        code, out, _ = self.cli("list", "--active", "--json")
        self.assertEqual(code, 0)
        self.assertEqual([r["company"] for r in json.loads(out)], ["Acme"])
        code, out, _ = self.cli("stats", "--json")
        data = json.loads(out)
        self.assertEqual(data["stale"][0]["company"], "Acme")
        code, out, _ = self.cli("list")
        self.assertIn("| id | company |", out)

    def test_errors_return_2(self):
        code, _, err = self.cli("update", "42", "--stage", "offer")
        self.assertEqual(code, 2)
        self.assertIn("no application", err)
        code, _, err = self.cli("list", "--stage", "nope")
        self.assertEqual(code, 2)

    def test_list_empty_file(self):
        code, out, _ = self.cli("list")
        self.assertEqual(code, 0)
        self.assertIn("No applications", out)


if __name__ == "__main__":
    unittest.main()
