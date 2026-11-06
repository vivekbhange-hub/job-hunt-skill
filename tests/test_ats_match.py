import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from _load import load_script

ats = load_script("jobhunt-resume", "ats_match.py")

POSTING = """
Operations Manager
We are seeking an operations manager with strong vendor management experience.
- Own vendor management and supplier contracts across 3 warehouses
- Build dashboards for inventory forecasting
- Inventory forecasting with Excel and SQL
- Lead a team of 12 and report to the COO
Nice to have: Lean Six Sigma certification.
"""

RESUME = """
Operations Lead, Northwind Logistics (2019-2024)
- Ran vendor management for 40 suppliers; cut late deliveries 18%
- Built inventory dashboards in Excel used by 3 site managers
- Managed a crew of 9; responsible for scheduling
- Responsible for safety audits. Responsible for training.
- Excel reporting, Excel macros, Excel models, Excel pivot tables
"""


class TokenizeTests(unittest.TestCase):
    def test_folds_plurals_both_sides(self):
        self.assertEqual(ats.fold("dashboards"), "dashboard")
        self.assertEqual(ats.fold("supplies"), "supply")
        self.assertEqual(ats.fold("processes"), "process")
        self.assertEqual(ats.fold("analysis"), "analysis")
        self.assertEqual(ats.fold("sales"), "sales")
        self.assertEqual(ats.fold("acls"), "acls")  # short tokens are left alone

    def test_keeps_symbol_terms(self):
        tokens = [t for seg in ats.tokenize_segments("Skills: C++, C#, Node.js and CI/CD.") for t in seg]
        for term in ("c++", "c#", "node.js", "ci/cd"):
            self.assertIn(term, tokens)

    def test_bigrams_do_not_cross_lines(self):
        _, bigrams = ats.count_terms("vendor management\nsupplier contracts")
        self.assertIn("vendor management", bigrams)
        self.assertIn("supplier contract", bigrams)
        self.assertNotIn("management supplier", bigrams)

    def test_spaced_dash_splits_phrases(self):
        _, bigrams = ats.count_terms("Registered Nurse - ICU")
        self.assertIn("registered nurse", bigrams)
        self.assertNotIn("nurse icu", bigrams)

    def test_stopwords_and_numbers_dropped(self):
        unigrams, _ = ats.count_terms("The ideal candidate has 5 years (2+ preferred) of experience with the budget")
        self.assertEqual(set(unigrams), {"budget"})
        self.assertNotIn("the", unigrams)
        self.assertNotIn("5", unigrams)
        self.assertNotIn("experience", unigrams)


class AnalyzeTests(unittest.TestCase):
    def setUp(self):
        self.result = ats.analyze(POSTING, RESUME, top=40, overuse=4)
        self.matched = {m["term"] for m in self.result["matched"]}
        self.missing = {m["term"] for m in self.result["missing"]}

    def test_matched_and_missing(self):
        self.assertIn("vendor management", self.matched)
        self.assertIn("dashboard", self.matched)
        self.assertIn("excel", self.matched)
        self.assertIn("sql", self.missing)
        self.assertIn("lean", self.missing)
        self.assertTrue(self.matched.isdisjoint(self.missing))

    def test_coverage_math(self):
        r = self.result
        expected = round(100.0 * len(r["matched"]) / r["terms_checked"], 1)
        self.assertEqual(r["coverage_pct"], expected)
        self.assertGreater(r["coverage_pct"], 0)
        self.assertLess(r["coverage_pct"], 100)

    def test_ranked_by_weight_then_alpha(self):
        terms = ats.top_terms(POSTING, top=50)
        keys = [(-s, t) for t, s in terms]
        self.assertEqual(keys, sorted(keys))
        # Phrases seen twice score 4 and outrank single words; ties sort alphabetically.
        self.assertEqual(terms[0], ("inventory forecasting", 4))
        self.assertIn(("vendor management", 4), terms[:3])
        self.assertNotIn("nice", dict(terms))

    def test_overused_and_cliches(self):
        over = {o["word"]: o["count"] for o in self.result["overused"]}
        self.assertEqual(over.get("excel"), 5)
        cliches = {c["phrase"]: c["count"] for c in self.result["cliches"]}
        self.assertEqual(cliches.get("responsible for"), 3)

    def test_deterministic(self):
        self.assertEqual(ats.analyze(POSTING, RESUME), ats.analyze(POSTING, RESUME))

    def test_empty_posting(self):
        r = ats.analyze("", RESUME)
        self.assertEqual(r["terms_checked"], 0)
        self.assertEqual(r["coverage_pct"], 0.0)

    def test_markdown_frames_missing_as_gaps(self):
        md = ats.to_markdown(self.result)
        self.assertIn("## Missing from the resume", md)
        self.assertIn("it is a gap", md)
        self.assertIn("- sql", md)


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ats.main(list(args))
        return code, out.getvalue()

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "posting.txt"
            r = Path(tmp) / "resume.md"
            p.write_text(POSTING, encoding="utf-8")
            r.write_text(RESUME, encoding="utf-8")
            code, out = self.run_cli("--posting", str(p), "--resume", str(r), "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("coverage_pct", data)
        self.assertIn("missing", data)

    def test_missing_file_returns_error(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code, _ = self.run_cli("--posting", "nope-does-not-exist.txt", "--resume", "also-missing.txt")
        self.assertEqual(code, 2)
        self.assertIn("error", err.getvalue())

    def test_both_stdin_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                ats.main(["--posting", "-", "--resume", "-"])


if __name__ == "__main__":
    unittest.main()
