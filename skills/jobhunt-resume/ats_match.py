#!/usr/bin/env python3
"""Compare the keywords of a job posting with a resume.

Extracts single words and two-word phrases from both texts (standard library
only: regex tokenization, a stopword list, light plural folding), then reports:

  * coverage: share of the posting's top terms that appear in the resume
  * matched and missing terms, ranked by how often the posting uses them
  * over-used words in the resume and stock phrases worth replacing

Missing terms are a to-check list, never a to-insert list. A term belongs on
the resume only if the user's real experience (jobhunt/profile.md) backs it.

Examples:
  python3 ats_match.py --posting posting.txt --resume resume.md
  python3 ats_match.py --posting posting.txt --resume resume.md --json
  cat posting.txt | python3 ats_match.py --posting - --resume resume.md
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

STOPWORDS = frozenset(
    """
    a about above across after again against all also am an and any are as at
    be because been before being below between both but by can could did do does
    doing down during each either etc even ever every few for from further get
    gets getting had has have having he her here hers him his how i if in into
    is it its itself just least less let like ll made make makes many may me
    might more most much must my no nor not now of off on once one only or other
    our ours out over own per please re same she should so some such than that
    the their theirs them then there these they this those through to too under
    until up upon us use used using ve very via was we well were what when where
    which while who whom whose why will with within without would yet you your
    yours

    ability able across apply applicant applicants candidate candidates company
    day days desired environment equal excellent experience experienced
    familiarity good great have highly ideal ideally including join job looking new nice
    opportunity plus position preferred qualifications related required
    qualification requirement requirements responsibilities responsibility role
    seeking skill skills strong
    successful team teams work working year years
    """.split()
)

# Phrases that tell a reader nothing. Reported so the user can swap them for evidence.
CLICHES = (
    "results-driven",
    "results driven",
    "detail-oriented",
    "detail oriented",
    "team player",
    "hard worker",
    "hardworking",
    "go-getter",
    "self-starter",
    "self starter",
    "think outside the box",
    "synergy",
    "dynamic",
    "passionate",
    "proven track record",
    "responsible for",
    "duties included",
    "fast-paced",
    "fast paced",
    "excellent communication skills",
    "best of breed",
    "rockstar",
    "ninja",
    "guru",
)

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#.&/-]*[a-z0-9+#]|[a-z0-9]")
SEGMENT_SPLIT_RE = re.compile(r"[\n\r;:,()\[\]{}|!?•]+|\.(?=\s|$)|\s[-–—]+\s")

# Words that end in "s" but are not plurals; leave them alone.
_NO_FOLD = frozenset(
    "analysis basis business process access success class status series "
    "aws sas kubernetes ios macos windows sales logistics statistics physics "
    "economics mathematics news canvas gas bus plus campus census address".split()
)


def fold(token):
    """Fold simple English plurals so 'dashboards' matches 'dashboard'."""
    # Short tokens are usually acronyms (ACLS, APIs, CPAs); leave them as written.
    if token in _NO_FOLD or token in STOPWORDS or len(token) <= 4 or not token.isalpha():
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith(("sses", "xes", "ches", "shes")):
        return token[:-2]
    if token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def tokenize_segments(text):
    """Split text into segments (lines, clauses) and each segment into tokens.

    Bigrams never cross a segment boundary, so a bullet's last word and the next
    bullet's first word never form a fake phrase.
    """
    segments = []
    for raw in SEGMENT_SPLIT_RE.split(text.lower()):
        tokens = [fold(t.strip(".-/&")) for t in TOKEN_RE.findall(raw)]
        tokens = [t for t in tokens if t]
        if tokens:
            segments.append(tokens)
    return segments


def is_content(token):
    if token in {"c", "r"}:  # programming languages
        return True
    return token not in STOPWORDS and len(token) > 1 and any(ch.isalpha() for ch in token)


def count_terms(text):
    """Return (unigram Counter, bigram Counter) of content terms."""
    unigrams, bigrams = Counter(), Counter()
    for tokens in tokenize_segments(text):
        for i, tok in enumerate(tokens):
            if is_content(tok):
                unigrams[tok] += 1
                if i + 1 < len(tokens) and is_content(tokens[i + 1]):
                    bigrams[tok + " " + tokens[i + 1]] += 1
    return unigrams, bigrams


def top_terms(text, top=40):
    """Rank the posting's terms. A phrase counts double: it is more specific."""
    unigrams, bigrams = count_terms(text)
    scored = [(term, n) for term, n in unigrams.items()]
    scored += [(term, n * 2) for term, n in bigrams.items()]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored[:top]


def find_cliches(text):
    low = text.lower()
    found = []
    for phrase in CLICHES:
        n = len(re.findall(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", low))
        if n:
            found.append((phrase, n))
    return found


def analyze(posting, resume, top=40, overuse=4):
    terms = top_terms(posting, top)
    r_uni, r_bi = count_terms(resume)
    present = set(r_uni) | set(r_bi)
    matched = [(t, s) for t, s in terms if t in present]
    missing = [(t, s) for t, s in terms if t not in present]
    total_weight = sum(s for _, s in terms)
    over = sorted(
        ((t, n) for t, n in r_uni.items() if n >= overuse),
        key=lambda item: (-item[1], item[0]),
    )
    return {
        "terms_checked": len(terms),
        "coverage_pct": round(100.0 * len(matched) / len(terms), 1) if terms else 0.0,
        "weighted_coverage_pct": round(100.0 * sum(s for _, s in matched) / total_weight, 1)
        if total_weight
        else 0.0,
        "matched": [{"term": t, "weight": s} for t, s in matched],
        "missing": [{"term": t, "weight": s} for t, s in missing],
        "overused": [{"word": t, "count": n} for t, n in over],
        "cliches": [{"phrase": p, "count": n} for p, n in find_cliches(resume)],
    }


def to_markdown(result):
    lines = [
        "# Keyword match report",
        "",
        f"- Terms checked from the posting: {result['terms_checked']}",
        f"- Coverage: {result['coverage_pct']}% of terms "
        f"({result['weighted_coverage_pct']}% weighted by how often the posting uses them)",
        "",
        "## Matched",
        "",
    ]
    lines += [f"- {m['term']} ({m['weight']})" for m in result["matched"]] or ["- none"]
    lines += [
        "",
        "## Missing from the resume",
        "",
        "Check each against profile.md. If the experience is real, reword a bullet to say so.",
        "If it is not real, it is a gap: leave it out and plan how to close it.",
        "",
    ]
    lines += [f"- {m['term']} ({m['weight']})" for m in result["missing"]] or ["- none"]
    lines += ["", "## Over-used words in the resume", ""]
    lines += [f"- {o['word']}: {o['count']} times" for o in result["overused"]] or ["- none"]
    lines += ["", "## Stock phrases to replace with evidence", ""]
    lines += [f"- \"{c['phrase']}\": {c['count']}" for c in result["cliches"]] or ["- none"]
    return "\n".join(lines) + "\n"


def read_input(path):
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Keyword coverage of a resume against a job posting (gaps are reported, never filled)."
    )
    parser.add_argument("--posting", required=True, help="posting text file, or - for stdin")
    parser.add_argument("--resume", required=True, help="resume text/markdown file, or - for stdin")
    parser.add_argument("--top", type=int, default=40, help="number of posting terms to check (default 40)")
    parser.add_argument("--overuse", type=int, default=4, help="flag resume words used this many times (default 4)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of markdown")
    args = parser.parse_args(argv)
    if args.posting == "-" and args.resume == "-":
        parser.error("only one of --posting and --resume can read stdin")
    if args.top < 1 or args.overuse < 2:
        parser.error("--top must be >= 1 and --overuse >= 2")
    try:
        posting, resume = read_input(args.posting), read_input(args.resume)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    result = analyze(posting, resume, top=args.top, overuse=args.overuse)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        sys.stdout.write(to_markdown(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
