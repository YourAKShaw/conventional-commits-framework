<div align="center">

# 📜 Conventional Commits Framework

[![HOL Guard](https://img.shields.io/endpoint?url=https%3A%2F%2Fhol.org%2Fapi%2Fregistry%2Fbadges%2Fplugin%3Fslug%3Dyourakshaw%252Fconventional-commits-framework%26metric%3Dtrust)](https://hol.org/registry/plugins/yourakshaw%2Fconventional-commits-framework)

**Complete, atomic, co-authored commits from every AI agent, every time.**

An agent skill that turns the Conventional Commits spec into commit messages people want to read and release tools can trust.

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-334155?style=flat-square)](SKILL.md)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-FE5196?style=flat-square&logo=conventionalcommits&logoColor=white)](https://www.conventionalcommits.org/en/v1.0.0/)
[![commitlint](https://img.shields.io/badge/commitlint-21.x-2563EB?style=flat-square)](references/rules-reference.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-2563EB?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-334155?style=flat-square)](.github/CONTRIBUTING.md)

[Explore the skill](SKILL.md) · [Commit protocol](references/agent-commit-protocol.md) · [Examples](references/example-library.md) · [Contribute](.github/CONTRIBUTING.md) · [Get help](.github/SUPPORT.md)

</div>

---

## Commits are the record your project keeps

AI agents now write a large share of commits, and they tend to write them in a hurry: `fix: update`, no body, an invented type, a breaking change nobody flagged, and an attribution line that changes from one session to the next. Each one costs a reviewer time, hides a reason that someone will need later, or ships the wrong version.

**Conventional Commits Framework** gives your agent one clear standard and the tools to meet it. Every commit is **complete**, **sized to one logical change**, and **credits both you and the agent** in exactly the same way across the whole repository.

```text
fix(auth): reject expired refresh tokens before rotation

Refresh tokens were rotated before their expiry was checked, so a
stolen expired token could still mint a new session. Validate expiry
first and return 401 without touching the token store.

Breaking: none
Refs: #318
Co-Authored-By: Claude Code <noreply@anthropic.com>
```

## ✨ Four rules, no exceptions

| | Rule | What your agent does |
| :---: | :--- | :--- |
| 🧾 | **Complete** | Fills every field (type, scope, subject, body, breaking declaration, co-author) on every commit. Nothing is left blank. |
| 📏 | **Standard length** | Writes 10-50 character subjects, 2-6 line bodies that explain *why*, and one-line trailers. No stubs, no essays. |
| 🤝 | **Co-authored** | Keeps you as author and committer, and credits itself through one fixed `Co-Authored-By` trailer that never varies. |
| ⚛️ | **Atomic** | Plans large work as a sequence of small commits, each one logical change that builds, reverts, and changelogs cleanly. |

## 🧠 What the skill knows

| Capability | In practice |
| :--- | :--- |
| **Type and scope judgment** | An ordered decision procedure and tie-breakers for the confusions behind most convention failures (`fix` or `feat`, `refactor` or `perf`, `build` or `chore`). |
| **Breaking-change safety** | Detection across code, HTTP, CLI, config, data, and runtime surfaces, plus migration notes that tell consumers what to do. |
| **Verified format traps** | Why `BREAKING CHANGE: none` publishes a major version, and why the spaced token hides your co-author trailer from git. |
| **Repository awareness** | Reads `AGENTS.md`, contributing guides, commitlint config, and history before the first commit, and follows the project's conventions. |
| **Validation and review** | Explains all 38 commitlint rules and reports errors separately from style suggestions, each with a corrected message. |
| **Enforcement setup** | Ready-made commitlint config, commit template, hooks, CI workflows, monorepo scope presets, and release tooling. |

## 🔍 Verified, not assumed

The format rules in this skill were checked against real tooling, not copied from blog posts:

| Claim | Verified with |
| :--- | :--- |
| `BREAKING CHANGE: none` and `Breaking-Change: none` create breaking notes | `conventional-commits-parser` 7.1.3 |
| A spaced `BREAKING CHANGE:` footer hides `Co-Authored-By` from git | `git interpret-trailers --parse` |
| `BREAKING-CHANGE:` with indented continuation lines keeps every trailer | git, the parser, and `@commitlint/cli` 21.2.4 |
| An emoji after the colon parses; one before the type does not | `conventional-commits-parser` 7.1.3 |
| `@commitlint/rules` ships 38 rules | `@commitlint/rules` 21.2.4 |
| All 22 example messages satisfy the contract | `scripts/lint-commit.py` and the contract commitlint config |

## 📥 Get started

Keep [`SKILL.md`](SKILL.md), `references/`, `assets/`, and `scripts/` together so the skill can resolve its resources.

### Skills CLI: any supported agent

```sh
npx skills add YourAKShaw/conventional-commits-framework
```

Follow the prompts to choose your agent and scope. To target Claude Code directly, add `--agent claude-code`, and add `--global` for a personal installation across projects. See the [Skills CLI documentation](https://github.com/vercel-labs/skills#readme).

### Claude Code: clone

```sh
# Personal, across all your projects
git clone https://github.com/YourAKShaw/conventional-commits-framework.git ~/.claude/skills/conventional-commits-framework

# Project only: run from the project root
git clone https://github.com/YourAKShaw/conventional-commits-framework.git .claude/skills/conventional-commits-framework
```

Then type `/conventional-commits-framework` in Claude Code, or just ask Claude to commit; it loads the skill for matching tasks. See the [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

### Claude apps: upload a ZIP

1. [Download the repository ZIP](https://github.com/YourAKShaw/conventional-commits-framework/archive/refs/heads/main.zip), extract it, and rename the folder to `conventional-commits-framework`.
2. Compress that folder so the archive contains `conventional-commits-framework/SKILL.md`.
3. Enable **Code execution and file creation** under **Settings → Capabilities**, then upload the ZIP under **Customize → Skills**.

See Claude's [skill upload instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## 💬 Put it to work

> **Commit as you go**
> Use the Conventional Commits Framework while you implement this feature. Plan the commits first and commit each step as you finish it.

> **Draft a message**
> Write a complete conventional commit for the staged diff.

> **Review history**
> Check the commits on this branch against the commit contract and give me corrected messages for any that fail.

> **Plan a split**
> These changes are all in my working tree. Propose a sequence of atomic commits with complete messages.

> **Set up enforcement**
> Add commitlint and a commit-msg hook that enforce the commit contract in this repository.

## 📚 Inside the skill

| Reference | Covers |
| :--- | :--- |
| [Agent commit protocol](references/agent-commit-protocol.md) | The Complete Commit Contract, field lengths, co-authorship, PRs, the pre-commit checklist |
| [Atomic commits](references/atomic-commits.md) | Smallest logical change, splitting seams, planning commit sequences |
| [Type and scope catalog](references/type-scope-catalog.md) | The eleven standard types, the decision procedure, scope selection |
| [Breaking changes](references/breaking-changes.md) | Detection, declaration, format traps, migration notes |
| [Example library](references/example-library.md) | 22 complete messages and a before-and-after table |
| [Rules reference](references/rules-reference.md) | All 38 commitlint rules with defaults and contract settings |
| [Config guide](references/config-guide.md) | Discovering conventions, commitlint files, precedence |
| [Monorepo patterns](references/monorepo-patterns.md) | Package scopes, cross-package changes, workspace presets |
| [Emoji reference](references/emoji-reference.md) | Safe gitmoji placement and the type-to-emoji mapping |
| [Integration examples](references/integration-examples.md) | Husky, Lefthook, pre-commit, GitHub Actions, release tools |

### Assets and scripts

- **[`commitlint.config.mjs`](assets/commitlint.config.mjs)**: enforces the contract, including the breaking declaration and the exact co-author line.
- **[`commit-template.txt`](assets/commit-template.txt)**: shows the contract in the editor via `git config commit.template`.
- **[`lint-commit.py`](scripts/lint-commit.py)**: offline checker for a message, stdin, or a revision range. Python 3.9+, no dependencies.
- **[`validate-skill.py`](scripts/validate-skill.py)**: structural check of this package.

```text
conventional-commits-framework/
├── SKILL.md          # Entry point: the four rules, workflows, traps, routing
├── references/       # Ten focused guides, loaded on demand
├── assets/           # commitlint config and git commit template
├── scripts/          # Contract checker, package validator, tests
├── .github/          # Contributing, support, templates, CI
├── README.md         # Project overview
├── SECURITY.md       # Supported versions and vulnerability reporting
└── LICENSE           # MIT License
```

## ✅ Validate

From the repository root, with Python 3.9+:

```sh
python3 scripts/validate-skill.py        # package structure and links
python3 scripts/test_lint_commit.py      # contract checker regression tests
python3 scripts/test_validate_skill.py   # validator regression tests
```

This repository follows its own rules: every commit in its history passes `scripts/lint-commit.py`.

---

## 🤝 Contributing and support

Improvements are welcome, especially real commit-message failures the skill does not yet prevent. Start with the [contribution guide](.github/CONTRIBUTING.md), use the [issue forms](https://github.com/YourAKShaw/conventional-commits-framework/issues/new/choose), read the [support guide](.github/SUPPORT.md), or report vulnerabilities privately as described in the [security policy](SECURITY.md).

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE).
