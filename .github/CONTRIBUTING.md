<div align="center">

# 🤝 Contributing to Conventional Commits Framework

**Help agents write commits that people and release tools can trust.**

[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-2563EB?style=flat-square)](https://github.com/YourAKShaw/conventional-commits-framework/pulls)
[![Python 3.9+](https://img.shields.io/badge/Scripts-Python%203.9%2B-334155?style=flat-square)](../scripts/lint-commit.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB?style=flat-square)](../LICENSE)

[Project overview](README.md) · [Skill entry point](../SKILL.md) · [Get help](SUPPORT.md)

</div>

---

## Start with a real commit problem

The most useful contributions start from an observed failure: a message an agent wrote that was incomplete, mistyped, mis-sized, wrongly attributed, or rejected by a real tool. Useful contributions include:

- A commit-message failure the guidance does not yet prevent, with the message and context.
- A correction to a rule, default, or tool behavior, with an authoritative source or a reproduction.
- A clearer decision rule for type, scope, breaking changes, or commit sizing.
- A new example that passes the contract, or a check the checker or validator should perform.

Read [SKILL.md](../SKILL.md) and the [agent commit protocol](../references/agent-commit-protocol.md) before changing guidance.

## 🧭 Choose the right starting point

| Contribution | Where to begin |
| :--- | :--- |
| Small correction or focused fix | Open a pull request with the problem and verification. |
| Incorrect guidance, checker bug, or broken link | Search existing issues, then use the matching [issue form](https://github.com/YourAKShaw/conventional-commits-framework/issues/new/choose). |
| New rule, changed default, or package structure | Open an issue first with the use case, trade-offs, and scope. |
| Usage question | Follow the [support guide](SUPPORT.md). |

Use sanitized examples. Remove credentials, private code, internal ticket details, and personal data before posting.

## ✍️ Commit conventions for this repository

This repository follows its own contract. Every commit uses this pattern:

```text
type(scope): :gitmoji: lower-case imperative subject

Two to six wrapped lines explaining why the change was needed and
what it changes.

Breaking: none
Co-Authored-By: Claude Code <noreply@anthropic.com>
```

- **Emoji:** one gitmoji shortcode after the colon, matching the type ([emoji reference](../references/emoji-reference.md)).
- **Agent trailer:** commits written with an AI agent end with exactly `Co-Authored-By: Claude Code <noreply@anthropic.com>`. This line is the repository's recorded trailer; do not vary its casing, name, or email. Human-only commits omit it. Other agents add their own documented trailer, recorded here first.
- **Size:** one logical change per commit ([atomic commits](../references/atomic-commits.md)).

Check your commits before pushing:

```sh
python3 scripts/lint-commit.py --range origin/main..HEAD \
  --trailer "Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

Add `--human` for commits without AI involvement. To check each commit as you write it:

```sh
printf '#!/bin/sh\nexec python3 scripts/lint-commit.py --trailer "Co-Authored-By: Claude Code <noreply@anthropic.com>" "$1"\n' > .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

## Make a focused change

1. Fork the repository and create a branch.
2. Read the guidance you are changing and everything that links to it.
3. Make the smallest coherent change. Keep the contract identical across [SKILL.md](../SKILL.md), the [protocol](../references/agent-commit-protocol.md), [`lint-commit.py`](../scripts/lint-commit.py), the [commitlint config](../assets/commitlint.config.mjs), and the [commit template](../assets/commit-template.txt).
4. Run the checks below and inspect the full diff.
5. Open a pull request using the template.

### Keep the package coherent

| Principle | What to preserve |
| :--- | :--- |
| **One contract** | A rule lives in the protocol; other files point to it or implement it identically. |
| **Verified claims** | Tool behavior is checked against a named tool version, and the version is written down. |
| **Real examples** | Every `text` example in the [example library](../references/example-library.md) passes the checker. Examples are labelled illustrative, never presented as real project commits. |
| **Progressive disclosure** | SKILL.md routes; detail lives in one focused reference. Keep SKILL.md under 500 lines. |
| **Portable scripts** | Python 3.9+ standard library only; read-only; no network access. |

## 🔍 Validate your change

From the repository root, with Python 3.9 or later:

```sh
python3 scripts/validate-skill.py
python3 scripts/test_lint_commit.py
python3 scripts/test_validate_skill.py
```

Wrappers for the validator: `sh scripts/validate-skill.sh` and `powershell -File scripts/validate-skill.ps1`.

When you change an example or the contract, also check every example:

```sh
python3 - <<'EOF'
import re, subprocess
text = open("references/example-library.md", encoding="utf-8").read()
for block in re.findall(r"```text\n(.*?)```", text, re.S):
    subprocess.run(["python3", "scripts/lint-commit.py", "-"], input=block, text=True, check=True)
EOF
```

When you change the commitlint config, test it with `@commitlint/cli` against passing and failing messages and record the version in your PR.

The package checks do not prove agent behavior. For instruction changes, describe a representative scenario, the host and model, what the agent did before and after, and the remaining limits. Report only results you observed.

## 📬 Open a reviewable pull request

Use the [pull request template](pull_request_template.md) to explain the problem, the change, the verification you ran, and any risks. Keep discussion focused on the change, and use concrete messages and tool output when you disagree.
