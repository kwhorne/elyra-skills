#!/usr/bin/env python3
"""
Validate every skill in the registry against the Agent Skills spec
and the local registry.schema.json.

Checks performed:

  1. JSON syntax of registry.json and registry.schema.json
  2. registry.json validates against registry.schema.json
  3. Every skills/<name>/SKILL.md has valid frontmatter:
       - name present, lowercase + hyphens, <=64 chars, matches folder
       - description present, non-empty, <=1024 chars
       - license, if set, is a recognized SPDX-ish identifier
  4. Every skill in registry.json has a matching folder on disk
  5. Every folder under skills/ has a matching entry in registry.json
  6. Every skill's `path` field in registry.json resolves to its folder
  7. Every skill's description in registry.json matches the SKILL.md frontmatter
  8. scripts/ files (if any) are executable

Exits 0 if everything passes, 1 otherwise. Prints a grouped report.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "registry.json"
SCHEMA_PATH = ROOT / "registry.schema.json"
SKILLS_DIR = ROOT / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024

# Common SPDX identifiers we want to allow without a hard dependency on a SPDX list.
ALLOWED_LICENSES = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "CC0-1.0",
    "CC-BY-4.0",
    "MPL-2.0",
    "Unlicense",
}

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    GREEN = RED = YELLOW = BOLD = DIM = RESET = ""


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_passed: int = 0

    def fail(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self) -> None:
        self.checks_passed += 1


def parse_frontmatter(text: str) -> dict[str, Any] | None:
    """Tiny YAML frontmatter parser. Handles the subset used by SKILL.md files."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    block = text[4:end]

    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        # nested keys under `metadata:` — we only need to know they exist
        if line.startswith(" ") or line.startswith("\t"):
            if current_key == "metadata":
                # collect into metadata dict
                stripped = line.strip()
                if ":" in stripped:
                    k, _, v = stripped.partition(":")
                    data.setdefault("metadata", {})[k.strip()] = v.strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            current_key = key
            if value == "":
                # opening a nested key (e.g. metadata:)
                data[key] = {} if key == "metadata" else ""
            else:
                # strip wrapping quotes if any
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                data[key] = value
    return data


def load_json(path: Path, report: Report) -> Any | None:
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        report.ok()
        return data
    except FileNotFoundError:
        report.fail(f"missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as e:
        report.fail(f"{path.relative_to(ROOT)}: invalid JSON at line {e.lineno}: {e.msg}")
    return None


def validate_with_schema(instance: Any, schema: Any, report: Report) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        report.warn(
            "jsonschema not installed; skipping registry.json schema validation. "
            "Install with: pip install jsonschema"
        )
        return
    try:
        jsonschema.validate(instance=instance, schema=schema)
        report.ok()
    except jsonschema.ValidationError as e:
        path = "/".join(str(p) for p in e.absolute_path) or "<root>"
        report.fail(f"registry.json: schema validation failed at {path}: {e.message}")


def validate_skill_file(skill_dir: Path, report: Report) -> dict[str, Any] | None:
    rel = skill_dir.relative_to(ROOT)
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        report.fail(f"{rel}: missing SKILL.md")
        return None

    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as e:
        report.fail(f"{rel}/SKILL.md: cannot read ({e})")
        return None

    fm = parse_frontmatter(text)
    if fm is None:
        report.fail(f"{rel}/SKILL.md: missing or malformed frontmatter (must start with `---`)")
        return None

    parent = skill_dir.name

    # name
    name = fm.get("name", "")
    if not name:
        report.fail(f"{rel}/SKILL.md: frontmatter is missing `name`")
    else:
        if name != parent:
            report.fail(
                f"{rel}/SKILL.md: name `{name}` does not match folder `{parent}`"
            )
        if len(name) > MAX_NAME_LEN:
            report.fail(
                f"{rel}/SKILL.md: name length {len(name)} exceeds {MAX_NAME_LEN}"
            )
        if not NAME_RE.match(name):
            report.fail(
                f"{rel}/SKILL.md: name `{name}` invalid "
                "(must be lowercase a-z, 0-9, hyphens; no leading/trailing/double hyphens)"
            )

    # description
    desc = fm.get("description", "")
    if not desc or not str(desc).strip():
        report.fail(f"{rel}/SKILL.md: frontmatter is missing `description`")
    elif len(desc) > MAX_DESC_LEN:
        report.fail(
            f"{rel}/SKILL.md: description length {len(desc)} exceeds {MAX_DESC_LEN}"
        )

    # license (warn only — not all skills must declare one; repo MIT applies)
    license_id = fm.get("license")
    if license_id and license_id not in ALLOWED_LICENSES:
        report.warn(
            f"{rel}/SKILL.md: unrecognized license `{license_id}` "
            f"(allowed: {', '.join(sorted(ALLOWED_LICENSES))})"
        )

    # scripts must be executable
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.iterdir():
            if script.is_file() and not os.access(script, os.X_OK):
                report.fail(
                    f"{rel}/scripts/{script.name}: not executable "
                    f"(chmod +x {script.relative_to(ROOT)})"
                )

    if not report.errors or report.errors[-1].split(":")[0] != str(rel) + "/SKILL.md":
        report.ok()
    return fm


def validate_sync(registry: dict[str, Any], frontmatters: dict[str, dict[str, Any]], report: Report) -> None:
    skills = registry.get("skills", [])
    in_registry: dict[str, dict[str, Any]] = {s["name"]: s for s in skills if "name" in s}

    fs_names = set(frontmatters.keys())
    reg_names = set(in_registry.keys())

    for missing in fs_names - reg_names:
        report.fail(f"skills/{missing}/ exists but is not in registry.json")

    for orphan in reg_names - fs_names:
        report.fail(f"registry.json lists `{orphan}` but skills/{orphan}/ does not exist")

    # path field
    for name, entry in in_registry.items():
        expected = f"skills/{name}"
        if entry.get("path") != expected:
            report.fail(
                f"registry.json: skill `{name}` has path `{entry.get('path')}` "
                f"(expected `{expected}`)"
            )

    # description parity
    for name, entry in in_registry.items():
        fm = frontmatters.get(name)
        if not fm:
            continue
        fm_desc = fm.get("description", "").strip()
        reg_desc = entry.get("description", "").strip()
        if fm_desc and reg_desc and fm_desc != reg_desc:
            report.warn(
                f"`{name}`: description in registry.json differs from SKILL.md frontmatter"
            )

    if fs_names == reg_names:
        report.ok()


def main() -> int:
    report = Report()

    print(f"{BOLD}Validating elyra-skills registry{RESET}")
    print(f"  root: {DIM}{ROOT}{RESET}")
    print()

    # 1. Load registry + schema
    print(f"{BOLD}[1] Loading JSON files{RESET}")
    registry = load_json(REGISTRY_PATH, report)
    schema = load_json(SCHEMA_PATH, report)

    if registry is None or schema is None:
        return finish(report)

    # 2. Schema validation
    print(f"{BOLD}[2] Validating registry.json against schema{RESET}")
    validate_with_schema(registry, schema, report)

    # 3. Per-skill frontmatter
    print(f"{BOLD}[3] Validating SKILL.md frontmatter{RESET}")
    frontmatters: dict[str, dict[str, Any]] = {}
    if SKILLS_DIR.exists():
        for entry in sorted(SKILLS_DIR.iterdir()):
            if not entry.is_dir() or entry.name.startswith("."):
                continue
            fm = validate_skill_file(entry, report)
            if fm and fm.get("name"):
                frontmatters[fm["name"]] = fm
    else:
        report.fail(f"missing directory: {SKILLS_DIR.relative_to(ROOT)}")

    # 4. Registry <-> filesystem sync
    print(f"{BOLD}[4] Checking registry <-> filesystem sync{RESET}")
    validate_sync(registry, frontmatters, report)

    return finish(report)


def finish(report: Report) -> int:
    print()
    print(f"{BOLD}Summary{RESET}")
    print(f"  Checks passed: {GREEN}{report.checks_passed}{RESET}")
    print(f"  Warnings:      {YELLOW}{len(report.warnings)}{RESET}")
    print(f"  Errors:        {RED}{len(report.errors)}{RESET}")

    if report.warnings:
        print()
        print(f"{YELLOW}{BOLD}Warnings:{RESET}")
        for w in report.warnings:
            print(f"  {YELLOW}!{RESET} {w}")

    if report.errors:
        print()
        print(f"{RED}{BOLD}Errors:{RESET}")
        for e in report.errors:
            print(f"  {RED}x{RESET} {e}")
        print()
        print(f"{RED}{BOLD}Validation failed.{RESET}")
        return 1

    print()
    print(f"{GREEN}{BOLD}All checks passed.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
