#!/usr/bin/env python3
"""Regression tests for lint-commit.py. Run: python3 scripts/test_lint_commit.py"""

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("lint_commit", Path(__file__).with_name("lint-commit.py"))
lint_commit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lint_commit)

TRAILER = "Co-Authored-By: Claude Code <noreply@anthropic.com>"
CHATGPT_TRAILER = "Co-Authored-By: ChatGPT <noreply@openai.com>"
BODY = "Explain the reason for the change in one or two full sentences."


def message(header="feat(auth): add passkey sign-in flow", body=BODY, trailers=("Breaking: none", TRAILER)):
    parts = [header]
    if body is not None:
        parts += ["", body]
    if trailers:
        parts += ["", "\n".join(trailers)]
    return "\n".join(parts) + "\n"


def rules(text, **kwargs):
    errors, _ = lint_commit.lint(text, trailer=kwargs.pop("trailer", (TRAILER, CHATGPT_TRAILER)), **kwargs)
    return {rule for rule, _ in errors}


class ValidMessages(unittest.TestCase):
    def test_complete_message_passes(self):
        self.assertEqual(rules(message()), set())

    def test_chatgpt_agent_trailer_passes(self):
        self.assertEqual(rules(message(trailers=("Breaking: none", CHATGPT_TRAILER))), set())

    def test_breaking_change_with_continuation_passes(self):
        text = message(
            header="feat(api)!: remove legacy v1 login endpoint",
            trailers=("BREAKING-CHANGE: /v1/login is gone; clients must call", "  /v2/sessions instead.", "Refs: #42", TRAILER),
        )
        self.assertEqual(rules(text), set())

    def test_gitmoji_shortcode_and_unicode_prefix_pass(self):
        self.assertEqual(rules(message(header="fix(cache): :bug: evict stale keys on write")), set())
        self.assertEqual(rules(message(header="fix(cache): 🐛 evict stale keys on write")), set())

    def test_comments_and_scissors_are_ignored(self):
        text = message() + "# Please enter the commit message\n" + lint_commit.SCISSORS + "\ndiff --git a b\n"
        self.assertEqual(rules(text), set())

    def test_merge_messages_are_skipped(self):
        self.assertEqual(rules("Merge branch 'main' into topic\n"), set())


class InvalidMessages(unittest.TestCase):
    def test_missing_scope(self):
        self.assertIn("scope-empty", rules(message(header="feat: add passkey sign-in flow")))

    def test_unknown_type(self):
        self.assertIn("type-enum", rules(message(header="feature(auth): add passkey sign-in flow")))

    def test_long_header(self):
        self.assertIn("header-max-length", rules(message(header="feat(auth): " + "x" * 70)))

    def test_vague_or_short_subject(self):
        self.assertIn("subject-vague", rules(message(header="fix(auth): fixes")))
        self.assertIn("subject-min-length", rules(message(header="fix(auth): typo")))

    def test_capitalised_subject_and_period(self):
        found = rules(message(header="feat(auth): Add passkey sign-in flow."))
        self.assertTrue({"subject-case", "subject-full-stop"} <= found)

    def test_missing_or_thin_body(self):
        self.assertIn("body-empty", rules(message(body=None)))
        self.assertIn("body-empty", rules(message(body="Adds it.")))

    def test_missing_breaking_declaration(self):
        self.assertIn("breaking-declared", rules(message(trailers=(TRAILER,))))

    def test_spaced_breaking_token_is_rejected(self):
        text = message(header="feat(api)!: remove legacy v1 login endpoint",
                       trailers=("BREAKING CHANGE: /v1/login is gone; use /v2/sessions.", TRAILER))
        self.assertEqual(rules(text), {"breaking-token"})

    def test_bang_without_footer_and_footer_without_bang(self):
        self.assertIn("breaking-change-exclamation-mark", rules(message(header="feat(api)!: remove legacy v1 login")))
        text = message(trailers=("BREAKING-CHANGE: sessions now expire after one hour.", TRAILER))
        self.assertIn("breaking-change-exclamation-mark", rules(text))

    def test_breaking_none_must_be_exact(self):
        self.assertIn("breaking-declared", rules(message(trailers=("Breaking: no", TRAILER))))

    def test_co_author_required_and_exact(self):
        self.assertIn("co-author", rules(message(trailers=("Breaking: none",))))
        other = "Co-authored-by: Claude Code <noreply@anthropic.com>"
        self.assertIn("co-author-pattern", rules(message(trailers=("Breaking: none", other))))

    def test_human_pair_and_agent_both_allowed(self):
        human = "Co-Authored-By: Jordan Lee <jordan.lee@example.com>"
        self.assertEqual(rules(message(trailers=("Breaking: none", human, TRAILER))), set())

    def test_varied_agent_trailer_alongside_canonical_is_rejected(self):
        variant = "Co-Authored-By: Claude <noreply@anthropic.com>"
        self.assertIn("co-author-pattern", rules(message(trailers=("Breaking: none", variant, TRAILER))))

    def test_unknown_agent_trailer_is_rejected(self):
        other = "Co-Authored-By: Other Agent <other@example.com>"
        self.assertIn("co-author-pattern", rules(message(trailers=("Breaking: none", other))))

    def test_human_mode_skips_co_author(self):
        self.assertEqual(rules(message(trailers=("Breaking: none",)), human=True), set())

    def test_human_mode_allows_human_pair_without_agent(self):
        human = "Co-Authored-By: Jordan Lee <jordan.lee@example.com>"
        self.assertEqual(rules(message(trailers=("Breaking: none", human)), human=True), set())

    def test_human_mode_still_rejects_varied_agent_trailer(self):
        variant = "Co-Authored-By: Claude <noreply@anthropic.com>"
        self.assertIn("co-author-pattern", rules(message(trailers=("Breaking: none", variant)), human=True))
        lower = "Co-authored-by: Claude Code <noreply@anthropic.com>"
        self.assertIn("co-author-pattern", rules(message(trailers=("Breaking: none", lower)), human=True))

    def test_missing_trailer_block(self):
        self.assertIn("footer-missing", rules(message(trailers=())))


class CommandLine(unittest.TestCase):
    def test_usage_error_without_source(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lint_commit.main([]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
