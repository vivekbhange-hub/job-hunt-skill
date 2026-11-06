#!/usr/bin/env python3
"""Compare job offers on year-1 and multi-year total compensation.

Input is JSON: either a list of offers or {"currency": "USD", "years": 4,
"offers": [...]}. Each offer:

  name                 required, label for the column
  base                 required, annual base salary
  bonus_pct            target bonus as % of base (default 0)
  equity_value         total value of the equity grant at today's price (default 0)
  vesting_years        years to fully vest (default 4)
  cliff_months         months before anything vests (default 12)
  equity_haircut_pct   % to knock off equity you cannot sell yet (default 0)
  signing_bonus        one-time, paid in year 1 (default 0)
  relocation           one-time, paid in year 1 (default 0)
  benefits_value       employer-paid benefits per year: retirement match, health premiums... (default 0)
  annual_raise_pct     expected raise per year on base (default 0)
  office_days          days per week in the office (default 5 minus remote_days, else 5)
  remote_days          days per week remote (default 0)
  commute_minutes      round-trip commute minutes per office day (default 0)
  commute_cost         money spent per office day on travel/parking (default 0)
  pto_days             paid days off per year (default 0)
  work_weeks           working weeks per year used for commute math (default 48)

Bonus is counted at target. Equity is counted at the value given, vested
evenly month by month after the cliff. Nothing here is financial, tax or legal
advice; it is arithmetic on the numbers you supply.

Examples:
  python3 offer_compare.py offers.json
  python3 offer_compare.py offers.json --years 3 --json
  cat offers.json | python3 offer_compare.py -
"""

import argparse
import json
import sys
from pathlib import Path

NUMERIC_FIELDS = {
    "base": None,
    "bonus_pct": 0.0,
    "equity_value": 0.0,
    "vesting_years": 4.0,
    "cliff_months": 12.0,
    "equity_haircut_pct": 0.0,
    "signing_bonus": 0.0,
    "relocation": 0.0,
    "benefits_value": 0.0,
    "annual_raise_pct": 0.0,
    "remote_days": 0.0,
    "commute_minutes": 0.0,
    "commute_cost": 0.0,
    "pto_days": 0.0,
    "work_weeks": 48.0,
}


class OfferError(ValueError):
    pass


def normalize(offer, index):
    if not isinstance(offer, dict):
        raise OfferError(f"offer #{index + 1} is not an object")
    name = str(offer.get("name") or "").strip()
    if not name:
        raise OfferError(f"offer #{index + 1} needs a 'name'")
    out = {"name": name}
    for field, default in NUMERIC_FIELDS.items():
        value = offer.get(field, default)
        if value is None:
            raise OfferError(f"{name}: '{field}' is required")
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise OfferError(f"{name}: '{field}' must be a number, got {value!r}")
        if value < 0:
            raise OfferError(f"{name}: '{field}' cannot be negative")
        out[field] = value
    if out["vesting_years"] <= 0:
        raise OfferError(f"{name}: 'vesting_years' must be greater than 0")
    if out["equity_haircut_pct"] > 100:
        raise OfferError(f"{name}: 'equity_haircut_pct' cannot exceed 100")
    if "office_days" in offer:
        try:
            out["office_days"] = float(offer["office_days"])
        except (TypeError, ValueError):
            raise OfferError(f"{name}: 'office_days' must be a number")
    else:
        out["office_days"] = 5.0 - out["remote_days"]
    if not 0 <= out["office_days"] <= 7:
        raise OfferError(f"{name}: office days per week must be between 0 and 7")
    return out


def vested_fraction(months, vesting_years, cliff_months):
    """Share of the grant vested after `months`, monthly vesting after the cliff."""
    if months < cliff_months:
        return 0.0
    return min(1.0, months / (vesting_years * 12.0))


def year_breakdown(o, year):
    """Cash and value received in a given year (1-based)."""
    base = o["base"] * (1 + o["annual_raise_pct"] / 100.0) ** (year - 1)
    bonus = base * o["bonus_pct"] / 100.0
    equity_total = o["equity_value"] * (1 - o["equity_haircut_pct"] / 100.0)
    vy, cliff = o["vesting_years"], o["cliff_months"]
    equity = equity_total * (vested_fraction(year * 12, vy, cliff) - vested_fraction((year - 1) * 12, vy, cliff))
    one_time = (o["signing_bonus"] + o["relocation"]) if year == 1 else 0.0
    commute = o["office_days"] * o["work_weeks"] * o["commute_cost"]
    total = base + bonus + equity + one_time + o["benefits_value"] - commute
    return {
        "base": base,
        "bonus": bonus,
        "equity": equity,
        "one_time": one_time,
        "benefits": o["benefits_value"],
        "commute_cost": commute,
        "total": total,
    }


def compare(offers, years=4):
    if not offers:
        raise OfferError("no offers given")
    if years < 1:
        raise OfferError("years must be at least 1")
    rows = []
    for i, raw in enumerate(offers):
        o = normalize(raw, i)
        per_year = [year_breakdown(o, y) for y in range(1, years + 1)]
        multi = sum(p["total"] for p in per_year)
        commute_hours = o["office_days"] * o["work_weeks"] * o["commute_minutes"] / 60.0
        rows.append(
            {
                "name": o["name"],
                "year1": per_year[0],
                "multi_year_total": multi,
                "average_per_year": multi / years,
                "pto_days": o["pto_days"],
                "office_days": o["office_days"],
                "commute_hours_per_year": commute_hours,
                "equity_value": o["equity_value"],
                "cliff_months": o["cliff_months"],
                "vesting_years": o["vesting_years"],
            }
        )
    best_y1 = max(rows, key=lambda r: r["year1"]["total"])["name"]
    best_multi = max(rows, key=lambda r: r["multi_year_total"])["name"]
    return {"years": years, "offers": rows, "best_year1": best_y1, "best_multi_year": best_multi}


def money(value, currency=""):
    value = round(value)
    text = f"{value + 0:,.0f}"  # + 0 turns -0.0 into 0.0
    return f"{currency} {text}".strip() if currency else text


def num(value):
    return f"{value:g}" if value != int(value) else f"{int(value)}"


def to_markdown(result, currency=""):
    rows = result["offers"]
    names = [r["name"] for r in rows]
    years = result["years"]

    def line(label, cells):
        return "| " + label + " | " + " | ".join(cells) + " |"

    out = [
        "# Offer comparison",
        "",
        line("", names),
        "|---|" + "---:|" * len(names),
        line("Base (year 1)", [money(r["year1"]["base"], currency) for r in rows]),
        line("Bonus at target", [money(r["year1"]["bonus"], currency) for r in rows]),
        line("Equity vested in year 1", [money(r["year1"]["equity"], currency) for r in rows]),
        line("Signing + relocation", [money(r["year1"]["one_time"], currency) for r in rows]),
        line("Benefits value", [money(r["year1"]["benefits"], currency) for r in rows]),
        line("Commute cost", [money(-r["year1"]["commute_cost"], currency) for r in rows]),
        line("**Year-1 total**", [f"**{money(r['year1']['total'], currency)}**" for r in rows]),
        line(f"**{years}-year total**", [f"**{money(r['multi_year_total'], currency)}**" for r in rows]),
        line(f"Average per year over {years}", [money(r["average_per_year"], currency) for r in rows]),
        line("PTO days", [num(r["pto_days"]) for r in rows]),
        line("Office days / week", [num(r["office_days"]) for r in rows]),
        line("Commute hours / year", [f"{r['commute_hours_per_year']:,.0f}" for r in rows]),
        line("Equity cliff / vesting", [
            f"{num(r['cliff_months'])} mo / {num(r['vesting_years'])} yr" if r["equity_value"] else "no equity"
            for r in rows]),
        "",
        f"- Highest year-1 total: {result['best_year1']}",
        f"- Highest {years}-year total: {result['best_multi_year']}",
        "",
        "Bonus is counted at target and is not guaranteed. Equity is counted at the value you",
        "entered; private-company equity can be worth nothing. One-time payments often carry",
        "clawback terms. This is arithmetic, not financial, tax or legal advice.",
        "",
    ]
    return "\n".join(out)


def load(path):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    if isinstance(data, list):
        return data, {}
    if isinstance(data, dict) and isinstance(data.get("offers"), list):
        return data["offers"], data
    raise OfferError("JSON must be a list of offers or an object with an 'offers' list")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Year-1 and multi-year total-comp comparison of job offers.")
    parser.add_argument("offers", help="offers JSON file, or - for stdin")
    parser.add_argument("--years", type=int, default=None, help="horizon in years (default 4, or 'years' in the file)")
    parser.add_argument("--currency", default=None, help="label for amounts, e.g. USD, EUR, INR")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a markdown table")
    args = parser.parse_args(argv)
    try:
        offers, meta = load(args.offers)
        years = args.years if args.years is not None else int(meta.get("years", 4))
        currency = args.currency if args.currency is not None else str(meta.get("currency", ""))
        result = compare(offers, years)
    except (OSError, json.JSONDecodeError, OfferError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        result["currency"] = currency
        print(json.dumps(result, indent=2))
    else:
        sys.stdout.write(to_markdown(result, currency))
    return 0


if __name__ == "__main__":
    sys.exit(main())
