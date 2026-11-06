---
name: jobhunt-profile
description: >-
  Builds and maintains jobhunt/profile.md, the single source of truth for a job
  search: real roles with dates, achievements with numbers the user confirmed,
  skills with evidence, education, and constraints such as location, salary
  floor, notice period and visa status. Runs as a short interview, one topic at
  a time, and never fills a blank with a guess. Every other jobhunt skill reads
  this file. Use when the user says "set up my job search", "build my profile",
  "here is my CV, learn it", "update my experience", "I just finished a
  project, add it", "start the job hunt pack", or when another jobhunt skill
  finds no profile.
argument-hint: "[path to existing resume or CV]"
---

# Job hunt profile

Purpose: capture the user's real working history once, in their own words, so
every resume, cover letter, interview answer and negotiation in this pack is
built from facts the user has confirmed. The profile is the guardrail against
invention: if a claim is not in `jobhunt/profile.md`, no other jobhunt skill may
put it in front of an employer.

## Inputs

- Optional: a path to an existing resume, CV, LinkedIn export or portfolio page
  saved as text, markdown, or PDF the user can read with the Read tool.
- The user's answers to the interview below.
- An existing `jobhunt/profile.md`, if there is one (update mode).

## Output

- `jobhunt/profile.md`, following `profile-template.md` in this skill folder.
- If the folder is inside a git repository, suggest adding `jobhunt/` to
  `.gitignore`. Personal data stays local; never upload it anywhere.

## Steps

1. Check for `jobhunt/profile.md`.
   - Exists: read it, show a five-line summary, and ask what changed. Edit only
     those sections, then go to step 7.
   - Missing: create the `jobhunt/` folder and continue.
2. If the user gave a resume or CV, read it and draft the Roles section from it.
   Mark every number you copied as `(from CV, confirm)`. Do not reword yet.
3. Interview in short rounds. Ask at most three questions per message, wait for
   answers, then move on. Order:
   1. Target: which roles, which field, which level, which industries are out.
   2. Constraints: locations or remote, salary floor and currency, notice
      period, work authorisation or visa sponsorship needed, travel limits,
      start date. These are private and only used for filtering and
      negotiation.
   3. Each role, most recent first: employer, title, dates (month and year),
      team size, who they reported to, what they owned.
   4. For each role, two to four achievements. Push for the result, not the
      task: "What changed because you did this? How do you know?"
   5. Skills, tools, licences, certifications, languages. For each skill, ask
      where they used it; a skill without evidence goes under "Learning".
   6. Education and training.
   7. Stories: one example each of a conflict, a failure, a hard deadline, a
      time they led without authority. These feed jobhunt-interview.
4. Numbers rule. When an achievement has a number, ask: "Is that exact, an
   estimate, or a range you can defend if asked?" Record the answer next to the
   number: `[exact]`, `[estimate]` or `[range]`. If the user has no number, write
   the achievement without one and add it to "Numbers to find" so they can look
   it up (old reports, performance reviews, emails). Never supply a plausible
   figure yourself.
5. Field-neutral wording. Use the user's field's own terms: patients and wards
   for a nurse, students and grades for a teacher, covers and food cost for a
   chef, tickets and uptime for an engineer. Do not translate everything into
   tech or corporate language.
6. Write `jobhunt/profile.md` from the template. Keep the user's phrasing in the
   achievement lines; tighten grammar only.
7. Read the file back as a short summary and ask the user to confirm or correct
   it. Set `Last confirmed:` to today's date once they confirm.
8. Hand off: suggest `jobhunt-decode` with a posting they care about, or
   `jobhunt-tracker` if they want to log applications already sent.

## Decision rules

- A fact goes in the profile only if the user stated or confirmed it.
- Titles stay as they were. If the official title undersells the work (for
  example "Associate" while running a team), record both: the official title,
  and a one-line "Scope" note. Resumes may show scope; they may not change the
  title.
- Dates stay as they were. Gaps are recorded honestly with a one-line reason if
  the user wants to give one (caregiving, study, health, layoff, travel).
- If the user asks to "make it sound better", tighten the wording but keep the
  same facts and the same numbers.
- Self-employment, volunteering, military service, care work and side projects
  count as experience. Record them like any other role.

## What NOT to do

- Do not invent, round up, or "estimate for them" any number, date, title,
  employer, skill, tool or certification.
- Do not copy the user's salary floor, visa status or health details into any
  file that leaves the `jobhunt/` folder.
- Do not ask for government ID numbers, bank details, passwords or dates of
  birth. The pack never needs them.
- Do not run the whole interview in one giant message. Three questions a turn.
- Do not judge the user's history. Gaps and short stints are facts to frame
  later, not problems to lecture about.
