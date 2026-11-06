"""Structure checks for the whole pack. Frontmatter is parsed by hand (no PyYAML)."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_NAME = "job-hunt-skill"  # manifests must use the published repository name
PREFIX = "jobhunt-"


def frontmatter(path):
    """Return a dict of top-level keys from a --- delimited frontmatter block.

    Handles `key: value`, quoted values, and folded/literal blocks (`>-`, `|`)
    whose continuation lines are indented.
    """
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    data, key = {}, None
    for line in text[4:end].split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[0] in " \t" and key:
            data[key] = (data[key] + " " + line.strip()).strip()
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            raise ValueError(f"{path}: cannot parse frontmatter line {line!r}")
        key, value = match.group(1), match.group(2).strip()
        if value in (">", ">-", "|", "|-"):
            value = ""
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key] = value
    return data


def skill_dirs():
    return sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())


def agent_files():
    return sorted((ROOT / "agents").glob("*.md"))


class SkillTests(unittest.TestCase):
    def test_has_skills(self):
        self.assertGreaterEqual(len(skill_dirs()), 7)

    def test_skill_frontmatter(self):
        for d in skill_dirs():
            with self.subTest(skill=d.name):
                skill_md = d / "SKILL.md"
                self.assertTrue(skill_md.is_file(), f"{d.name} has no SKILL.md")
                fm = frontmatter(skill_md)
                self.assertIsNotNone(fm, f"{d.name}: missing frontmatter")
                self.assertEqual(fm.get("name"), d.name)
                self.assertTrue(d.name.startswith(PREFIX))
                self.assertRegex(d.name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
                desc = fm.get("description", "")
                self.assertTrue(desc, f"{d.name}: empty description")
                self.assertLess(len(desc), 1024, f"{d.name}: description too long ({len(desc)})")
                self.assertIn("Use when", desc)

    def test_skill_body_has_what_not_to_do(self):
        for d in skill_dirs():
            with self.subTest(skill=d.name):
                text = (d / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("What NOT to do", text)
                lines = text.count("\n")
                self.assertTrue(60 <= lines <= 200, f"{d.name}: {lines} lines")

    def test_referenced_scripts_exist(self):
        for d in skill_dirs():
            text = (d / "SKILL.md").read_text(encoding="utf-8")
            for ref in re.findall(r"\$\{CLAUDE_SKILL_DIR\}/([\w./-]+\.py)", text):
                with self.subTest(skill=d.name, script=ref):
                    self.assertTrue((d / ref).resolve().is_file(), f"{d.name} references missing {ref}")


class AgentTests(unittest.TestCase):
    def test_agent_frontmatter(self):
        files = agent_files()
        self.assertGreaterEqual(len(files), 4)
        for f in files:
            with self.subTest(agent=f.name):
                fm = frontmatter(f)
                self.assertIsNotNone(fm, f"{f.name}: missing frontmatter")
                self.assertEqual(fm.get("name"), f.stem)
                self.assertTrue(fm.get("description"))

    def test_truth_checker_is_read_only(self):
        fm = frontmatter(ROOT / "agents" / "resume-truth-checker.md")
        tools = {t.strip() for t in fm.get("tools", "").split(",")}
        self.assertTrue(tools)
        self.assertTrue(tools.isdisjoint({"Write", "Edit", "Bash", "NotebookEdit"}))

    def test_agents_used_by_skills_exist(self):
        names = {f.stem for f in agent_files()}
        text = "\n".join((d / "SKILL.md").read_text(encoding="utf-8") for d in skill_dirs())
        for name in ("recruiter-screen", "hiring-manager", "bar-raiser", "resume-truth-checker"):
            self.assertIn(name, names)
            self.assertIn(name, text)


class ManifestTests(unittest.TestCase):
    def load(self, name):
        with (ROOT / ".claude-plugin" / name).open(encoding="utf-8") as fh:
            return json.load(fh)

    def test_marketplace(self):
        m = self.load("marketplace.json")
        self.assertEqual(m["name"], REPO_NAME)
        self.assertEqual(m["owner"]["name"], "Vivek Bhange")
        self.assertEqual(len(m["plugins"]), 1)
        plugin = m["plugins"][0]
        self.assertEqual(plugin["name"], REPO_NAME)
        self.assertEqual(plugin["source"], "./")
        self.assertEqual(plugin["homepage"], f"https://github.com/vivekbhange-hub/{REPO_NAME}")

    def test_plugin(self):
        p = self.load("plugin.json")
        self.assertEqual(p["name"], REPO_NAME)
        self.assertEqual(p["version"], "1.0.0")
        self.assertEqual(p["license"], "MIT")
        self.assertEqual(p["author"]["name"], "Vivek Bhange")
        self.assertEqual(p["repository"], f"https://github.com/vivekbhange-hub/{REPO_NAME}")
        self.assertTrue(6 <= len(p["keywords"]) <= 10)
        self.assertIn("claude-code", p["keywords"])
        self.assertIn("claude-skills", p["keywords"])


class DocsTests(unittest.TestCase):
    def test_readme_mentions_every_skill_and_agent(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for d in skill_dirs():
            self.assertIn(d.name, readme)
        for f in agent_files():
            self.assertIn(f.stem, readme)
        self.assertIn(f"/plugin marketplace add vivekbhange-hub/{REPO_NAME}", readme)

    def test_license(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT", text)
        self.assertIn("Copyright (c) 2026 Vivek Bhange", text)

    def test_required_files(self):
        for name in ("CONTRIBUTING.md", "CHANGELOG.md", ".gitignore"):
            self.assertTrue((ROOT / name).is_file(), name)
        self.assertIn("1.0.0", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        self.assertIn("2026-11-07", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_every_script_has_a_test(self):
        for script in (ROOT / "skills").glob("*/*.py"):
            with self.subTest(script=script.name):
                self.assertTrue((ROOT / "tests" / f"test_{script.stem}.py").is_file())


if __name__ == "__main__":
    unittest.main()
