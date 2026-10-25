#!/usr/bin/env python3
"""Repository hygiene checker for Gauge integrations (stdlib only, HA-free).

Checks the repository surface defined by ``canon/repository.md`` and
``canon/repository.schema.json``: the bilingual README pair, the My-Link,
the screenshot asset, metadata files, community files, CI gates and the
version triplet (git tag <-> ``manifest.version`` <-> ``CHANGELOG.md``).

Only files are inspected - GitHub settings (description, topics, issue
switch) cannot be verified from a checkout. The checker works on a plain
directory, never touches the network and never imports Home Assistant.

Usage:
    check_repo_hygiene.py <repo> [--warn-only] [--schema PATH]

Exit codes:
    0 = no errors (``--warn-only`` downgrades every finding to a warning)
    1 = at least one error, or an unreadable/missing repository path
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

CHECKER_VERSION = "1.7.0"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA = SCRIPT_DIR.parent / "canon" / "repository.schema.json"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PNG_IHDR_OFFSET = 16
GIT_TIMEOUT_SECONDS = 5
TAG_PATTERN = re.compile(r"^v?\d+\.\d+")
MY_LINK_URL_REGEX = (
    r"""my\.home-assistant\.io/redirect/(?:hacs|marketplace)_repository/"""
    r"""\?[^)\s"'<>]*"""
)
MY_LINK_REDIRECT_REGEX = (
    r"my\.home-assistant\.io/redirect/(?:hacs|marketplace)_repository/"
    r"\?[^)\s]*owner=[^&\s]+[^)\s]*repository=[^&\s]+"
)
MY_LINK_REQUIRED_QUERY = ["category=integration"]

DEFAULT_ROOT_FILES = [
    "README.md",
    "README.de.md",
    "LICENSE",
    "CHANGELOG.md",
    "hacs.json",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
]
DEFAULT_COMMUNITY_FILES = ["CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md"]
DEFAULT_HEADINGS = {
    "installation": ["installation"],
    "setup": ["setup", "einrichtung"],
    "troubleshooting": ["troubleshooting", "faq", "problembehebung"],
    "diagnostics": ["diagnostics", "diagnose"],
    "support": ["support"],
    "contributing": ["contributing", "mitwirken"],
    "security": ["security", "sicherheit"],
    "license": ["license", "lizenz"],
}
DEFAULT_MANIFEST_KEYS = [
    "domain",
    "name",
    "version",
    "documentation",
    "issue_tracker",
    "codeowners",
    "config_flow",
    "integration_type",
    "iot_class",
]


class Findings:
    """Collects findings and applies the ``--warn-only`` downgrade."""

    def __init__(self, warn_only: bool) -> None:
        self.warn_only = warn_only
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        """Record an error (a warning in ``--warn-only`` mode)."""
        if self.warn_only:
            self.warnings.append(message)
        else:
            self.errors.append(message)

    def warning(self, message: str) -> None:
        """Record a warning."""
        self.warnings.append(message)


def read_text(path: Path) -> str | None:
    """Read a UTF-8 file, returning ``None`` when it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def relative(repo: Path, path: Path) -> str:
    """Best-effort repository-relative path for messages."""
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def load_json(repo: Path, path: Path, findings: Findings) -> dict | None:
    """Load a JSON object and report unreadable/invalid content."""
    text = read_text(path)
    if text is None:
        findings.error(f"{relative(repo, path)}: file is missing or unreadable")
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        findings.error(f"{relative(repo, path)}: invalid JSON: {exc}")
        return None
    if not isinstance(data, dict):
        findings.error(f"{relative(repo, path)}: top-level JSON value must be an object")
        return None
    return data


def detect_domain(repo: Path, findings: Findings) -> str | None:
    """Return the single integration directory under ``custom_components``."""
    components = repo / "custom_components"
    try:
        domains = sorted(p for p in components.iterdir() if p.is_dir())
    except OSError:
        findings.error("custom_components/: directory is missing or unreadable")
        return None
    if len(domains) != 1:
        names = [p.name for p in domains]
        findings.error(
            "custom_components/ must contain exactly one integration directory, "
            f"found {len(domains)}: {names}"
        )
        return None
    return domains[0].name


def check_root_files(repo: Path, schema: dict, findings: Findings) -> None:
    """Check the required root files and the non-empty community files."""
    required = schema.get("required_root_files", DEFAULT_ROOT_FILES)
    for rel in required:
        if not (repo / rel).is_file():
            findings.error(f"required root file is missing: {rel}")

    community = schema.get("community_files", {})
    must_be_non_empty = community.get("must_be_non_empty", True)
    if not must_be_non_empty:
        return
    for rel in community.get("required", DEFAULT_COMMUNITY_FILES):
        path = repo / rel
        if not path.is_file():
            continue  # already reported by the root-file check
        text = read_text(path)
        if text is None or not text.strip():
            findings.error(f"community file is empty or unreadable: {rel}")


def check_github_files(repo: Path, schema: dict, findings: Findings) -> None:
    """Check issue/PR templates, CODEOWNERS and dependabot."""
    github = schema.get("github_files", {})

    for rel in github.get(
        "issue_templates",
        [
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/config.yml",
        ],
    ):
        if not (repo / rel).is_file():
            findings.error(f"issue template is missing: {rel}")

    pr_template = github.get("pull_request_template", ".github/PULL_REQUEST_TEMPLATE.md")
    if not (repo / pr_template).is_file():
        findings.error(f"pull request template is missing: {pr_template}")

    codeowners_rel = github.get("codeowners", ".github/CODEOWNERS")
    codeowners = read_text(repo / codeowners_rel)
    if codeowners is None:
        findings.error(f"CODEOWNERS is missing or unreadable: {codeowners_rel}")
    elif not re.search(r"@[A-Za-z0-9_.-]+", codeowners):
        findings.error(f"{codeowners_rel} must contain at least one '@handle' rule")

    dependabot_rel = github.get("dependabot", ".github/dependabot.yml")
    dependabot = read_text(repo / dependabot_rel)
    if dependabot is None:
        findings.error(f"dependabot config is missing or unreadable: {dependabot_rel}")
    else:
        if not re.search(r"(?m)^\s*version\s*:\s*2\s*$", dependabot):
            findings.error(f"{dependabot_rel} must declare 'version: 2'")
        if "package-ecosystem" not in dependabot:
            findings.error(f"{dependabot_rel} must declare a 'package-ecosystem'")

    workflow_rel = github.get("workflow", ".github/workflows/validate.yml")
    if not (repo / workflow_rel).is_file():
        findings.error(f"validation workflow is missing: {workflow_rel}")


def check_hacs(repo: Path, schema: dict, findings: Findings) -> dict | None:
    """Check ``hacs.json``: required keys, forbidden and legacy keys.

    ``render_readme`` is an error (no effect since HACS 2), while the optional
    legacy switches (``zip_release``, ``hide_default_branch``, ...) are only
    warned about - they are allowed when the release process really needs them,
    but the justification must be visible.
    """
    hacs_cfg = schema.get("hacs", {})
    rel = hacs_cfg.get("file", "hacs.json")
    data = load_json(repo, repo / rel, findings)
    if data is None:
        return None

    for key in hacs_cfg.get("required_keys", ["name", "homeassistant"]):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            findings.error(f"{rel}: '{key}' must be a non-empty string, got {value!r}")

    for key in hacs_cfg.get("forbidden_keys", ["render_readme"]):
        if key in data:
            findings.error(
                f"{rel}: legacy '{key}' key is forbidden by the hygiene contract"
            )

    for key in hacs_cfg.get(
        "warning_keys", ["zip_release", "hide_default_branch"]
    ):
        if key in data:
            findings.warning(
                f"{rel}: legacy/optional hacs.json key '{key}' present "
                "— must be justified"
            )
    return data


def resolve_git_tag(repo: Path) -> str | None:
    """Return a version tag for ``repo``, or ``None`` when unavailable.

    Resolution order:

    1. ``git describe --tags --abbrev=0`` - the closest **reachable** tag from
       ``HEAD``, i.e. the tag of the checked-out branch (authoritative).
    2. ``git describe --tags --abbrev=0 --always`` - same, but git falls back
       to a commit id when no tag is reachable. A non-version output (bare
       commit id) means "no version information" and is discarded instead of
       being compared against ``manifest.version``.
    3. ``git tag --sort=-v:refname`` - last resort only. This lookup is
       **repository-global**: it can return a tag that does not belong to the
       checked-out branch (e.g. a release tag of another branch), so its result
       is advisory at best.

    Every failure mode (missing git, shallow clone, no tags) returns ``None``;
    callers turn ``None`` into a warning, never an error.
    """
    commands = [
        ["git", "-C", str(repo), "describe", "--tags", "--abbrev=0"],
        ["git", "-C", str(repo), "describe", "--tags", "--abbrev=0", "--always"],
        ["git", "-C", str(repo), "tag", "--sort=-v:refname"],
    ]
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode != 0:
            continue
        for line in (line.strip() for line in result.stdout.splitlines()):
            if line and TAG_PATTERN.match(line):
                return line
    return None


def check_manifest(
    repo: Path,
    domain: str,
    schema: dict,
    findings: Findings,
    tag: str | None,
) -> dict | None:
    """Check ``manifest.json`` keys, categories shape and tag synchronisation."""
    manifest_cfg = schema.get("manifest", {})
    rel = manifest_cfg.get(
        "path", "custom_components/{domain}/manifest.json"
    ).format(domain=domain)
    path = repo / rel
    data = load_json(repo, path, findings)
    if data is None:
        return None

    for key in manifest_cfg.get("required_keys", DEFAULT_MANIFEST_KEYS):
        if key not in data or data[key] in ("", None, [], {}):
            findings.error(f"{rel}: required key '{key}' is missing or empty")

    if data.get("domain") not in (None, domain):
        findings.error(
            f"{rel}: 'domain' is {data.get('domain')!r} but the directory is '{domain}'"
        )

    categories = data.get("categories")
    if categories is not None:
        valid = (
            isinstance(categories, list)
            and 1 <= len(categories) <= 3
            and all(isinstance(item, str) and item.strip() for item in categories)
            and len(set(categories)) == len(categories)
        )
        if not valid:
            findings.error(
                f"{rel}: 'categories' must be 1-3 unique non-empty strings, "
                f"got {categories!r}"
            )

    version = data.get("version")
    if version is not None and not isinstance(version, str):
        findings.error(f"{rel}: 'version' must be a string, got {version!r}")
        version = str(version)
    if isinstance(version, str) and version.startswith("v"):
        findings.error(f"{rel}: 'version' must be bare SemVer without 'v', got {version!r}")

    if manifest_cfg.get("version_matches_git_tag", True):
        if tag is None:
            findings.warning(
                "Tag-Info nicht verfügbar — Tag↔Manifest nicht prüfbar"
            )
        elif isinstance(version, str) and version:
            tag_version = tag[1:] if tag.startswith("v") else tag
            if version != tag_version:
                findings.error(
                    f"{rel}: 'version' {version!r} != git tag {tag!r} "
                    f"(expected {tag_version!r})"
                )
    return data


def check_brand(
    repo: Path, domain: str, schema: dict, findings: Findings
) -> None:
    """Check the brand icon: real PNG, exactly 256x256 (IHDR, no Pillow)."""
    brand = schema.get("brand", {})
    rel = brand.get("icon", "custom_components/{domain}/brand/icon.png").format(
        domain=domain
    )
    path = repo / rel
    try:
        data = path.read_bytes()
    except OSError:
        findings.error(f"brand icon is missing or unreadable: {rel}")
        return
    if data[:8] != PNG_MAGIC:
        findings.error(f"{rel}: not a PNG (first bytes: {data[:8]!r})")
        return
    if len(data) < PNG_IHDR_OFFSET + 8:
        findings.error(f"{rel}: too small to hold an IHDR chunk")
        return
    width, height = struct.unpack(">II", data[PNG_IHDR_OFFSET : PNG_IHDR_OFFSET + 8])
    expected = (
        brand.get("width", 256),
        brand.get("height", 256),
    )
    if (width, height) != expected:
        findings.error(
            f"{rel}: is {width}x{height}px, expected {expected[0]}x{expected[1]}px"
        )


def check_my_link(
    rel: str,
    text: str,
    redirect_regex: str,
    required_query: list[str],
    findings: Findings,
) -> None:
    """Require one complete My-Link redirect URL.

    A bare token match is not enough: the URL must carry ``owner=`` and
    ``repository=`` in the documented order and the ``category=integration``
    parameter, otherwise the one-click install opens HACS with an empty or
    wrong form. ``hacs_repository`` (HACS < 2026.11) and
    ``marketplace_repository`` (Marketplace >= 2026.11) are both accepted as
    the redirect target.
    """
    try:
        redirect_pattern = re.compile(redirect_regex)
    except re.error as exc:
        findings.error(f"schema: invalid my_link_redirect_regex: {exc}")
        return
    for match in re.finditer(MY_LINK_URL_REGEX, text):
        url = match.group(0)
        if not redirect_pattern.search(url):
            continue
        if all(param in url for param in required_query):
            return
    findings.error(
        f"{rel}: missing a complete My-Link redirect "
        "(expected my.home-assistant.io/redirect/"
        "(hacs|marketplace)_repository/?owner=...&repository=...&category=integration)"
    )


def check_readme(repo: Path, schema: dict, findings: Findings) -> None:
    """Check the bilingual README pair, switcher, My-Link, screenshot, headings."""
    cfg = schema.get("readme", {})
    primary_rel = cfg.get("primary", "README.md")
    secondary_rel = cfg.get("secondary", "README.de.md")
    min_bytes = cfg.get("min_bytes_primary", 5000)
    redirect_regex = cfg.get("my_link_redirect_regex", MY_LINK_REDIRECT_REGEX)
    required_query = cfg.get("my_link_required_query", MY_LINK_REQUIRED_QUERY)
    hint = cfg.get("custom_repository_hint", "custom repositor").lower()
    headings = cfg.get("required_headings", DEFAULT_HEADINGS)

    texts: dict[str, str] = {}
    for rel in (primary_rel, secondary_rel):
        text = read_text(repo / rel)
        if text is None:
            findings.error(f"{rel}: README is missing or unreadable")
            continue
        texts[rel] = text

        lines = text.splitlines()
        first_line = lines[0].strip() if lines else ""
        if "README.de.md" not in first_line or "README.md" not in first_line:
            # One finding per cause: a structurally broken line 1 is not also
            # reported as a deviation from the canonical switcher.
            findings.error(
                f"{rel}: line 1 must be the language switcher linking "
                f"README.md and README.de.md, got {first_line!r}"
            )
        elif first_line != cfg.get(
            "language_switcher", "[English](README.md) | [Deutsch](README.de.md)"
        ):
            findings.warning(
                f"{rel}: line 1 differs from the canonical language switcher, "
                f"got {first_line!r}"
            )

        check_my_link(rel, text, redirect_regex, required_query, findings)

        screenshot_refs = re.findall(r'src="([^"]*docs/images/[^"]+)"', text)
        screenshot_refs += re.findall(r"\]\(([^)]*docs/images/[^)]+)\)", text)
        if not screenshot_refs:
            findings.error(
                f"{rel}: no screenshot referenced from docs/images/"
            )
        for ref in screenshot_refs:
            candidate = repo / ref.removeprefix("./")
            if not candidate.is_file():
                findings.error(f"{rel}: referenced screenshot does not exist: {ref}")

        for key, aliases in headings.items():
            alternatives = "|".join(re.escape(alias) for alias in aliases)
            if not re.search(rf"(?mi)^#{{1,6}}\s*[^\n]*\b(?:{alternatives})\b", text):
                findings.error(
                    f"{rel}: missing required heading '{key}' "
                    f"(accepted: {aliases})"
                )

        if hint not in text.lower():
            findings.error(
                f"{rel}: missing custom-repository hint (searched for {hint!r})"
            )

    primary = texts.get(primary_rel)
    if primary is not None and len(primary.encode("utf-8")) <= min_bytes:
        findings.error(
            f"{primary_rel}: only {len(primary.encode('utf-8'))} bytes, "
            f"expected more than {min_bytes} (truncated README?)"
        )


def check_ci(repo: Path, schema: dict, findings: Findings) -> None:
    """Check the validation workflow tokens, ignored gates and triggers.

    The tool gates (``hacs/action``, ``hassfest``, ``pytest``, ``ruff``,
    ``mypy``, ``check_json_consistency``, ``check_canon``) are mandatory - a
    missing token is an error. The recommended triggers (``schedule:``,
    ``workflow_dispatch:``) are advisory and only warn.
    """
    cfg = schema.get("ci", {})
    rel = cfg.get("file", ".github/workflows/validate.yml")
    text = read_text(repo / rel)
    if text is None:
        findings.error(f"{rel}: workflow is missing or unreadable")
        return

    for token in cfg.get(
        "required_tokens",
        [
            "hacs/action",
            "hassfest",
            "pytest",
            "ruff",
            "mypy",
            "check_json_consistency",
            "check_canon",
        ],
    ):
        if token not in text:
            findings.error(f"{rel}: required CI gate {token!r} is missing")

    for key in cfg.get("forbidden_keys", ["ignore"]):
        if re.search(rf"(?m)^\s*{re.escape(key)}\s*:", text):
            findings.error(f"{rel}: must not silence a gate with a '{key}:' key")

    for token in cfg.get("warning_if_missing", ["schedule:", "workflow_dispatch:"]):
        if token not in text:
            findings.warning(f"{rel}: recommended trigger {token!r} is missing")


def check_changelog(
    repo: Path, manifest: dict | None, schema: dict, findings: Findings
) -> None:
    """Check that ``CHANGELOG.md`` documents the manifest version."""
    cfg = schema.get("releases", {})
    rel = cfg.get("changelog", "CHANGELOG.md")
    text = read_text(repo / rel)
    if text is None:
        findings.error(f"{rel}: changelog is missing or unreadable")
        return
    version = (manifest or {}).get("version")
    if not isinstance(version, str) or not version:
        findings.error(f"{rel}: cannot check version block (manifest version missing)")
        return
    # Anchored tail: "2.0.2" must not match a heading such as "## [2.0.20]".
    heading = re.compile(
        rf"(?m)^##\s*\[?{re.escape(version)}\]?\s*(?:—|-|$)"
    )
    if not heading.search(text):
        findings.error(f"{rel}: no version heading for manifest version {version!r}")


def check_dashboards(repo: Path, schema: dict, findings: Findings) -> None:
    """Warn (never error) when the optional dashboard docs are absent."""
    cfg = schema.get("dashboards_docs", {})
    if not cfg.get("optional", True):
        return
    for rel in cfg.get(
        "files", ["docs/dashboards/README.md", "docs/dashboards/README.en.md"]
    ):
        if not (repo / rel).is_file():
            findings.warning(f"optional dashboard doc is missing: {rel}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", type=Path, help="integration repo root")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="downgrade every finding to a warning (exit 0 for convergence targets)",
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    repo: Path = args.repo
    header = f"check_repo_hygiene v{CHECKER_VERSION} — {repo}"

    if not repo.is_dir():
        print(header)
        print(f"ERROR: repository path not found or not a directory: {repo}")
        print("result: 1 error(s), 0 warning(s)")
        return 1
    try:
        list(repo.iterdir())
    except OSError as exc:
        print(header)
        print(f"ERROR: repository path is not readable: {repo}: {exc}")
        print("result: 1 error(s), 0 warning(s)")
        return 1

    if not args.schema.is_file():
        print(header)
        print(f"ERROR: schema not found or unreadable: {args.schema}")
        print("result: 1 error(s), 0 warning(s)")
        return 1
    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(header)
        print(f"ERROR: cannot read schema {args.schema}: {exc}")
        print("result: 1 error(s), 0 warning(s)")
        return 1

    findings = Findings(warn_only=args.warn_only)

    domain = detect_domain(repo, findings)
    check_root_files(repo, schema, findings)
    check_github_files(repo, schema, findings)
    check_hacs(repo, schema, findings)

    if domain is not None:
        tag = resolve_git_tag(repo)
        manifest = check_manifest(repo, domain, schema, findings, tag)
        check_brand(repo, domain, schema, findings)
        check_changelog(repo, manifest, schema, findings)

    check_readme(repo, schema, findings)
    check_ci(repo, schema, findings)
    check_dashboards(repo, schema, findings)

    print(header)
    for message in findings.warnings:
        print(f"WARNING: {message}")
    for message in findings.errors:
        print(f"ERROR: {message}")
    suffix = " (warn-only)" if findings.warn_only else ""
    print(
        f"result: {len(findings.errors)} error(s), "
        f"{len(findings.warnings)} warning(s){suffix}"
    )
    return 1 if findings.errors else 0


if __name__ == "__main__":
    sys.exit(main())
