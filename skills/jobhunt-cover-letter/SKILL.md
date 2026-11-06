---
name: jobhunt-cover-letter
description: >-
  Writes a short, specific cover letter (under 250 words) for one job, tied to
  what the employer is actually dealing with and backed by two or three real
  achievements from jobhunt/profile.md. Bans stock openings and clichés, and
  counts words before handing it over. Also writes a three-sentence version for
  online forms and recruiter messages. Use when the user says "write a cover
  letter", "I need a letter for this job", "short note to the hiring manager",
  "why do you want to work here answer", "motivation letter", or "fill in the
  cover letter box on this application".
argument-hint: "[role folder or posting file]"
---

# Write a cover letter

Purpose: a cover letter earns its place only when it says something the resume
cannot: why this employer, why now, and the one or two pieces of evidence that
match their most pressing need. This skill writes that letter in under 250
words, using only facts from the profile.

## Inputs

- `jobhunt/profile.md` (required).
- The posting and, if present, `decode.md` from `jobhunt/roles/<slug>/`.
- Anything the user knows about the employer: a news item, a conversation with
  someone who works there, a product or service they used. Ask once; if there
  is nothing, work from the posting alone.

## Outputs

- `jobhunt/roles/<slug>/cover-letter.md`: the letter, with a word count line
  at the bottom.
- In the same file, a "Short version" section: three sentences for online form
  boxes, email bodies and recruiter messages.

## Steps

1. Find the employer's situation, in this order of preference: something the
   user told you, something stated in the posting ("we are opening a second
   site", "new team", "growing fast", "replacing a legacy system"), the
   signals in `decode.md`. Name it in one phrase. If you cannot find one, use
   the role's main outcome instead and say so to the user.
2. Pick the two or three profile achievements that best match that situation
   and the must-haves. Use their numbers exactly as tagged in the profile.
3. Write four short paragraphs:
   1. Opening (1-2 sentences): the role, and the specific reason this employer.
      Start with the employer's situation or a concrete fact, not with
      "I am writing to apply".
   2. Evidence (2-4 sentences): the achievements, each linked to their need.
   3. Fit and honesty (1-2 sentences): how the user would approach the first
      months, or, if there is a notable gap, a plain sentence on how they are
      closing it. Only mention a gap if the posting makes it a must-have.
   4. Close (1 sentence): a clear next step, e.g. that they would welcome a
      conversation about the role.
4. Run the cliché check below. Rewrite any sentence that contains one.
5. Count words: `python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read().split()))" <file>`
   or count by hand for short text. Body must be under 250 words; aim for 180-220.
6. Write the three-sentence short version.
7. Show both to the user. Offer one revision pass on tone (warmer, more formal,
   more direct). Keep all facts fixed during tone changes.
8. Hand off: `jobhunt-tracker` to log the application; `jobhunt-interview` to
   start preparing.

## Banned phrases

Replace each with a specific fact or delete the sentence:

- "I am writing to express my interest", "I am excited to apply"
- "I believe I would be a great fit", "perfect fit", "ideal candidate"
- "passionate about", "thrilled", "dream job"
- "team player", "hard-working", "detail-oriented", "self-starter",
  "results-driven", "go-getter", "think outside the box"
- "proven track record", "extensive experience", "wealth of experience"
- "I look forward to hearing from you at your earliest convenience"
- "To whom it may concern" (use the hiring manager's name if known, else
  "Dear Hiring Team" or the field's normal greeting)
- Any sentence that would be true of every applicant

## Field notes

- Academic, medical and public-sector posts sometimes expect a longer letter or
  a statement against selection criteria. If the posting asks for that, say so
  and offer to write it criterion by criterion; the 250-word rule then does not
  apply, but the evidence rule still does.
- For career changers: lead with the transferable result, name the new field's
  term for it, and do not pretend the previous job was in the new field.

## What NOT to do

- Do not invent knowledge of the company ("I have long admired your...") unless
  the user told you it is true.
- Do not repeat the resume line by line.
- Do not add achievements, numbers or skills that are not in `profile.md`.
- Do not mention salary, visa status or reasons for leaving unless the posting
  explicitly asks and the user agrees.
- Do not send the letter. The user submits it.
