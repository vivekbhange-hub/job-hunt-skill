---
name: jobhunt-followup
description: >-
  Drafts the messages around an application: thank-you notes after an
  interview, polite follow-ups after silence, a status check before a deadline,
  accepting an offer, declining an offer or withdrawing from a process without
  burning the bridge, and asking someone to be a reference. Every message is
  short, specific to what actually happened, and drafted for the user to send;
  nothing is sent automatically. Use when the user says "write a thank you
  note", "they haven't replied, should I follow up", "how do I decline this
  offer", "withdraw my application", "ask my old manager for a reference",
  or "accept the offer in writing".
argument-hint: "[thank-you | follow-up | decline | withdraw | accept | reference]"
---

# Follow-up messages

Purpose: the small messages decide more outcomes than people expect. A specific
thank-you is remembered, a polite nudge revives a stalled process, and a
graceful decline keeps a door open. This skill drafts each one so it sounds
like the user and says something real.

## Inputs

- The message type: thank-you, follow-up, status check, accept, decline,
  withdraw, reference request. Ask if unclear.
- Context: from `jobhunt/applications.csv` (dates, stage, contact), the role
  folder (`interview-notes.md`, `decode.md`), and the user's account of what
  happened. Ask for one concrete detail from the conversation for thank-yous.
- `jobhunt/profile.md` for the reference request (which project the referee
  saw first-hand).

## Output

- `jobhunt/roles/<slug>/drafts/<YYYY-MM-DD>-<type>.md` containing: To, Subject,
  Body, and a "Send when" line. For reference requests with no role folder,
  `jobhunt/drafts/<YYYY-MM-DD>-reference-<name>.md`.

## Steps

1. Identify the type and gather the facts above. If the tracker shows the
   application, read its `last_contact` date to pick the right timing.
2. Apply the timing rules:
   - Thank-you: same day or next working day after each interview round. One
     note per interviewer if the user has their addresses; vary each note.
   - Follow-up after silence: if they gave a date, wait one or two working
     days past it; otherwise about 7-10 working days after the last contact.
     Second nudge a week or so later. After that, stop and mark the
     application `ghosted` in the tracker; a third message rarely helps.
   - Status check with a competing deadline: send as soon as the other offer
     has a deadline. State the deadline plainly, no pressure language.
   - Decline or withdraw: as soon as the decision is made.
   - Reference request: before the user lists the person, not after.
3. Draft using the patterns below. Keep thank-yous to 80-150 words, follow-ups
   to 50-100, declines to 60-120.
4. Read the draft against the "What NOT to do" list. Fix and show it to the
   user with the "Send when" line.
5. Offer to log the step: `python3 "${CLAUDE_SKILL_DIR}/../jobhunt-tracker/tracker.py" update <id> --last-contact <date> --append-note "<type> sent"`
   only after the user says they sent it.
6. Hand off: `jobhunt-tracker stats` to see what else is going quiet.

## Patterns

**Thank-you**: thanks for the time -> one specific thing from the
conversation (a problem they described, a question that made the user think)
-> one sentence linking a real piece of the user's experience to it -> looking
forward to next steps.

**Follow-up after silence**: one line of context (role, date of last contact)
-> still interested, one concrete reason -> a simple question ("Is there an
update on timing?") -> thanks. No guilt, no "just checking in" opener.

**Status check with a deadline**: still very interested in this role -> I have
received another offer with a decision date of <date> -> is there anything you
can share about your timeline? -> thanks.

**Accept**: accept the offer with the agreed terms restated in one line (title,
start date, pay as agreed) -> ask what the next steps are -> thanks. Remind the
user not to resign from their current job until the written offer and any
checks are complete.

**Decline**: thanks -> decision made to accept another role / not to move
forward -> one honest, kind line (no detailed reasons needed) -> hope to cross
paths again.

**Withdraw**: thanks for their time -> withdrawing from the process -> brief
reason only if the user wants to give one -> wish them well with the hire.

**Reference request**: ask, do not assume -> remind them which work they saw
(project, dates) -> the role and what the employer may ask about -> offer a
short summary to make it easy -> say it is fine to say no.

## What NOT to do

- Never send, schedule or post anything. Drafts only. If an email tool is
  connected, create at most a draft there and only after the user asks.
- No guilt-trips ("I haven't heard back..."), no fake urgency, no invented
  competing offers.
- Do not invent details of the interview conversation; ask for one.
- Do not criticise the employer, the interviewer or the current employer.
- Do not write a reference letter in the referee's name for them to sign as
  their own words unless the user says the referee asked for a draft.
