import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from _load import load_script

oc = load_script("jobhunt-negotiate", "offer_compare.py")

OFFERS = [
    {
        "name": "Acme",
        "base": 100000,
        "bonus_pct": 10,
        "equity_value": 40000,
        "vesting_years": 4,
        "cliff_months": 12,
        "signing_bonus": 5000,
        "benefits_value": 6000,
        "remote_days": 2,
        "commute_minutes": 60,
        "commute_cost": 10,
        "pto_days": 20,
    },
    {"name": "Beta", "base": 115000, "remote_days": 5, "pto_days": 25},
]


class VestingTests(unittest.TestCase):
    def test_cliff(self):
        self.assertEqual(oc.vested_fraction(11, 4, 12), 0.0)
        self.assertEqual(oc.vested_fraction(12, 4, 12), 0.25)
        self.assertEqual(oc.vested_fraction(48, 4, 12), 1.0)
        self.assertEqual(oc.vested_fraction(60, 4, 12), 1.0)

    def test_long_cliff_pushes_to_year_two(self):
        o = oc.normalize({"name": "X", "base": 0, "equity_value": 48000, "cliff_months": 18}, 0)
        self.assertEqual(oc.year_breakdown(o, 1)["equity"], 0.0)
        self.assertAlmostEqual(oc.year_breakdown(o, 2)["equity"], 24000.0)
        self.assertAlmostEqual(oc.year_breakdown(o, 3)["equity"], 12000.0)


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.result = oc.compare(OFFERS, years=4)
        self.by_name = {r["name"]: r for r in self.result["offers"]}

    def test_year_one_total(self):
        acme = self.by_name["Acme"]["year1"]
        # 3 office days * 48 weeks * 10 = 1440 commute cost
        self.assertAlmostEqual(acme["commute_cost"], 1440.0)
        expected = 100000 + 10000 + 10000 + 5000 + 6000 - 1440
        self.assertAlmostEqual(acme["total"], expected)
        self.assertAlmostEqual(self.by_name["Beta"]["year1"]["total"], 115000.0)

    def test_four_year_total(self):
        acme = self.by_name["Acme"]
        expected = 4 * (100000 + 10000 + 10000 + 6000 - 1440) + 5000
        self.assertAlmostEqual(acme["multi_year_total"], expected)
        self.assertAlmostEqual(acme["average_per_year"], expected / 4)

    def test_best_offer_flags(self):
        self.assertEqual(self.result["best_year1"], "Acme")
        self.assertEqual(self.result["best_multi_year"], "Acme")

    def test_commute_hours(self):
        self.assertAlmostEqual(self.by_name["Acme"]["commute_hours_per_year"], 3 * 48 * 60 / 60)
        self.assertEqual(self.by_name["Beta"]["commute_hours_per_year"], 0)

    def test_raise_and_haircut(self):
        r = oc.compare([{"name": "R", "base": 100000, "annual_raise_pct": 10,
                         "equity_value": 40000, "equity_haircut_pct": 50}], years=2)
        row = r["offers"][0]
        self.assertAlmostEqual(row["year1"]["equity"], 5000.0)
        self.assertAlmostEqual(row["multi_year_total"], 100000 + 110000 + 5000 + 5000)

    def test_validation(self):
        for bad in ([{"base": 1}], [{"name": "A"}], [{"name": "A", "base": -5}],
                    [{"name": "A", "base": "lots"}], [{"name": "A", "base": 1, "vesting_years": 0}],
                    [{"name": "A", "base": 1, "office_days": 9}], []):
            with self.assertRaises(oc.OfferError):
                oc.compare(bad)

    def test_markdown(self):
        md = oc.to_markdown(self.result, "USD")
        self.assertIn("|  | Acme | Beta |", md)
        self.assertIn("**Year-1 total**", md)
        self.assertIn("**4-year total**", md)
        self.assertIn("USD 129,560", md)
        self.assertIn("| 12 mo / 4 yr | no equity |", md)
        self.assertIn("not financial, tax or legal advice", md)

    def test_money_formatting(self):
        self.assertEqual(oc.money(1234.4), "1,234")
        self.assertEqual(oc.money(-0.2), "0")
        self.assertEqual(oc.money(-1500, "EUR"), "EUR -1,500")


class CliTests(unittest.TestCase):
    def run_cli(self, data, *args):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "offers.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = oc.main([str(path), *args])
        return code, out.getvalue(), err.getvalue()

    def test_object_form_with_meta(self):
        code, out, _ = self.run_cli({"currency": "INR", "years": 3, "offers": OFFERS})
        self.assertEqual(code, 0)
        self.assertIn("**3-year total**", out)
        self.assertIn("INR", out)

    def test_json_flag(self):
        code, out, _ = self.run_cli(OFFERS, "--json", "--years", "2")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["years"], 2)
        self.assertEqual(len(data["offers"]), 2)

    def test_bad_input(self):
        code, _, err = self.run_cli({"nothing": 1})
        self.assertEqual(code, 2)
        self.assertIn("error", err)

    def test_example_file_parses(self):
        example = Path(__file__).resolve().parent.parent / "skills" / "jobhunt-negotiate" / "offers.example.json"
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = oc.main([str(example)])
        self.assertEqual(code, 0)
        self.assertIn("Offer comparison", out.getvalue())


if __name__ == "__main__":
    unittest.main()
