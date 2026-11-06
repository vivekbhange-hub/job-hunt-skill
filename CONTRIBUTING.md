# Contributing

Thanks for helping make job searching less miserable. Issues and pull requests
are welcome, especially from people outside tech: nurses, teachers, tradespeople,
lawyers, designers, anyone whose field the examples do not cover well yet.

## Ground rules

1. **The honesty rule is not negotiable.** No change may let a skill or agent
   add experience, skills, titles, dates or numbers the user did not confirm.
   Pull requests that weaken this will be closed.
2. **Personal data stays local.** Skills write to the user's `jobhunt/` folder
   and nowhere else. No network calls in scripts, no uploads, no telemetry.
3. **Drafts, never sends.** Anything that would reach another person (email,
   message, form) is drafted for the user to send.
4. **Any field, any country.** Prefer examples from more than one field, and
   do not assume US-only norms for pay, benefits or hiring law.

## Project layout

- `skills/<name>/SKILL.md`: one skill per folder; frontmatter `name` must match
  the folder name.
- `skills/<name>/*.py`: helper scripts, Python 3.9+ standard library only,
  deterministic, with `--help`.
- `agents/*.md`: subagents used by the skills.
- `tests/`: `unittest` tests, standard library only.

## Before you open a pull request

```
python -m unittest discover -s tests -v
```

All tests must pass on Windows, macOS and Linux. If you add a script, add
`tests/test_<script>.py`. If you add a skill or agent, `tests/test_repo.py`
checks its frontmatter and that the README lists it.

## Writing style

Plain, specific English. Short sentences. No buzzwords. Each skill needs
numbered steps Claude can actually follow, concrete file paths, and a
"What NOT to do" section.

## Conduct

Be kind and assume good faith. This project follows the spirit of the
[Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
