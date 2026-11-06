---
name: jobhunt-decode
description: >-
  Reads a job posting (pasted text or a file) and decodes it: real must-haves
  versus nice-to-haves, the seniority and team situation hidden in the wording,
  red flags, the likely interview loop, how well the user's profile fits, and
  sharp questions to ask the employer. Saves the decode next to the posting so
  the resume, cover letter and interview skills can reuse it. Use when the user
  says "decode this job post", "what are they really asking for", "is this job
  worth applying to", "read this posting", "am I a fit for this", "any red
  flags in this listing", or pastes a job description.
argument-hint: "[posting file or pasted text]"
---

# Decode a job posting

Purpose: turn a posting written by a committee into a plain answer to three
questions: what does this employer actually need, what is going on behind the
wording, and is it worth this user's time. Works for any field: a hospital
ward, a school, a warehouse, a law firm, a software team.

## Inputs

- The posting: pasted text, a `.txt`/`.md`/`.pdf` file, or text the user copied
  from a web page. If the user gives only a URL, ask them to paste the text;
  postings change and get taken down, and the saved copy is the record.
- `jobhunt/profile.md` if it exists (for the fit section).

## Output

- `jobhunt/roles/<company>-<role>/posting.md`: the posting text, verbatim, with
  the date saved and the source at the top.
- `jobhunt/roles/<company>-<role>/decode.md`: the report below.
- Folder name: lowercase, hyphens, no spaces, e.g. `roles/st-marys-icu-nurse/`.

## Steps

1. Save the posting verbatim to `posting.md`. Do not clean it up; the exact
   words matter later for keyword matching.
2. Split every requirement into one of three buckets:
   - **Must-have**: stated as required, repeated, listed first, or tied to a
     licence or legal duty (registration, clearance, driving licence).
   - **Nice-to-have**: "preferred", "bonus", "a plus", listed last, or a long
     wish list of tools where nobody could have all of them.
   - **Noise**: generic traits every posting lists ("self-motivated", "team
     player"). Name them once and move on.
   When the posting does not say which bucket, decide from position and
   repetition and say that you inferred it.
3. Read the signals. For each one, quote the phrase and say what it most often
   means, with a confidence word (likely, possible, unclear):
   - Seniority: years asked for, scope words ("own", "set direction" vs
     "support", "assist"), who the role reports to.
   - Team state: "build from scratch" (new team, little process), "scale"
     (growth, hiring), "stabilise", "bring order" (something broke),
     "backfill" or urgent start (someone left).
   - Workload: "wear many hats", "fast-paced", "comfortable with ambiguity",
     "flexible hours", on-call or weekend cover. These are not always bad;
     say what to ask to find out.
   - Red flags: salary missing where the law requires it, "competitive pay"
     with unpaid trial work, commission-only framed as salary, a role that
     reads like two or three jobs, "family" culture language next to long
     hours, vague duties, asks for personal data up front.
   - Green flags: a stated salary range, a named manager, clear outcomes for
     the first 90 days, training or mentoring promised, realistic tool list.
4. Predict the interview loop from the level and field. Typical shapes:
   recruiter or HR screen, hiring-manager conversation, a skills check
   (practical task, case study, teaching demo, clinical scenario, portfolio
   review, technical exercise), a panel or team meet, and a final or values
   round. Say which stages are likely and what each will test. Label it a
   prediction.
5. If the profile exists, write a fit table: each must-have against the
   evidence in the profile, marked **Strong** (direct evidence), **Partial**
   (related or adjacent evidence) or **Gap** (nothing in the profile). Quote
   the profile line you used. Do not count a skill from the "Learning" list as
   evidence.
6. Give a verdict: **Apply**, **Apply with a plan for gaps**, or **Skip**, and
   one sentence on why. A gap in nice-to-haves never makes it a Skip. A missing
   licence or legal requirement usually does.
7. Write six to ten questions for the user to ask the employer, each tied to a
   signal you found, e.g. "What does success look like at 90 days?" when the
   duties are vague, or "Why is this role open?" when the start is urgent.
8. Write `decode.md` and print the verdict and the top three signals in chat.
9. Hand off: `jobhunt-resume` to tailor the resume, `jobhunt-cover-letter` for
   a letter, `jobhunt-tracker` to log it as saved or applied.

## decode.md template

```
# <Role> at <Company> (decoded YYYY-MM-DD)
Verdict: <Apply | Apply with a plan for gaps | Skip> - <one sentence>

## Must-haves
- ...
## Nice-to-haves
- ...
## Signals
| Phrase | Likely meaning | Confidence | What to ask |
## Likely interview loop (prediction)
1. ...
## Fit against your profile
| Must-have | Your evidence (from profile.md) | Rating |
## Gaps and how to close them
- <gap>: <honest way to address it: course, small project, transferable example, or say so in the interview>
## Questions to ask them
1. ...
```

## What NOT to do

- Do not present guesses about the company as facts. Every signal is a reading
  of the wording, labelled with confidence.
- Do not research the company on the web unless the user asks; if they do, cite
  each source.
- Do not mark a gap as Partial to make the user feel better. Honest gaps are
  what the gap plan is for.
- Do not tell the user to skip a job only because they miss nice-to-haves.
- Do not include the user's salary floor or visa status in the decode.
