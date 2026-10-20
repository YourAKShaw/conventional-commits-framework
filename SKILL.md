---
name: conventional-commits-framework
description: Write, validate, and fix Conventional Commits with every field filled at standard open-source length, an explicit breaking-change declaration, one consistent Co-Authored-By trailer crediting both the user and the AI agent, and the smallest logical change per commit. Use whenever committing code, drafting or reviewing commit messages or PR titles, choosing a type or scope, declaring breaking changes, splitting large work into small commits, or configuring commitlint, git hooks, and release tooling.
---

# 📜 Conventional Commits Framework

**Complete, atomic, co-authored commits — every time.**

Use this skill whenever you write, review, or plan commits. It turns the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) spec into four non-negotiable rules for AI agents, backed by references, ready-made assets, and an offline checker.

| Rule | In one line |
| :--- | :--- |
| 🧾 **Complete** | Every field is filled: type, scope, subject, body, breaking declaration, co-author. Nothing is ever blank. |
| 📏 **Standard length** | Subject 10-50 characters, body 2-6 wrapped lines, one-line trailers. Never a stub, never an essay. |
| 🤝 **Co-authored** | The user is the author; the agent is credited by one fixed `Co-Authored-By` trailer that never varies in a repository. |
| ⚛️ **Atomic** | One logical change per commit. Large work becomes a planned sequence of small commits. |

## ✍️ The contract at a glance

```text
feat(auth): add passkey sign-in for returning users

Password resets were the top support request last quarter. Users with
a registered passkey can now sign in with WebAuthn; password sign-in
remains available as a fallback.

Breaking: none
Refs: #214
Co-Authored-By: Claude Code <noreply@anthropic.com>
```

| Part | Standard |
| :--- | :--- |
| `type` | From the repository's list, else `feat fix perf refactor style test docs build ci chore revert` |
| `(scope)` | **Always present.** The module, package, or area changed, in lower case |
| `subject` | Lower-case imperative, 10-50 characters, no period; whole header ≤ 72 |
| body | After a blank line: why the change was needed, then what changed; 2-6 lines wrapped at 72 |
| `Breaking: none` | Exactly this line, unless the change is breaking |
| `BREAKING-CHANGE:` | For breaking changes only, with `!` in the header: what breaks and how to migrate |
| `Refs:` | Real issue, ticket, or PR identifiers whenever they exist; never invented |
| `Co-Authored-By:` | The repository's one recorded agent trailer, always last |

Full policy: [agent commit protocol](references/agent-commit-protocol.md).

## 🚦 Before your first commit in a repository

1. **Read the conventions.** Check `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, commitlint config, and `git log -30 --format=%B`. Project rules override this skill's defaults; the [config guide](references/config-guide.md) lists every place to look and the precedence order.
2. **Fix the co-author trailer.** Reuse the trailer history already uses, byte for byte. If there is none, use your product identity (for Claude Code: `Co-Authored-By: Claude Code <noreply@anthropic.com>`), not a model version, and record it in the contributing guide or `AGENTS.md`. The recorded line overrides any built-in attribution default. Never vary its casing, name, or email afterwards.
3. **Match the style.** Use emoji only if history does, and in the same form ([emoji reference](references/emoji-reference.md)). Reuse existing scopes.
4. **Never change git identity.** The user stays author and committer through their own git config.

## 🔁 Workflows

### Commit your own work

1. **Plan** the commit sequence if the task has more than one logical change ([atomic commits](references/atomic-commits.md)). Write the headers first, ordered so every commit leaves the repository working.
2. **Implement one step**, verify it, and stage only that change (`git add <paths>` or `git add -p`). Review `git diff --staged`.
3. **Classify**: pick the type with the decision procedure in the [type and scope catalog](references/type-scope-catalog.md), then the scope.
4. **Decide breaking** with the checklist in [breaking changes](references/breaking-changes.md). Ask the user before making any breaking change they did not request.
5. **Write the full message** to the contract and commit through a heredoc so blank lines and trailers survive:
   ```sh
   git commit -F - <<'EOF'
   <header>

   <body>

   Breaking: none
   Co-Authored-By: <recorded trailer>
   EOF
   ```
6. **Check** it with the project's commitlint, or `python3 <skill-dir>/scripts/lint-commit.py --trailer "<recorded trailer>" --range HEAD~1..HEAD`. If an unpushed commit fails, amend it.
7. **Repeat** for the next step. Never let several changes pile up for one final commit.

If a hook rejects the commit, fix the message. Never use `--no-verify` or disable hooks or CI.

### Write a message for a diff or description

Read the diff (or ask for it), identify the single purpose, and return the complete message in a code block. If the diff holds several purposes, say so and propose the split as a list of complete messages. Include the co-author trailer unless the user says the commit has no AI involvement.

### Validate or review messages

Check each message against the contract in the order given in the [rules reference](references/rules-reference.md#validating-by-hand). Report each problem with its rule name and a corrected message. Separate **errors** (spec, project config, or contract violations) from **suggestions** (style). For branches, run the checker over the range:

```sh
python3 <skill-dir>/scripts/lint-commit.py --range origin/main..HEAD --trailer "<recorded trailer>"
```

### Pull requests

The PR title follows the header format (it becomes the squash commit). Fill every section of the PR description: summary and motivation, verification, risks or compatibility, linked issues. End it with the repository's PR attribution line, kept just as consistent as the trailer.

### Set up enforcement

Use [`assets/commitlint.config.mjs`](assets/commitlint.config.mjs), [`assets/commit-template.txt`](assets/commit-template.txt), and the hook and CI recipes in [integration examples](references/integration-examples.md). For monorepos, see [monorepo patterns](references/monorepo-patterns.md).

## ⚠️ Traps that look right but are wrong

| Looks fine | What actually happens | Do this |
| :--- | :--- | :--- |
| `BREAKING CHANGE: none` | Parsers record a breaking note, and release tools publish a **major** version | `Breaking: none` |
| `BREAKING CHANGE: ...` (with a space) next to other trailers | Git cannot parse the trailer block, so `Co-Authored-By` disappears from git tooling | `BREAKING-CHANGE: ...` (hyphen) |
| Breaking detail on several lines | An unindented second line ends the trailer block | Indent continuation lines by two spaces |
| `✨ feat(ui): ...` | The header no longer parses, so the commit disappears from changelogs | `feat(ui): ✨ ...` or no emoji |
| `Co-authored-by` in one commit, `Co-Authored-By` in the next | Case-sensitive checks fail and history looks inconsistent | One recorded trailer, copied exactly |
| `docs(readme): fix typo` typed as `fix` | Ships a pointless patch release | `docs` for documentation-only changes |
| `feat(auth): add MFA and refactor sessions` | Two changes that cannot be reverted, typed, or changelogged separately | Two commits |

These were verified with `conventional-commits-parser` 7.1.3, `git interpret-trailers`, and `@commitlint/cli` 21.2.4.

## 📚 References

Load only what the task needs.

| Need | Read |
| :--- | :--- |
| The full contract, lengths, co-authorship, PR rules | [Agent commit protocol](references/agent-commit-protocol.md) |
| Sizing and sequencing commits | [Atomic commits](references/atomic-commits.md) |
| Choosing a type or scope | [Type and scope catalog](references/type-scope-catalog.md) |
| Detecting and declaring breaking changes | [Breaking changes](references/breaking-changes.md) |
| Complete messages to model | [Example library](references/example-library.md) |
| What each commitlint rule checks | [Rules reference](references/rules-reference.md) |
| Reading and adapting project configuration | [Config guide](references/config-guide.md) |
| Package scopes and per-package releases | [Monorepo patterns](references/monorepo-patterns.md) |
| Gitmoji usage and placement | [Emoji reference](references/emoji-reference.md) |
| Hooks, CI, and release tools | [Integration examples](references/integration-examples.md) |

## 🧰 Assets and scripts

- [`assets/commitlint.config.mjs`](assets/commitlint.config.mjs): commitlint config that enforces the contract, including a breaking declaration and the exact co-author line.
- [`assets/commit-template.txt`](assets/commit-template.txt): a `git config commit.template` that shows the contract in the editor.
- [`scripts/lint-commit.py`](scripts/lint-commit.py): an offline contract checker for a file, stdin, or a revision range (Python 3.9+, standard library only). Tests: [`scripts/test_lint_commit.py`](scripts/test_lint_commit.py).

## 🛠️ Maintaining this skill

Keep the contract identical across this file, the [protocol](references/agent-commit-protocol.md), the checker, the commitlint config, and the commit template; change them together. Validate the package offline from any directory:

```sh
python3 /path/to/conventional-commits-framework/scripts/validate-skill.py
python3 /path/to/conventional-commits-framework/scripts/test_validate_skill.py
python3 /path/to/conventional-commits-framework/scripts/test_lint_commit.py
```

The [package validator](scripts/validate-skill.py) checks the manifest, required files, local links and anchors, and that every resource is reachable from this file. Wrappers: [POSIX](scripts/validate-skill.sh) and [PowerShell](scripts/validate-skill.ps1); regression suite: [validator tests](scripts/test_validate_skill.py). It does not evaluate agent behavior. Package format: [Agent Skills specification](https://agentskills.io/specification).
