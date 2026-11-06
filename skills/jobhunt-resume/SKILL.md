---
name: jobhunt-resume
description: >-
  Tailors the user's resume to one job posting using only the experience in
  jobhunt/profile.md: picks the most relevant roles and achievements, reorders
  and rewords them in the posting's language, and runs ats_match.py to report
  keyword coverage, missing terms and over-used words. Missing terms the user
  truly lacks are reported as gaps, never inserted. Ends with a truth check
  against the profile. Use when the user says "tailor my resume", "rewrite my
  CV for this job", "will my resume pass the ATS", "match my resume to this
  posting", "what keywords am I missing", or "make my resume stronger".
argument-hint: "[role folder or posting file]"
---

# Tailor a resume

Purpose: produce a resume for one posting that a recruiter can scan in ten
seconds and an applicant tracking system can match, while every line stays
true. Tailoring means choosing, ordering and rewording real experience. It
never means adding experience the user does not have.

## Inputs

- `jobhunt/profile.md` (required). If missing, stop and run `jobhunt-profile`.
- The posting: `jobhunt/roles/<slug>/posting.md`, or a file/text the user gives
  (save it there first). If `decode.md` exists, use its must-haves.
- Optional: the user's current resume, for layout and tone.

## Outputs

- `jobhunt/roles/<slug>/resume.md`: the tailored resume in plain markdown
  (easy to paste into Word, Google Docs or an online form).
- `jobhunt/roles/<slug>/ats-report.md`: keyword report before and after.
- `jobhunt/roles/<slug>/gaps.md`: requirements the profile cannot support and
  how to close each one.

## Steps

1. Read the profile and the posting. List the must-haves (from `decode.md` if
   present, else pull them from the posting yourself).
2. Baseline: if the user has a current resume file, run
   `python3 "${CLAUDE_SKILL_DIR}/ats_match.py" --posting jobhunt/roles/<slug>/posting.md --resume <current resume> --json`
   and keep the coverage number for comparison. On Windows, `python` instead of
   `python3` is fine.
3. Map each must-have to profile evidence: role, achievement line, number and
   its tag (`[exact]`, `[estimate]`, `[range]`). Anything with no evidence goes
   to `gaps.md`, not the resume.
4. Draft the resume:
   - Header from the profile's contact line. No photo, age, marital status or
     ID numbers unless the user says their country expects them.
   - Summary: two or three lines naming the target role, years of relevant
     work the profile supports, and the two strongest proofs.
   - Experience: real titles and real dates. Order bullets by relevance to this
     posting. Three to five bullets for recent roles, one or two for old ones.
   - Bullet shape: action verb + what + result. Use the number exactly as the
     profile tags it: an `[estimate]` reads "about 30%", a `[range]` reads
     "20-30%", never a sharper figure.
   - Reword with the posting's own terms where the meaning is the same:
     "rota" to "staff scheduling", "clients" to "accounts", "bug fixes" to
     "defect resolution". If the meaning would change, keep the user's words.
   - Skills: only skills listed in "Skills with evidence". Order by the
     posting's priorities.
   - Length: one page for under about ten years of experience, two pages
     maximum otherwise, unless the field expects a long CV (academia,
     medicine); ask if unsure.
5. Run the match on the draft:
   `python3 "${CLAUDE_SKILL_DIR}/ats_match.py" --posting jobhunt/roles/<slug>/posting.md --resume jobhunt/roles/<slug>/resume.md`
   Save the output to `ats-report.md` with the baseline number at the top.
6. Work through the report's "Missing" list term by term:
   - Real but worded differently in the profile: reword the bullet to use the
     posting's term. Re-run the script.
   - Real but not in the profile: ask the user. If they confirm it with a
     concrete example, add it to `profile.md` first, then to the resume.
   - Not real: leave it out. Add it to `gaps.md` with an honest way to close it
     (a short course, a small project, a transferable example to raise in the
     interview, or simply naming it as an area they are learning).
   - Boilerplate words (company name, "benefits", "nice") need no action.
   Do not chase 100% coverage. 60-80% on must-have terms with true bullets
   beats a stuffed resume a human reader rejects.
7. Fix the "Over-used words" and "Stock phrases" sections: vary verbs, replace
   "responsible for" with what actually happened.
8. Truth check: delegate to the `resume-truth-checker` agent with the paths to
   `resume.md` and `profile.md`. Fix every line it flags as unsupported or
   overstated before showing the user the final version.
9. Show the user: coverage before and after, the top five changes and why, and
   the gaps list. Ask before overwriting any file they wrote themselves.
10. Hand off: `jobhunt-cover-letter` for the letter, `jobhunt-tracker` to log
    the application once they send it.

## Format rules for tracking systems

- One column, standard headings (Summary, Experience, Skills, Education).
- No tables, text boxes, images or icons in the final document.
- Dates as "Mon YYYY - Mon YYYY" on the same line as the title.
- Save the final as .docx or PDF only if the posting asks for a format; the
  user can export the markdown themselves.

## What NOT to do

- Never add a skill, tool, title, employer, date, degree, certification or
  number that is not in `profile.md`.
- Never upgrade a title ("Coordinator" to "Manager") or stretch dates to hide
  a gap.
- Never hide keywords in white text, tiny fonts or metadata. It is dishonest
  and recruiters catch it.
- Never turn an `[estimate]` into an exact number.
- Never paste the posting's sentences into the resume as if they were the
  user's experience.
