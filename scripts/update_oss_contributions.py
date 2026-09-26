#!/usr/bin/env python3
"""Regenerate the OSS sections of README.md from GitHub.

Reads data/oss-contributions.toml, fetches every pull request authored by the
configured user through the GraphQL API, and rewrites only the text between
the OSS-SELECTED and OSS-AUTO markers. Everything else in the README is left
byte for byte.

The script only reads public metadata: it never checks out or runs pull
request code, and the token it is given is sent to api.github.com only.

Usage:
  update_oss_contributions.py              fetch, then rewrite README.md
  update_oss_contributions.py --dry-run    fetch, print the diff, write nothing
  update_oss_contributions.py --check      exit 1 if README.md is out of date
  update_oss_contributions.py --input prs.json   use saved data, no network
"""

from __future__ import annotations

import argparse
import difflib
import http.client
import json
import os
import sys
import time
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPHQL_URL = "https://api.github.com/graphql"
OTHER_PROJECTS = "Other projects"
MARKERS = {
    "selected": ("<!-- OSS-SELECTED:START -->", "<!-- OSS-SELECTED:END -->"),
    "record": ("<!-- OSS-AUTO:START -->", "<!-- OSS-AUTO:END -->"),
}

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    pullRequests(first: 100, after: $after) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title url state merged isDraft createdAt updatedAt mergedAt
        repository { nameWithOwner isPrivate owner { login } }
      }
    }
  }
}
"""


class UpdateError(Exception):
    """Anything that must stop the run before README.md is touched."""


@dataclass(frozen=True)
class PR:
    repo: str
    number: int
    title: str
    url: str
    state: str  # OPEN, CLOSED or MERGED
    draft: bool
    created: str
    merged_at: str | None

    @property
    def key(self) -> str:
        return f"{self.repo}#{self.number}"

    @property
    def merged(self) -> bool:
        return self.state == "MERGED"

    @property
    def open(self) -> bool:
        return self.state == "OPEN"


# --- fetching ---------------------------------------------------------------


def _post(payload: dict, token: str, attempts: int = 3) -> dict:
    body = json.dumps(payload).encode()
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            GRAPHQL_URL,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "tc3oliver-profile-oss-update",
            },
        )
        # Unredirected: a redirect never carries the token to another host.
        request.add_unredirected_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.load(response)
        except (OSError, http.client.HTTPException, json.JSONDecodeError) as error:
            retryable = not isinstance(error, urllib.error.HTTPError) or error.code >= 500
            if retryable and attempt < attempts:
                time.sleep(2**attempt)
                continue
            raise UpdateError(f"GitHub API request failed: {error}") from None
        if data.get("errors"):
            raise UpdateError(f"GitHub API returned errors: {data['errors']}")
        return data
    raise AssertionError("unreachable")


def fetch_pull_requests(login: str, token: str) -> list[dict]:
    nodes: list[dict] = []
    after = None
    while True:
        data = _post({"query": QUERY, "variables": {"login": login, "after": after}}, token)
        user = (data.get("data") or {}).get("user")
        if user is None:
            raise UpdateError(f"GitHub user {login!r} not found")
        page = user["pullRequests"]
        nodes.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        after = page["pageInfo"]["endCursor"]


# --- filtering --------------------------------------------------------------


def parse_nodes(nodes: list[dict], author: str) -> dict[str, PR]:
    """Public pull requests outside the author's own repositories, by key."""
    prs: dict[str, PR] = {}
    for node in nodes:
        repo = node["repository"]
        if repo["isPrivate"] or repo["owner"]["login"].lower() == author.lower():
            continue
        pr = PR(
            repo=repo["nameWithOwner"],
            number=node["number"],
            title=node["title"].strip(),
            url=node["url"],
            state="MERGED" if node["merged"] else node["state"],
            draft=node["isDraft"],
            created=node["createdAt"],
            merged_at=node.get("mergedAt"),
        )
        prs[pr.key] = pr
    return prs


def _require(prs: dict[str, PR], key: str, where: str) -> PR:
    if key not in prs:
        raise UpdateError(
            f"{key} ({where}) is not among the public external pull requests "
            f"fetched for this author; refusing to write a partial README"
        )
    return prs[key]


def validate_config(config: dict, prs: dict[str, PR]) -> None:
    superseded = {entry["pr"] for entry in config.get("superseded", [])}
    ignored = set(config.get("ignore", []))
    for entry in config.get("superseded", []):
        _require(prs, entry["pr"], "superseded")
        for key in entry["replaced_by"]:
            _require(prs, key, f"replacement for {entry['pr']}")
    for entry in config.get("selected", []):
        for key in entry["prs"]:
            pr = _require(prs, key, "selected")
            if key in superseded or key in ignored:
                raise UpdateError(f"{key} is selected but also superseded or ignored")
            if pr.state == "CLOSED":
                raise UpdateError(f"{key} is selected but closed without merging")


def active_record(config: dict, prs: dict[str, PR]) -> list[PR]:
    """Pull requests that count: merged or open, not ignored, not superseded."""
    excluded = set(config.get("ignore", []))
    excluded |= {entry["pr"] for entry in config.get("superseded", [])}
    return [pr for pr in prs.values() if pr.key not in excluded and pr.state != "CLOSED"]


# --- rendering --------------------------------------------------------------

_ESCAPES = str.maketrans(
    {
        "\\": "\\\\",
        "&": "&amp;",
        "~": "\\~",
        "<": "&lt;",
        ">": "&gt;",
        "[": "\\[",
        "]": "\\]",
        "*": "\\*",
        "_": "\\_",
        "`": "\\`",
        "|": "\\|",
    }
)


def md_escape(text: str) -> str:
    return text.translate(_ESCAPES)


def link_title(text: str) -> str:
    """Escape a title for a Markdown link title in double quotes."""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("&", "&amp;").replace("<", "&lt;")


def ordered(prs: list[PR]) -> list[PR]:
    """Merged first, most recently merged first; then open, newest first."""
    merged = sorted(
        (pr for pr in prs if pr.merged), key=lambda pr: (pr.merged_at or "", pr.number, pr.repo)
    )
    opened = sorted(
        (pr for pr in prs if not pr.merged), key=lambda pr: (pr.created, pr.number, pr.repo)
    )
    return merged[::-1] + opened[::-1]


def counts(prs: list[PR]) -> str:
    merged = sum(pr.merged for pr in prs)
    opened = sum(pr.open for pr in prs)
    parts = []
    if merged:
        parts.append(f"{merged} merged")
    if opened:
        parts.append(f"{opened} open")
    return " · ".join(parts)


def _link(pr: PR, qualified: bool) -> str:
    label = pr.key if qualified else f"#{pr.number}"
    return f"[{label}]({pr.url})"


def render_selected(config: dict, prs: dict[str, PR]) -> str:
    groups: dict[str, list[dict]] = {}
    for entry in config.get("selected", []):
        groups.setdefault(entry["project"], []).append(entry)
    blocks = []
    for project, entries in groups.items():
        lines = [f"**{project}**", ""]
        rendered = []
        for position, entry in enumerate(entries):
            members = [prs[key] for key in entry["prs"]]
            merged = sum(pr.merged for pr in members)
            if merged == len(members):
                status = "**Merged**"
            elif merged:
                status = f"{merged} of {len(members)} merged"
            else:
                status = "Open"
            links = " + ".join(
                f'[#{pr.number}]({pr.url} "{link_title(pr.title)}")' for pr in members
            )
            rendered.append(
                (merged != len(members), position, f"- {status} · {links} — {entry['summary']}")
            )
        lines += [line for _, _, line in sorted(rendered)]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def render_record(config: dict, prs: dict[str, PR]) -> str:
    record = active_record(config, prs)
    names = {p["repo"]: p["name"] for p in config.get("projects", [])}
    order = [p["name"] for p in config.get("projects", [])] + [OTHER_PROJECTS]
    groups: dict[str, list[PR]] = {name: [] for name in order}
    for pr in record:
        groups[names.get(pr.repo, OTHER_PROJECTS)].append(pr)

    noun = "pull request" if len(record) == 1 else "pull requests"
    lines = [
        f"{len(record)} {noun} to projects I don't maintain: {counts(record) or 'none active'}."
    ]
    for name in order:
        members = ordered(groups[name])
        if not members:
            continue
        lines += ["", f"**{name}** — {counts(members)}", ""]
        for pr in members:
            mark = "✓" if pr.merged else "○"
            draft = " (draft)" if pr.draft else ""
            lines.append(
                f"- {mark} {_link(pr, name == OTHER_PROJECTS)} {md_escape(pr.title)}{draft}"
            )

    superseded = config.get("superseded", [])
    if superseded:
        lines += ["", "<details>", "<summary>Superseded, not counted</summary>", ""]
        for entry in sorted(superseded, key=lambda e: e["pr"]):
            pr = prs[entry["pr"]]
            replacements = ", ".join(_link(prs[key], False) for key in entry["replaced_by"])
            lines.append(f"- {_link(pr, True)} {md_escape(pr.title)} — replaced by {replacements}")
        lines += ["", "</details>"]
    return "\n".join(lines)


def replace_section(readme: str, name: str, content: str) -> str:
    start, end = MARKERS[name]
    if readme.count(start) != 1 or readme.count(end) != 1:
        raise UpdateError(f"README.md must contain {start} and {end} exactly once each")
    if readme.index(end) < readme.index(start):
        raise UpdateError(f"{end} appears before {start} in README.md")
    head, rest = readme.split(start)
    _, tail = rest.split(end)
    return f"{head}{start}\n{content}\n{end}{tail}"


def render_readme(readme: str, config: dict, nodes: list[dict]) -> str:
    prs = parse_nodes(nodes, config["author"])
    if not prs:
        raise UpdateError("no public external pull requests fetched; refusing to write")
    validate_config(config, prs)
    readme = replace_section(readme, "selected", render_selected(config, prs))
    return replace_section(readme, "record", render_record(config, prs))


# --- command line -----------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--readme", type=Path, default=ROOT / "README.md")
    parser.add_argument("--config", type=Path, default=ROOT / "data" / "oss-contributions.toml")
    parser.add_argument("--input", type=Path, help="read pull requests from a JSON file")
    parser.add_argument("--save-input", type=Path, help="also save fetched pull requests as JSON")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="print the diff, write nothing")
    mode.add_argument("--check", action="store_true", help="exit 1 if README.md would change")
    args = parser.parse_args(argv)

    try:
        try:
            config = tomllib.loads(args.config.read_text(encoding="utf-8"))
            nodes = json.loads(args.input.read_text(encoding="utf-8")) if args.input else None
            before = args.readme.read_text(encoding="utf-8")
        except (OSError, ValueError) as error:
            raise UpdateError(f"cannot read input: {error}") from None
        if nodes is None:
            token = os.environ.get("GITHUB_TOKEN")
            if not token:
                raise UpdateError("GITHUB_TOKEN is not set")
            nodes = fetch_pull_requests(config["author"], token)
        if args.save_input:
            args.save_input.write_text(
                json.dumps(nodes, indent=1, sort_keys=True) + "\n", encoding="utf-8"
            )
        after = render_readme(before, config, nodes)
    except (UpdateError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if after == before:
        print("README.md is up to date")
        return 0
    if args.dry_run or args.check:
        sys.stdout.writelines(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                "README.md",
                "README.md (generated)",
            )
        )
        return 1 if args.check else 0
    args.readme.write_text(after, encoding="utf-8")
    print("README.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
