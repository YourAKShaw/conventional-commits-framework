#!/usr/bin/env python3
"""Read-only package validation for this skill, using Python 3.9+ standard library only.

Usage: python3 scripts/validate-skill.py [SKILL_ROOT] [--json]
Exit status: 0 valid, 1 validation errors, 2 command-line usage error.

This is deliberately a validator for this package, not a general YAML or Markdown parser.
The manifest supports exactly name and description as single-line scalars:
plain strings, YAML single quotes, or JSON-compatible double quotes. Use inline
Markdown links (optional double-quoted titles); reference-style links are rejected
so dependencies cannot silently escape validation. Fenced examples are ignored.
No network, subprocess execution, installation or filesystem writes occur.
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED = (
    "SKILL.md",
    "references/agent-commit-protocol.md",
    "references/atomic-commits.md",
    "references/type-scope-catalog.md",
    "references/breaking-changes.md",
    "references/example-library.md",
    "references/rules-reference.md",
    "references/config-guide.md",
    "references/monorepo-patterns.md",
    "references/emoji-reference.md",
    "references/integration-examples.md",
    "assets/commitlint.config.mjs",
    "assets/commit-template.txt",
    "scripts/lint-commit.py",
    "scripts/test_lint_commit.py",
    "scripts/validate-skill.py",
    "scripts/validate-skill.sh",
    "scripts/validate-skill.ps1",
    "scripts/test_validate_skill.py",
)
RESOURCE_DIRS = ("references", "assets", "scripts")
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(([^\n)]*)\)")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")


def parse_manifest(text):
    """Parse the intentionally narrow manifest format without guessing YAML."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with a YAML frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("frontmatter has no closing delimiter") from None
    fields = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z-]*):\s+(.+)", line)
        if not match:
            raise ValueError("use single-line 'name: value' and 'description: value' fields")
        key, value = match.groups()
        if key not in {"name", "description"}:
            raise ValueError("unsupported field {!r}; extend the parser before adding metadata".format(key))
        if key in fields:
            raise ValueError("duplicate frontmatter field: " + key)
        value = value.strip()
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError("double-quoted scalars must use JSON-compatible escaping") from exc
        elif value.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                raise ValueError("invalid single-quoted scalar")
            value = value[1:-1].replace("''", "'")
        elif (
            value[0] in "!&*{}[]|>@`%"
            or ": " in value
            or " #" in value
            or value.lower() in {"true", "false", "null", "~", "yes", "no", "on", "off"}
            or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value)
        ):
            raise ValueError("ambiguous plain scalar; quote it as a string")
        if not isinstance(value, str) or not value.strip():
            raise ValueError(key + " must be a nonempty string")
        fields[key] = value
    if set(fields) != {"name", "description"}:
        raise ValueError("frontmatter requires name and description")
    if not "\n".join(lines[end + 1:]).strip():
        raise ValueError("SKILL.md has no instruction body")
    return fields, "\n".join(lines[end + 1:])


def prose_lines(text):
    """Yield numbered non-fenced lines; reject an incomplete fenced example."""
    marker = None
    length = 0
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if match:
            fence, tail = match.groups()
            if marker is None:
                marker, length = fence[0], len(fence)
            elif fence[0] == marker and len(fence) >= length and not tail.strip():
                marker = None
            continue
        if marker is None:
            yield number, line
    if marker is not None:
        raise ValueError("unclosed fenced code block")


def heading_anchors(lines):
    """Compute GitHub-style anchors for the package's ordinary ATX headings."""
    counts = {}
    anchors = set()
    for _, line in lines:
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        heading = match.group(1).lower()
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        slug = "".join(
            char for char in heading
            if char in " -_" or unicodedata.category(char)[0] in {"L", "N", "M"}
        ).replace(" ", "-")
        index = counts.get(slug, 0)
        counts[slug] = index + 1
        anchors.add(slug if index == 0 else "{}-{}".format(slug, index))
    return anchors


def validate(root):
    errors = []
    warnings = []
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        return {"valid": False, "root": str(root), "files_checked": 0,
                "errors": ["skill root is not a directory"], "warnings": []}

    paths = {Path("SKILL.md")}

    def inventory(directory):
        try:
            children = sorted(directory.iterdir())
        except OSError as exc:
            errors.append("cannot list {}: {}".format(directory.relative_to(root), exc))
            return
        for path in children:
            relative = path.relative_to(root)
            if path.name == "__pycache__":
                continue
            if path.is_symlink():
                errors.append("{}: symlinks are not portable package resources".format(relative))
            elif path.is_dir():
                inventory(path)
            elif path.is_file():
                paths.add(relative)

    for dirname in RESOURCE_DIRS:
        directory = root / dirname
        if directory.is_symlink():
            errors.append(dirname + ": resource directory must not be a symlink")
        elif directory.is_dir():
            inventory(directory)

    contents = {}
    for relative in sorted(paths | {Path(item) for item in REQUIRED}):
        path = root / relative
        # Do not read external files through either file or ancestor symlinks.
        if any(part.is_symlink() for part in (path, *path.parents)):
            errors.append(str(relative) + ": resource path contains a symlink")
            continue
        if not path.is_file():
            errors.append("missing required resource: " + str(relative))
            continue
        try:
            data = path.read_bytes()
            if not data.strip():
                errors.append(str(relative) + ": empty resource")
                continue
            if path.suffix in {".md", ".py", ".sh", ".ps1", ".mjs", ".txt"}:
                contents[relative] = data.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append("{}: cannot read UTF-8 resource: {}".format(relative, exc))

    entry = Path("SKILL.md")
    if entry in contents:
        try:
            fields, _ = parse_manifest(contents[entry])
            name = fields["name"]
            if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
                errors.append("name must be 1–64 lowercase letters/digits with single interior hyphens")
            if name != root.name:
                errors.append("manifest name must match skill directory name: " + root.name)
            if len(fields["description"]) > 1024:
                errors.append("description exceeds 1024 characters")
            if re.search(r"\[(?:TODO|TBD|FIXME)[:\]]", fields["description"]):
                errors.append("description contains an unfinished scaffold marker")
        except ValueError as exc:
            errors.append(str(exc))
        if len(contents[entry].splitlines()) >= 500:
            warnings.append("SKILL.md should stay under 500 lines for progressive disclosure")

    docs = {}
    anchors = {}
    graph = {relative: set() for relative in paths}
    for relative, content in contents.items():
        if relative.suffix != ".md":
            continue
        try:
            lines = list(prose_lines(content))
            docs[relative] = lines
            anchors[relative] = heading_anchors(lines)
        except ValueError as exc:
            errors.append("{}: {}".format(relative, exc))
            continue
        for number, line in lines:
            if relative.parts[0] != "assets" and re.match(
                r"^\s*(?:[-*+]\s+|#{1,6}\s+)?(?:\[(?:TODO|TBD|FIXME)[:\]]|(?:TODO|TBD|FIXME)(?::|\s*$))", line
            ):
                errors.append("{}:{}: unfinished scaffold marker".format(relative, number))
            if re.match(r"^\s*\[[^]]+\]:", line):
                errors.append("{}:{}: use inline links for package validation".format(relative, number))

    for relative, lines in docs.items():
        for number, line in lines:
            # Inline code may contain literal Markdown examples, not dependencies.
            line = re.sub(r"(`+).*?\1", "", line)
            for match in INLINE_LINK.finditer(line):
                location = "{}:{}".format(relative, number)
                destination = re.fullmatch(r'\s*(<[^>]+>|[^\s]+)(?:\s+"[^"]*")?\s*', match.group(1))
                if not destination:
                    errors.append(location + ": unsupported/empty link destination")
                    continue
                target = destination.group(1).removeprefix("<").removesuffix(">")
                try:
                    url = urlsplit(target)
                    if url.scheme in {"https", "http", "mailto", "tel"}:
                        continue  # External links are never fetched.
                    if url.scheme or url.netloc or url.query or "\\" in target:
                        raise ValueError("unsupported local link or scheme: " + target)
                    candidate = ((root / relative).parent / unquote(url.path)).resolve() if url.path else root / relative
                    dependency = candidate.relative_to(root)
                    if not candidate.is_file():
                        raise ValueError("missing local target: " + target)
                    if dependency not in contents:
                        raise ValueError("target is not a packaged text resource: " + target)
                    if url.fragment and unquote(url.fragment) not in anchors.get(dependency, set()):
                        raise ValueError("missing local heading anchor: " + target)
                    graph.setdefault(relative, set()).add(dependency)
                except (ValueError, OSError, RuntimeError) as exc:
                    errors.append("{}: invalid local link {} ({})".format(location, target, exc))

    reachable = set()
    pending = deque([entry])
    while pending:
        current = pending.popleft()
        if current in reachable:
            continue
        reachable.add(current)
        pending.extend(graph.get(current, ()))
    for relative in sorted(paths - reachable):
        errors.append(str(relative) + ": not discoverable through links from SKILL.md")

    return {"valid": not errors, "root": str(root), "files_checked": len(contents),
            "errors": errors, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="skill directory (default: this script's parent package)")
    parser.add_argument("--json", action="store_true", help="emit a structured result")
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except (OSError, RuntimeError) as exc:
        result = {"valid": False, "root": str(args.root), "files_checked": 0,
                  "errors": ["cannot inspect package: " + str(exc)], "warnings": []}
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("{}: conventional-commits-framework package ({} text files checked)".format(
            "PASS" if result["valid"] else "FAIL", result["files_checked"]))
        for item in result["errors"]:
            print("ERROR: " + item)
        for item in result["warnings"]:
            print("WARNING: " + item)
        print("Structural validation only; agent behavior and external URLs are not verified.")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
