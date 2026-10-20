# Agent commit protocol

This is the policy every agent follows when it writes a commit. It has three parts: the **Complete Commit Contract** (every field filled, at a standard length), **co-authorship** (one fixed trailer per repository), and the **pre-commit checklist**. Atomic commit sizing is covered in [atomic commits](atomic-commits.md).

## The Complete Commit Contract

Every commit an agent writes contains all of these parts. None is optional, and none may be a placeholder.

```text
<type>(<scope>)<!>: <subject>
                                                   ← one blank line
<body: what changed and why, 2-6 lines wrapped at 72>
                                                   ← one blank line
Breaking: none          ─┐ exactly one of these two
BREAKING-CHANGE: <impact and migration>
Refs: #123               ← when an issue, ticket, or PR exists
Co-Authored-By: <the repository's fixed agent identity>
```

### Field-by-field standard

The lengths below reflect what Git, GitHub, the Linux kernel and Git project guidelines, Angular, and commitlint converge on. "Too short" means a reader cannot tell what changed or why; "too long" means the detail belongs in a PR description, docs, or a second commit.

| Field | Required content | Standard length | Too short | Too long |
| :--- | :--- | :--- | :--- | :--- |
| **type** | One of the repository's allowed types ([catalog](type-scope-catalog.md)) | 2-8 chars | — | Invented types (`feature`, `hotfix`) |
| **scope** | The area changed: module, package, or doc | 2-20 chars, kebab-case | `(x)`, `(misc)` | `(authentication-and-session-module)` |
| **subject** | Lower-case imperative verb + object | **10-50 chars** (header ≤ 72) | `fix(api): bug` | Anything that wraps in `git log --oneline` |
| **body** | Why the change was needed, then what changed at a high level | **2-6 lines**, wrapped at 72, ≥ 40 chars | Repeating the subject | > 25 lines: split the commit or move to PR |
| **Breaking** | `Breaking: none`, or `BREAKING-CHANGE:` with impact and migration | 1 line; breaking detail 1-4 lines | `BREAKING-CHANGE: yes` | A migration guide (link to it instead) |
| **Refs** | Issue, ticket, or PR identifiers that exist | 1 line | — | Prose |
| **Co-Authored-By** | The repository's fixed trailer | 1 line, never varied | — | — |

### Writing each field well

**Subject.** Complete the sentence *"If applied, this commit will …"*. Name the object, not the activity: `add retry budget to webhook sender` beats `update webhook code`. No trailing period, no capitalised first word (acronyms such as `API` are fine), no issue numbers (they go in `Refs`).

**Body.** Lead with the reason: the bug, the requirement, the constraint. Then summarise the approach in a sentence or a short bullet list. Mention notable side effects or alternatives rejected when a reviewer would ask. Do not narrate the diff line by line, paste logs, or describe how you (the agent) worked.

**Breaking declaration.** Always present, always explicit:

- Non-breaking: the exact line `Breaking: none`.
- Breaking: put `!` before the colon in the header **and** add `BREAKING-CHANGE: <what breaks>; <how to migrate>`. Indent continuation lines by two spaces.

Write `BREAKING-CHANGE` with a hyphen. The spec treats it as identical to `BREAKING CHANGE`, but the spaced form is not a valid git trailer: it hides the whole trailer block, including `Co-Authored-By`, from `git interpret-trailers` and tools built on it. Never write `BREAKING CHANGE: none` or `BREAKING-CHANGE: none`: parsers record any text after that token as a breaking note, and release tools will publish a major version. Details are in [breaking changes](breaking-changes.md).

**Refs.** Add when an issue, ticket, discussion, or PR exists: `Refs: #123`, `Refs: PROJ-481`. Use `Fixes: #123` or `Closes: #123` only when the commit fully resolves it and the host supports auto-closing. Never invent an issue number to fill the slot.

**Trailer order.** `Breaking` (or `BREAKING-CHANGE`), then `Refs`/`Fixes`, then any `Signed-off-by` the project requires, then `Co-Authored-By` last. Keep the trailers in one paragraph with no blank lines between them.

## Co-authorship: two authors, one fixed pattern

When an agent writes or substantially shapes a commit for a user, the commit records **both**:

1. **The user** as author and committer, through their own `git config user.name` and `user.email`. The agent never overrides `--author`, `GIT_AUTHOR_*`, or `GIT_COMMITTER_*`, and never commits under its own identity.
2. **The agent** through one `Co-Authored-By` trailer, which GitHub and GitLab display as a co-author.

### Choose the trailer once, then never vary it

The pattern is a repository-level decision, like the license. Follow this order:

1. **Reuse what exists.** Inspect recent history before the first commit:
   ```sh
   git log -50 --format='%(trailers:key=Co-Authored-By,valueonly)' | sed '/^$/d' | sort | uniq -c
   ```
   If the repository's contributing guide, `AGENTS.md`, `CLAUDE.md`, or commitlint config defines the trailer, or history shows one dominant form, copy it **byte for byte**: key casing, name, and email.
2. **Otherwise establish one.** Use `Co-Authored-By: <Agent Product Name> <documented-noreply-address>`. For Claude Code this is `Co-Authored-By: Claude Code <noreply@anthropic.com>`. Use the product name, not a model version, so the trailer stays identical when the underlying model changes. For another agent, use the noreply address its vendor documents; if none is documented, ask the user once rather than inventing an address.
3. **Record it** in the repository's contributing guide or `AGENTS.md` (and in the commitlint `co-author-exact` rule if the project uses [the provided config](../assets/commitlint.config.mjs)) so every later session and every other agent uses the same line.

The recorded repository trailer takes precedence over an agent's built-in default attribution line. Never mix `Co-Authored-By` and `Co-authored-by`, never alternate names (`Claude`, `Claude Code`, `Claude Opus`), and never add a second agent trailer for the same agent. Some tools match keys case-sensitively (commitlint's `trailer-exists` does), so a single variation breaks enforcement.

### When there are more contributors

- Pair programming with another human: add their `Co-Authored-By` line **before** the agent's line.
- Several distinct agents genuinely contributed: one fixed trailer per agent, each recorded in the repository.
- The user wrote the change entirely and asked the agent only to commit it: the agent still did the committing work, so keep the trailer unless the user explicitly asks to omit it. Respect that request.
- Commits created by bots (Dependabot, Renovate, release tooling) follow those tools' own formats.

### Pull requests

PR titles follow the same header format (they become the squash-merge commit). PR descriptions are also completely filled: a summary of what changed and why, verification performed, risks or compatibility, and linked issues, using the repository's PR template when one exists. End the description with the agent attribution line the repository uses for PRs, kept as consistent as the commit trailer.

## Pre-commit checklist

Before every commit, the agent confirms:

- [ ] The staged diff is **one logical change** ([atomic commits](atomic-commits.md)); nothing unrelated is staged.
- [ ] Type and scope come from the repository's conventions or the [catalog](type-scope-catalog.md).
- [ ] Subject is 10-50 characters of lower-case imperative text; header ≤ 72.
- [ ] Body explains why in 2-6 wrapped lines and does not repeat the subject.
- [ ] Exactly one breaking declaration is present, and `!` matches it.
- [ ] `Refs` lists real identifiers only.
- [ ] The co-author trailer matches the repository's recorded line exactly and is last.
- [ ] The message passes the repository's commitlint config or `python3 scripts/lint-commit.py` from this skill.

Pass the message through a file or heredoc (`git commit -F -`), not a long `-m` string, so blank lines and trailers survive shell quoting.

```sh
git commit -F - <<'EOF'
fix(auth): reject expired refresh tokens before rotation

Refresh tokens were rotated before their expiry was checked, so a
stolen expired token could still mint a new session. Validate expiry
first and return 401 without touching the token store.

Breaking: none
Refs: #318
Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```
