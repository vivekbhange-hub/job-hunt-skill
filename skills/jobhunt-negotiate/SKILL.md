---
name: jobhunt-negotiate
description: >-
  Compares job offers on year-1 and four-year total compensation with
  offer_compare.py (base, target bonus, equity vesting with cliff, signing
  bonus, benefits, commute cost and time, PTO), then prepares the negotiation:
  a target and walk-away number, a counter-offer email and call talking points,
  all grounded in the user's real offers and constraints. Drafts only; the user
  sends. Not financial, tax or legal advice. Use when the user says "I got an
  offer", "compare these offers", "help me negotiate", "is this offer good",
  "how do I ask for more money", "write a counter offer", or "which job should I take".
argument-hint: "[offers.json]"
---

# Compare offers and negotiate

Purpose: replace the anxious guesswork of an offer with arithmetic and a plan.
First see what each offer is worth over time, side by side; then ask for more
with a specific number, a real reason, and words that keep the relationship
warm.

## Inputs

- Offer details from the user: offer letters, emails, or numbers typed in
  chat. Ask for anything missing: base, bonus target and whether it is
  guaranteed, equity grant value and vesting schedule, signing bonus and its
  clawback, benefits the employer pays, office days, commute, PTO, start date,
  offer deadline.
- `jobhunt/profile.md` constraints (salary floor, location, start date).
- Any market data the user has (published salary ranges, pay bands, a friend's
  figure). Use it only with its source named.

## Outputs

- `jobhunt/offers/offers.json`: the offers in the script's format (see
  `offers.example.json` in this folder).
- `jobhunt/offers/comparison.md`: the script's table plus your notes.
- `jobhunt/offers/negotiation-<company>.md`: target, walk-away, email draft,
  call talking points.

## Steps

1. Collect the numbers. Write `jobhunt/offers/offers.json`. Field reference is
   in the script's `--help`. Use the user's figures only; where a value is
   unknown, leave the field out (it defaults to 0) and list it under
   "Unknowns to ask about".
2. Run the comparison:
   `python3 "${CLAUDE_SKILL_DIR}/offer_compare.py" jobhunt/offers/offers.json`
   Add `--years 3` if the user expects to stay a shorter time. Save the table to
   `comparison.md`.
3. Add notes under the table:
   - Which differences are cash certainty (base, signing) and which are bets
     (bonus at target, private-company equity). If equity cannot be sold,
     rerun with `equity_haircut_pct` set to what the user believes is a fair
     discount, and show both runs.
   - Time cost: commute hours a year, office days, PTO.
   - Non-money factors the user named (manager, growth, mission, stability).
     Ask them to rank their top three; do not rank for them.
4. Set the numbers with the user:
   - **Target**: the specific figure to ask for, with a reason (a competing
     offer, a published band, scope bigger than the title, a relocation cost).
   - **Walk-away**: the lowest offer they would accept, at least the profile's
     salary floor.
   - **Trade list**: what they would take instead of base (signing bonus,
     extra PTO, remote days, earlier review, title, training budget, start
     date).
5. Draft the counter-offer email (150-220 words): thanks and enthusiasm for
   the role in one line, the specific ask with one reason, an open question
   ("Is there flexibility to get to X?"), a warm close. One number, not a
   range; a range invites the bottom of it.
6. Draft call talking points: opening line, the ask, the reason, three likely
   pushbacks with a reply to each ("the band is fixed" -> ask about signing
   bonus or review timing; "we need an answer today" -> ask for 48 hours;
   "this is our best offer" -> thank them, ask about non-cash items), and the
   line to close.
7. If there is a competing offer, use it honestly: name only what is true and
   be ready to accept the other offer if asked.
8. Show the drafts. The user sends the email and makes the call. After the
   reply, rerun the comparison with the new numbers.
9. Hand off: `jobhunt-followup` to accept or decline gracefully,
   `jobhunt-tracker` to set the stage to `offer`, `accepted` or `withdrawn`.

## Decision rules

- If the user has one offer and no other leverage, still negotiate if the ask
  is reasonable; most employers expect it. Frame it on scope and fit, not need.
- Never advise bluffing about other offers, a current salary, or a deadline.
- If the user's current salary is asked and local law bans that question,
  mention that it may be restricted where they live and offer a redirect: "I'm
  focused on the value of this role; my expectation is X."
- In fields with fixed public pay scales (many public-sector, union and
  hospital roles), negotiation is usually about grade or step placement,
  relocation and start date. Say so and adapt.

## What NOT to do

- Do not invent market data, salary bands or "typical" percentages. If the
  user has no data, say the counter rests on their own reasons.
- Do not send anything. Every email and message is a draft.
- Do not present the comparison as financial, tax or legal advice. Equity,
  tax and contract terms vary by country; suggest a qualified adviser for
  large equity grants or unusual clauses (non-competes, clawbacks).
- Do not pressure the user toward the highest number; the table is one input.
