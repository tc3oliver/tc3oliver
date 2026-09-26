import sys
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import update_oss_contributions as oss  # noqa: E402


def node(
    repo,
    number,
    state="OPEN",
    title="t",
    created="2026-09-01T00:00:00Z",
    merged_at=None,
    private=False,
    draft=False,
):
    owner = repo.split("/")[0]
    return {
        "number": number,
        "title": title,
        "url": f"https://github.com/{repo}/pull/{number}",
        "state": "MERGED" if state == "MERGED" else state,
        "merged": state == "MERGED",
        "isDraft": draft,
        "createdAt": created,
        "updatedAt": created,
        "mergedAt": merged_at,
        "repository": {"nameWithOwner": repo, "isPrivate": private, "owner": {"login": owner}},
    }


NODES = [
    node("up/core", 1, "OPEN", "Release the GIL"),
    node("up/omlx", 10, "MERGED", "fix: a", "2026-09-01T00:00:00Z", "2026-09-05T00:00:00Z"),
    node("up/omlx", 11, "MERGED", "fix: b", "2026-09-02T00:00:00Z", "2026-09-06T00:00:00Z"),
    node("up/omlx", 12, "OPEN", "feat: recover", "2026-09-10T00:00:00Z"),
    node("up/omlx", 13, "CLOSED", "feat: recover (old)", "2026-09-03T00:00:00Z"),
    node("up/omlx", 14, "OPEN", "test: split out", "2026-09-10T00:00:00Z"),
    node("up/omlx", 15, "CLOSED", "abandoned", "2026-09-04T00:00:00Z"),
    node(
        "other/lib",
        3,
        "MERGED",
        'parse "Error: <status>" [x] a_b',
        merged_at="2026-01-01T00:00:00Z",
    ),
    node("other/noise", 4, "MERGED", "typo", merged_at="2026-01-02T00:00:00Z"),
    node("me/own", 99, "MERGED", "own repo"),
    node("corp/secret", 5, "MERGED", "private", private=True),
]

CONFIG_TOML = """
author = "me"
projects = [
  { repo = "up/core", name = "Core" },
  { repo = "up/omlx", name = "oMLX" },
]
ignore = ["other/noise#4"]

[[superseded]]
pr = "up/omlx#13"
replaced_by = ["up/omlx#12", "up/omlx#14"]

[[selected]]
project = "Core"
prs = ["up/core#1"]
summary = "Core summary."

[[selected]]
project = "oMLX"
prs = ["up/omlx#12"]
summary = "Open one, listed first in config."

[[selected]]
project = "oMLX"
prs = ["up/omlx#10", "up/omlx#11"]
summary = "Two merged fixes."
"""
CONFIG = tomllib.loads(CONFIG_TOML)

README = """# Title

intro

<!-- OSS-SELECTED:START -->
stale
<!-- OSS-SELECTED:END -->

middle

<!-- OSS-AUTO:START -->
stale
<!-- OSS-AUTO:END -->

tail
"""


class FilterTest(unittest.TestCase):
    def test_excludes_own_and_private_repositories(self):
        prs = oss.parse_nodes(NODES, "me")
        self.assertNotIn("me/own#99", prs)
        self.assertNotIn("corp/secret#5", prs)
        self.assertIn("up/core#1", prs)

    def test_record_drops_superseded_ignored_and_closed(self):
        prs = oss.parse_nodes(NODES, "me")
        keys = {pr.key for pr in oss.active_record(CONFIG, prs)}
        self.assertNotIn("up/omlx#13", keys)  # superseded
        self.assertNotIn("other/noise#4", keys)  # ignored
        self.assertNotIn("up/omlx#15", keys)  # closed, never merged
        self.assertEqual(len(keys), 6)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.out = oss.render_readme(README, CONFIG, NODES)

    def section(self, name):
        start, end = oss.MARKERS[name]
        return self.out.split(start)[1].split(end)[0]

    def test_text_outside_markers_is_untouched(self):
        for text in ("# Title\n\nintro\n\n", "\n\nmiddle\n\n", "\n\ntail\n"):
            self.assertIn(text, self.out)

    def test_counts_are_computed(self):
        record = self.section("record")
        self.assertIn("6 pull requests to projects I don't maintain: 3 merged · 3 open.", record)
        self.assertIn("**oMLX** — 2 merged · 2 open", record)

    def test_superseded_is_listed_once_and_not_counted(self):
        record = self.section("record")
        self.assertEqual(record.count("up/omlx/pull/13)"), 1)
        self.assertIn("<summary>Superseded, not counted</summary>", record)

    def test_selected_keeps_curation_and_puts_merged_first(self):
        selected = self.section("selected")
        self.assertNotIn("other/lib", selected)
        self.assertLess(selected.index("Two merged fixes."), selected.index("Open one"))
        self.assertIn("- **Merged** · [#10]", selected)
        self.assertIn("- Open · [#1]", selected)

    def test_titles_are_escaped(self):
        self.assertIn('parse "Error: &lt;status&gt;" \\[x\\] a\\_b', self.section("record"))

    def test_link_titles_cannot_break_the_link_or_add_markers(self):
        self.assertEqual(oss.link_title('a "b" c\\'), 'a \\"b\\" c\\\\')
        self.assertNotIn("<!--", oss.link_title("<!-- OSS-AUTO:END -->"))

    def test_second_run_is_a_no_op(self):
        self.assertEqual(oss.render_readme(self.out, CONFIG, NODES), self.out)

    def test_order_does_not_depend_on_api_order(self):
        self.assertEqual(oss.render_readme(README, CONFIG, list(reversed(NODES))), self.out)


class SafetyTest(unittest.TestCase):
    def test_missing_marker_fails(self):
        broken = README.replace("<!-- OSS-AUTO:END -->", "")
        with self.assertRaises(oss.UpdateError):
            oss.render_readme(broken, CONFIG, NODES)

    def test_reversed_markers_fail(self):
        broken = "<!-- OSS-AUTO:END -->\n<!-- OSS-AUTO:START -->\n" + README.split("middle")[0]
        with self.assertRaises(oss.UpdateError):
            oss.render_readme(broken, CONFIG, NODES)

    def test_selected_pr_missing_from_api_fails(self):
        partial = [n for n in NODES if n["number"] != 12]
        with self.assertRaises(oss.UpdateError):
            oss.render_readme(README, CONFIG, partial)

    def test_empty_api_result_fails(self):
        with self.assertRaises(oss.UpdateError):
            oss.render_readme(README, CONFIG, [])

    def test_selected_closed_pr_fails(self):
        config = dict(CONFIG, selected=[{"project": "oMLX", "prs": ["up/omlx#15"], "summary": "x"}])
        with self.assertRaises(oss.UpdateError):
            oss.render_readme(README, config, NODES)


class CommandLineTest(unittest.TestCase):
    def test_check_and_dry_run_never_write(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            readme, config, data = (Path(tmp) / name for name in ("R.md", "c.toml", "n.json"))
            readme.write_text(README)
            config.write_text(CONFIG_TOML)
            data.write_text(json.dumps(NODES))
            common = ["--readme", str(readme), "--config", str(config), "--input", str(data)]
            self.assertEqual(oss.main(common + ["--check"]), 1)
            self.assertEqual(oss.main(common + ["--dry-run"]), 0)
            self.assertEqual(readme.read_text(), README)
            self.assertEqual(oss.main(common), 0)
            self.assertEqual(oss.main(common + ["--check"]), 0)
            broken = readme.read_text().replace("<!-- OSS-AUTO:END -->", "")
            readme.write_text(broken)
            self.assertEqual(oss.main(common), 2)
            self.assertEqual(readme.read_text(), broken)


if __name__ == "__main__":
    unittest.main()
