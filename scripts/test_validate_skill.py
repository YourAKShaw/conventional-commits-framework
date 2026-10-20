#!/usr/bin/env python3
"""Regression checks for package integrity and trust boundaries; no network.

Run: python3 scripts/test_validate_skill.py
All mutations are confined to automatically cleaned temporary fixture copies.
"""

import importlib.util
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().with_name("validate-skill.py")
PACKAGE = SCRIPT.parent.parent
SPEC = importlib.util.spec_from_file_location("skill_validator", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class PackageValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill-validation-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "conventional-commits-framework"
        for relative in (*VALIDATOR.REQUIRED, "scripts/test_validate_skill.py"):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PACKAGE / relative, target)

    def append(self, relative, text):
        with (self.root / relative).open("a", encoding="utf-8") as handle:
            handle.write("\n" + text + "\n")

    def result(self):
        return VALIDATOR.validate(self.root)

    def assert_invalid(self, message):
        result = self.result()
        self.assertFalse(result["valid"], result)
        self.assertTrue(any(message in error for error in result["errors"]), result)

    def test_complete_package_and_templates_pass(self):
        self.assertTrue(self.result()["valid"], self.result())

    def test_missing_and_empty_resources_fail(self):
        (self.root / "assets/commit-template.txt").unlink()
        (self.root / "references/atomic-commits.md").write_text(" \n", encoding="utf-8")
        self.assert_invalid("missing required resource")
        self.assert_invalid("empty resource")

    def test_invalid_duplicate_and_ambiguous_manifests_fail(self):
        manifests = (
            "---\nname: conventional-commits-framework\nname: duplicate\ndescription: text\n---\nBody",
            "---\nname: conventional-commits-framework\ndescription: true\n---\nBody",
            '---\nname: conventional-commits-framework\ndescription: ""\n---\nBody',
            "---\nname: conventional-commits-framework\ndescription: |\n  text\n---\nBody",
            "---\nname: conventional-commits-framework\ndescription: text\n---\n",
        )
        for manifest in manifests:
            with self.subTest(manifest=manifest):
                with self.assertRaises(ValueError):
                    VALIDATOR.parse_manifest(manifest)
        entry = self.root / "SKILL.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            "name: conventional-commits-framework", "name: conventional--commits-framework"), encoding="utf-8")
        self.assert_invalid("single interior hyphens")

    def test_scalar_quote_formats_preserve_strings(self):
        for scalar, expected in (
            ('"Inspect APIs: report evidence"', "Inspect APIs: report evidence"),
            ("'Review a team''s code'", "Review a team's code"),
            ("Review production code", "Review production code"),
        ):
            manifest = "---\nname: conventional-commits-framework\ndescription: {}\n---\nBody".format(scalar)
            fields, _ = VALIDATOR.parse_manifest(manifest)
            self.assertEqual(fields["description"], expected)

    def test_description_limit_and_directory_identity(self):
        entry = self.root / "SKILL.md"
        original = entry.read_text(encoding="utf-8")
        entry.write_text('---\nname: conventional-commits-framework\ndescription: "' + "x" * 1025 + '"\n---\nBody', encoding="utf-8")
        self.assert_invalid("1024")
        entry.write_text(original.replace("name: conventional-commits-framework", "name: another-skill"), encoding="utf-8")
        self.assert_invalid("match skill directory")

    def test_broken_link_and_anchor_fail(self):
        self.append("SKILL.md", "[Missing](references/absent.md)\n[Bad anchor](references/agent-commit-protocol.md#absent)")
        self.assert_invalid("missing local target")
        self.assert_invalid("missing local heading anchor")

    def test_relative_and_duplicate_heading_anchors_work(self):
        self.append("references/agent-commit-protocol.md", "## Extra check\n## Extra check\n[Self](#extra-check-1)\n[Sibling](atomic-commits.md)")
        self.append("SKILL.md", "[Heading](references/agent-commit-protocol.md#extra-check)")
        self.assertTrue(self.result()["valid"], self.result())

    def test_encoded_path_traversal_is_rejected(self):
        outside = self.root.parent / "outside.md"
        outside.write_text("Private fixture", encoding="utf-8")
        self.append("SKILL.md", "[Escape](%2e%2e/outside.md)")
        self.assert_invalid("invalid local link")

    def test_file_and_directory_symlinks_are_rejected(self):
        outside = self.root.parent / "outside.md"
        outside.write_text("Private fixture", encoding="utf-8")
        try:
            (self.root / "references/escape.md").symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable on this platform")
        self.assert_invalid("symlinks are not portable")
        # A parent directory symlink must not make outside files readable either.
        shutil.rmtree(self.root / "assets")
        (self.root / "assets").symlink_to(self.root.parent, target_is_directory=True)
        self.assert_invalid("resource directory must not be a symlink")

    def test_orphan_resource_is_detected(self):
        (self.root / "references/orphan.md").write_text("# Unreachable\n", encoding="utf-8")
        self.assert_invalid("not discoverable")

    def test_fenced_examples_do_not_become_dependencies(self):
        self.append("SKILL.md", "```markdown\n[Example](absent.md)\n[TODO: example]\n```\n`[Literal](absent.md)`")
        self.assertTrue(self.result()["valid"], self.result())
        self.append("SKILL.md", "~~~markdown\nUnclosed example")
        self.assert_invalid("unclosed fenced")

    def test_scaffold_marker_is_distinct_from_explanation(self):
        self.append("SKILL.md", "Do not ship TODO implementations as functionality.")
        self.assertTrue(self.result()["valid"], self.result())
        self.append("SKILL.md", "[TODO: write real guidance]")
        self.assert_invalid("unfinished scaffold marker")

    def test_unsafe_scheme_and_unsupported_link_style_fail(self):
        self.append("SKILL.md", "[Unsafe](file:///tmp/private.md)\n[ref]: references/agent-commit-protocol.md")
        self.assert_invalid("unsupported local link or scheme")
        self.assert_invalid("use inline links")

    def test_cli_from_unrelated_directory_and_nonexistent_root(self):
        script = self.root / "scripts/validate-skill.py"
        completed = subprocess.run([sys.executable, str(script), "--json"],
                                   cwd=self.root.parent, capture_output=True, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["valid"])
        failed = subprocess.run([sys.executable, str(script), str(self.root / "missing"), "--json"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)["valid"])

    @unittest.skipUnless(shutil.which("sh"), "POSIX shell unavailable")
    def test_shell_wrapper_handles_spaces_and_preserves_failure_status(self):
        moved = self.root.parent / "location with spaces" / "conventional-commits-framework"
        shutil.copytree(self.root, moved)
        wrapper = moved / "scripts/validate-skill.sh"
        passed = subprocess.run([shutil.which("sh"), str(wrapper), "--json"],
                                cwd=self.root.parent, capture_output=True, text=True, check=False)
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)
        self.assertTrue(json.loads(passed.stdout)["valid"])
        (moved / "references/agent-commit-protocol.md").write_text("", encoding="utf-8")
        failed = subprocess.run([shutil.which("sh"), str(wrapper), str(moved), "--json"],
                                cwd=self.root.parent, capture_output=True, text=True, check=False)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertFalse(json.loads(failed.stdout)["valid"])

    def test_validation_does_not_change_package_contents(self):
        def snapshot():
            return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in self.root.rglob("*") if path.is_file()}
        before = snapshot()
        self.assertTrue(self.result()["valid"], self.result())
        self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
