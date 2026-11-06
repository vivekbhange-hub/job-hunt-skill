#!/usr/bin/env python3
"""Keep a job-application tracker in a plain CSV file.

Commands:
  add      add an application
  update   change stage, last contact, next action or notes of one application
  list     print applications as a markdown table (filter by stage or active only)
  stats    response rate, stage funnel, and stale applications that need a follow-up

The CSV lives at jobhunt/applications.csv by default (change with --file). It
is a normal spreadsheet file: open it in Excel, Numbers or LibreOffice too.

Examples:
  python3 tracker.py add --company "Acme" --role "Ops Lead" --source referral
  python3 tracker.py update 3 --stage interview --next-action "prep case study"
  python3 tracker.py list --active
  python3 tracker.py stats --stale-days 10
"""

import argparse
import csv
import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path

DEFAULT_FILE = Path("jobhunt") / "applications.csv"

COLUMNS = [
    "id",
    "company",
    "role",
    "stage",
    "furthest_stage",
    "applied_date",
    "last_contact",
    "next_action",
    "source",
    "link",
    "salary_range",
    "notes",
]

# Pipeline order. Closed stages sit outside the pipeline.
PIPELINE = ["saved", "applied", "screen", "interview", "final", "offer", "accepted"]
CLOSED = ["rejected", "withdrawn", "ghosted"]
STAGES = PIPELINE + CLOSED
ACTIVE = {"applied", "screen", "interview", "final", "offer"}
RESPONDED = {"screen", "interview", "final", "offer", "accepted"}


class TrackerError(ValueError):
    pass


def parse_date(text, field="date"):
    try:
        return dt.date.fromisoformat(text)
    except (TypeError, ValueError):
        raise TrackerError(f"{field} must be YYYY-MM-DD, got {text!r}")


def check_stage(stage):
    stage = (stage or "").strip().lower()
    if stage not in STAGES:
        raise TrackerError(f"unknown stage {stage!r}; use one of: {', '.join(STAGES)}")
    return stage


def load(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        rows = []
        for row in csv.DictReader(fh):
            rows.append({col: (row.get(col) or "").strip() for col in COLUMNS})
        return rows


def save(path, rows):
    """Write atomically so a crash never leaves a half-written tracker."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".applications.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=COLUMNS)
            writer.writeheader()
            for row in rows:
                writer.writerow({col: row.get(col, "") for col in COLUMNS})
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def further(a, b):
    """Return whichever pipeline stage is further along."""
    rank = {s: i for i, s in enumerate(PIPELINE)}
    if a not in rank:
        return b if b in rank else a
    if b not in rank:
        return a
    return a if rank[a] >= rank[b] else b


def add(rows, company, role, today, stage="applied", applied=None, source="", link="",
        salary="", notes="", next_action=""):
    if not company.strip() or not role.strip():
        raise TrackerError("company and role are required")
    stage = check_stage(stage)
    applied_date = parse_date(applied, "--applied").isoformat() if applied else (
        "" if stage == "saved" else today.isoformat())
    next_id = max((int(r["id"]) for r in rows if r["id"].isdigit()), default=0) + 1
    row = {
        "id": str(next_id),
        "company": company.strip(),
        "role": role.strip(),
        "stage": stage,
        "furthest_stage": stage if stage in PIPELINE else "applied",
        "applied_date": applied_date,
        "last_contact": applied_date,
        "next_action": next_action.strip(),
        "source": source.strip(),
        "link": link.strip(),
        "salary_range": salary.strip(),
        "notes": notes.strip(),
    }
    rows.append(row)
    return row


def find(rows, app_id):
    for row in rows:
        if row["id"] == str(app_id):
            return row
    raise TrackerError(f"no application with id {app_id}")


def update(rows, app_id, today, stage=None, last_contact=None, next_action=None,
           notes=None, append_note=None, link=None, salary=None):
    row = find(rows, app_id)
    if stage:
        stage = check_stage(stage)
        row["stage"] = stage
        base = row["furthest_stage"] or "applied"
        if stage != "saved" and base == "saved":
            base = "applied"  # leaving 'saved' for any other stage means it was sent
        row["furthest_stage"] = further(base, stage)
        if stage != "saved" and not row["applied_date"]:
            row["applied_date"] = today.isoformat()
        if not last_contact:
            row["last_contact"] = today.isoformat()
    if last_contact:
        row["last_contact"] = parse_date(last_contact, "--last-contact").isoformat()
    if next_action is not None:
        row["next_action"] = next_action.strip()
    if notes is not None:
        row["notes"] = notes.strip()
    if append_note:
        stamp = f"{today.isoformat()}: {append_note.strip()}"
        row["notes"] = f"{row['notes']} | {stamp}" if row["notes"] else stamp
    if link is not None:
        row["link"] = link.strip()
    if salary is not None:
        row["salary_range"] = salary.strip()
    return row


def days_since(row, today):
    ref = row["last_contact"] or row["applied_date"]
    if not ref:
        return None
    try:
        return (today - dt.date.fromisoformat(ref)).days
    except ValueError:
        return None


def stale(rows, today, stale_days=10):
    out = []
    for row in rows:
        if row["stage"] not in ACTIVE:
            continue
        age = days_since(row, today)
        if age is not None and age >= stale_days:
            out.append({**row, "days_quiet": age})
    out.sort(key=lambda r: (-r["days_quiet"], int(r["id"]) if r["id"].isdigit() else 0))
    return out


def stats(rows, today, stale_days=10):
    by_stage = {s: 0 for s in STAGES}
    for row in rows:
        if row["stage"] in by_stage:
            by_stage[row["stage"]] += 1
    sent = [r for r in rows if r["stage"] != "saved"]
    responded = [
        r for r in sent
        if r["stage"] == "rejected" or r["stage"] in RESPONDED or r["furthest_stage"] in RESPONDED
    ]
    rank = {s: i for i, s in enumerate(PIPELINE)}
    funnel = {}
    for stage in PIPELINE[1:]:
        funnel[stage] = sum(
            1 for r in sent if rank.get(r["furthest_stage"] or "applied", 1) >= rank[stage]
        )
    return {
        "total": len(rows),
        "sent": len(sent),
        "active": sum(1 for r in rows if r["stage"] in ACTIVE),
        "responses": len(responded),
        "response_rate_pct": round(100.0 * len(responded) / len(sent), 1) if sent else 0.0,
        "by_stage": by_stage,
        "funnel": funnel,
        "stale": stale(rows, today, stale_days),
        "stale_days": stale_days,
    }


def md_escape(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def table(rows, columns):
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(row.get(c, "")) for c in columns) + " |")
    return "\n".join(lines)


def stats_markdown(s):
    lines = [
        "# Job search stats",
        "",
        f"- Applications tracked: {s['total']} ({s['sent']} sent, {s['active']} active)",
        f"- Response rate: {s['response_rate_pct']}% ({s['responses']} of {s['sent']} heard back)",
        "",
        "## Funnel (reached at least this stage)",
        "",
    ]
    top = s["funnel"].get("applied", 0)
    for stage, n in s["funnel"].items():
        share = f"{100.0 * n / top:.0f}%" if top else "0%"
        lines.append(f"- {stage}: {n} ({share})")
    lines += ["", "## Current stage", ""]
    lines += [f"- {stage}: {n}" for stage, n in s["by_stage"].items() if n]
    lines += ["", f"## Needs a follow-up (quiet {s['stale_days']}+ days)", ""]
    if s["stale"]:
        lines.append(table(s["stale"], ["id", "company", "role", "stage", "days_quiet", "next_action"]))
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_parser():
    p = argparse.ArgumentParser(description="Track job applications in a CSV file.")
    p.add_argument("--file", default=str(DEFAULT_FILE), help=f"CSV path (default {DEFAULT_FILE})")
    p.add_argument("--today", help="override today's date, YYYY-MM-DD (for tests and backfilling)")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="add an application")
    a.add_argument("--company", required=True)
    a.add_argument("--role", required=True)
    a.add_argument("--stage", default="applied", help=f"one of: {', '.join(STAGES)}")
    a.add_argument("--applied", help="date applied, YYYY-MM-DD (default today)")
    a.add_argument("--source", default="", help="where you found it: referral, job board, recruiter...")
    a.add_argument("--link", default="")
    a.add_argument("--salary", default="", help="posted or discussed range")
    a.add_argument("--notes", default="")
    a.add_argument("--next-action", default="")

    u = sub.add_parser("update", help="update one application")
    u.add_argument("id")
    u.add_argument("--stage")
    u.add_argument("--last-contact", help="YYYY-MM-DD (default today when the stage changes)")
    u.add_argument("--next-action")
    u.add_argument("--notes", help="replace notes")
    u.add_argument("--append-note", help="add a dated note")
    u.add_argument("--link")
    u.add_argument("--salary")

    ls = sub.add_parser("list", help="list applications")
    ls.add_argument("--stage", help="only this stage")
    ls.add_argument("--active", action="store_true", help="only applied/screen/interview/final/offer")
    ls.add_argument("--json", action="store_true")

    st = sub.add_parser("stats", help="response rate, funnel, stale applications")
    st.add_argument("--stale-days", type=int, default=10, help="quiet days before a follow-up is due (default 10)")
    st.add_argument("--json", action="store_true")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        today = parse_date(args.today, "--today") if args.today else dt.date.today()
        rows = load(args.file)
        if args.command == "add":
            row = add(rows, args.company, args.role, today, stage=args.stage, applied=args.applied,
                      source=args.source, link=args.link, salary=args.salary, notes=args.notes,
                      next_action=args.next_action)
            save(args.file, rows)
            print(f"added #{row['id']}: {row['company']} - {row['role']} ({row['stage']})")
        elif args.command == "update":
            row = update(rows, args.id, today, stage=args.stage, last_contact=args.last_contact,
                         next_action=args.next_action, notes=args.notes, append_note=args.append_note,
                         link=args.link, salary=args.salary)
            save(args.file, rows)
            print(f"updated #{row['id']}: {row['company']} - {row['role']} ({row['stage']})")
        elif args.command == "list":
            picked = rows
            if args.stage:
                stage = check_stage(args.stage)
                picked = [r for r in picked if r["stage"] == stage]
            if args.active:
                picked = [r for r in picked if r["stage"] in ACTIVE]
            if args.json:
                print(json.dumps(picked, indent=2))
            elif picked:
                print(table(picked, ["id", "company", "role", "stage", "applied_date", "last_contact", "next_action"]))
            else:
                print("No applications match.")
        elif args.command == "stats":
            if args.stale_days < 1:
                raise TrackerError("--stale-days must be at least 1")
            result = stats(rows, today, args.stale_days)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                sys.stdout.write(stats_markdown(result))
    except (TrackerError, OSError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
