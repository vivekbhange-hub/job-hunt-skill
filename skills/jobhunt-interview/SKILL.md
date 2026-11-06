---
name: jobhunt-interview
description: >-
  Runs a realistic mock interview for one job with a panel of interviewer
  agents (recruiter screen, hiring manager, bar raiser): behavioral STAR
  questions plus role-specific ones built from the posting. Asks one question
  at a time, scores each answer against a five-part rubric, and rewrites a
  stronger answer using only facts the user gave. Saves a prep sheet of story
  gaps to fix. Use when the user says "mock interview me", "practice for my
  interview", "ask me interview questions", "how do I answer tell me about
  yourself", "prep me for the hiring manager round", or "grill me".
argument-hint: "[role folder] [screen | manager | bar-raiser | full]"
---

# Mock interview

Purpose: let the user rehearse out loud (or in writing) against interviewers
who behave like the real ones, then show them exactly what made an answer weak
and what a stronger version sounds like, built only from their own facts.

## Inputs

- `jobhunt/profile.md`, especially "Stories for interviews".
- `jobhunt/roles/<slug>/posting.md` and `decode.md` if present (the predicted
  loop decides which rounds to run).
- Round choice from the user: `screen`, `manager`, `bar-raiser` or `full`.
  Default: the next round they actually face; ask if unknown.
- `rubric.md` in this skill folder.

## Outputs

- `jobhunt/roles/<slug>/interview-notes.md`: every question, the user's
  answer (summarised), the score, the stronger answer, and follow-ups to
  practise.
- `jobhunt/roles/<slug>/prep-sheet.md`: one page to read before the real
  interview: 6-8 stories mapped to likely questions, numbers to remember,
  questions to ask them, and gaps with an honest line for each.

## Steps

1. Read the profile and posting. Build a question bank of 10-15 questions:
   - Behavioral (STAR): conflict, failure, influence, prioritising, a hard
     deadline, a mistake, feedback received. Pick the ones the posting's
     must-haves point to.
   - Role-specific: what the job really tests in this field. A nurse gets a
     deteriorating-patient scenario, a teacher a lesson-planning or behaviour
     scenario, a sales rep a pipeline question, an accountant a month-end
     close problem, an engineer a design or debugging question.
   - Motivation: why this role, why leave, what they want next.
   - One gap question that probes the weakest must-have from the fit table.
2. Choose interviewers by round and delegate to the matching agent with the
   posting, the decode and the question bank:
   - `screen` -> `recruiter-screen` agent.
   - `manager` -> `hiring-manager` agent.
   - `bar-raiser` -> `bar-raiser` agent.
   - `full` -> all three in that order, 3-5 questions each.
   The agent returns its questions and follow-up probes; you run the
   conversation.
3. Ask one question at a time and wait. Do not show the next question, the
   rubric or a model answer before the user has answered.
4. After each answer, ask the agent's follow-up probe if the answer was vague
   (no numbers, "we" instead of "I", no result). One probe per question.
5. Score the answer with `rubric.md`: five criteria, 1-4 each, total out of
   20. Give one sentence of evidence per criterion, quoting the user.
6. Write a stronger answer:
   - Use only facts from the user's answer and `profile.md`. If a stronger
     answer needs a fact the user has not given (the result, a number, their
     own part), ask for it instead of supplying it, and show the answer with
     a bracketed placeholder like `[result you measured]`.
   - Keep their voice. Shorter is usually stronger: 60-120 seconds spoken,
     about 150-250 words.
7. After the round, give: average score, the two habits to fix (for example
   "ends without a result", "says we, never I"), and the best answer of the
   session.
8. Write `interview-notes.md` and `prep-sheet.md`. Add any new story the user
   told you to `profile.md` under "Stories for interviews", after asking.
9. Hand off: run another round, `jobhunt-followup` for a thank-you note after
   the real interview, `jobhunt-tracker` to update the stage.

## Rules for realism

- Interviewers interrupt rambling. If an answer passes about 300 words, the
  agent cuts in with a redirect, as real interviewers do.
- Mix easy and hard. Start with "Tell me about yourself"; put the hardest
  question in the middle, not at the end.
- If the user says "I don't know", score it honestly, then coach the honest
  version: what they do know, how they would find out, a related example.

## What NOT to do

- Never write a stronger answer that contains a result, number, tool, team
  size or decision the user did not give you.
- Never tell the user to claim experience they lack to get past a gap
  question. Coach the honest answer instead.
- Do not dump all questions at once or answer for the user.
- Do not score generously to be kind. A 2 with a clear fix helps more than a
  vague 4.
- Do not give legal advice about questions on age, family, religion, health or
  nationality; flag that such questions may be unlawful where they live and
  offer a polite redirect line.
