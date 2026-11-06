---
name: jobhunt-tracker
description: >-
  Keeps the user's job applications in jobhunt/applications.csv with
  tracker.py: add and update applications, list them by stage, and report the
  response rate, the stage funnel and stale applications that need a
  follow-up. The CSV opens in any spreadsheet app and never leaves the user's
  machine. Use when the user says "track this application", "I applied to",
  "I got a screen with", "show my applications", "how is my job search going",
  "what should I follow up on", "they rejected me", or "update my tracker".
argument-hint: "[add | update | list | stats]"
---

# Application tracker

Purpose: a job search with more than a handful of applications needs a ledger.
This skill keeps one in a plain CSV and turns it into the two numbers that
matter week to week: how many applications get a response, and which ones
have gone quiet and need a nudge.

## Inputs

- What the user tells you: company, role, stage, dates, source, link.
- `jobhunt/applications.csv` (created on first `add`).

## Output

- `jobhunt/applications.csv` with columns: id, company, role, stage,
  furthest_stage, applied_date, last_contact, next_action, source, link,
  salary_range, notes.
- Markdown tables and stats printed in chat.

## Stages

`saved` -> `applied` -> `screen` -> `interview` -> `final` -> `offer` -> `accepted`,
plus closed stages `rejected`, `withdrawn`, `ghosted`. The script remembers the
furthest pipeline stage reached, so a rejection after a final round still
counts in the funnel.

## Steps

1. Work out the command from what the user said:
   - "I applied to X for Y" -> `add`
   - "I have a screen / interview / offer with X", "X rejected me" -> `update`
   - "show my applications", "what is active" -> `list`
   - "how is it going", "what should I follow up on" -> `stats`
2. Run the script from the user's project root. Base command:
   `python3 "${CLAUDE_SKILL_DIR}/tracker.py" <command> ...`
   On Windows, `python` works in place of `python3`.
   - Add: `... add --company "Acme Health" --role "Ward Manager" --source referral --link "<url>" --next-action "follow up 2026-11-20"`
     (`--applied YYYY-MM-DD` for past applications, `--stage saved` for ones
     not yet sent).
   - Update: `... update 4 --stage interview --next-action "prep case study"`
     (`--last-contact` defaults to today when the stage changes;
     `--append-note "text"` adds a dated note).
   - List: `... list --active` or `... list --stage offer`.
   - Stats: `... stats --stale-days 10`.
3. If the user names a company that matches more than one row, run `list`,
   show the matches, and ask which id.
4. After `stats`, summarise in three lines: response rate, where the funnel
   narrows most, and how many applications need a follow-up. Then add one
   practical suggestion based on the numbers:
   - Low response rate (roughly under 10% after 20+ applications): the resume
     or targeting is the bottleneck. Suggest `jobhunt-decode` on recent
     postings and `jobhunt-resume` for the next few.
   - Many screens but few interviews: the pitch on the phone is the
     bottleneck. Suggest `jobhunt-interview screen`.
   - Interviews but no offers: suggest `jobhunt-interview bar-raiser`.
   - Stale list not empty: suggest `jobhunt-followup` for each one.
   These are rules of thumb from the user's own data, not market benchmarks;
   say so.
5. When the user reports a stage change in another skill's flow (an interview
   booked, an offer received), offer to update the tracker.

## Decision rules

- Ask before logging an application the user only mentioned in passing.
- Use the date the user gives; default to today only for events happening
  today.
- Never delete rows. Closed applications stay for the stats; set them to
  `rejected`, `withdrawn` or `ghosted`.
- If the CSV was edited by hand and the script reports an error, show the error
  and the offending line instead of rewriting the file.

## What NOT to do

- Do not store passwords, portal logins or ID numbers in notes.
- Do not move the file out of `jobhunt/` or sync it anywhere unless the user
  asks.
- Do not invent dates or stages to fill the table.
- Do not compare the user's response rate with made-up "industry averages".
