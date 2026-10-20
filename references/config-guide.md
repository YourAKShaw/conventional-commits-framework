# Configuration guide

Projects customise Conventional Commits through commitlint and related tools. An agent reads this configuration **before** writing its first commit in a repository, because the project's rules override this skill's defaults wherever they are stricter or different.

## Discover the project's conventions

Check these sources, then follow the strictest consistent reading:

| Source | What it tells you |
| :--- | :--- |
| `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md` | Rules written specifically for AI agents, often including the co-author trailer |
| `CONTRIBUTING.md`, `.github/CONTRIBUTING.md` | Human-facing commit rules, scopes, sign-off requirements |
| commitlint config (below) | Machine-enforced types, scopes, and lengths |
| `.czrc`, `.cz.toml`, `cz.json`, or `config.commitizen` in `package.json` | Commitizen adapter, types and scopes offered in prompts |
| `release-please-config.json`, `.releaserc*`, `cliff.toml` | Which types appear in changelogs and bump versions |
| `.husky/commit-msg`, `lefthook.yml`, `.pre-commit-config.yaml` | Which checks run locally |
| `git log -30 --format=%B` | The conventions people actually follow, including trailer format and emoji |

If sources conflict, ask the user, or follow the enforced tool and mention the conflict.

## commitlint config files

commitlint (21.x) searches from the working directory upward and uses the first match, in this order: a `commitlint` field in `package.json` or `package.yaml`; `.commitlintrc` with no extension or with `.json`, `.yaml`, `.yml`, `.js`, `.cjs`, or `.mjs`; `commitlint.config.js`, `.cjs`, or `.mjs`; then the TypeScript forms `.commitlintrc.ts`/`.cts`/`.mts` and `commitlint.config.ts`/`.cts`/`.mts`.

A minimal configuration that extends the conventional preset:

```json
{
  "extends": ["@commitlint/config-conventional"],
  "rules": {
    "header-max-length": [2, "always", 72],
    "scope-enum": [2, "always", ["api", "auth", "ui", "deps", "docs", "release"]]
  }
}
```

Each rule takes `[level, applicable, value]`: level `0` off, `1` warning, `2` error. See the [rules reference](rules-reference.md).

## Adopt the Complete Commit Contract

Copy [`assets/commitlint.config.mjs`](../assets/commitlint.config.mjs) to the repository root as `commitlint.config.mjs`, then:

1. Set `CO_AUTHOR` to the repository's one agent trailer ([protocol](agent-commit-protocol.md#co-authorship-two-authors-one-fixed-pattern)).
2. Add `scope-enum` with the project's scopes if the list is stable.
3. Install and test:

```sh
npm install --save-dev @commitlint/cli @commitlint/config-conventional
git log -1 --format=%B | npx commitlint
```

For a repository where many commits have no AI involvement, set `'co-author-exact': [0]` and rely on the agent protocol, or keep it at level `1` as a reminder.

No Node.js? `scripts/lint-commit.py` from this skill applies the same contract with only Python 3.9+:

```sh
python3 path/to/conventional-commits-framework/scripts/lint-commit.py \
  --trailer "Co-Authored-By: Claude Code <noreply@anthropic.com>" --range origin/main..HEAD
```

## Common customisations

| Goal | Configuration |
| :--- | :--- |
| Restrict scopes to known packages | `"scope-enum": [2, "always", ["web-app", "api", "ui-kit"]]` |
| Allow a project-specific type | `"type-enum": [2, "always", ["feat", "fix", "docs", "deps", ...]]` (list all types) |
| Shorter subjects (Vue style) | `"header-max-length": [2, "always", 60]` |
| Require a DCO sign-off | `"signed-off-by": [2, "always", "Signed-off-by:"]` |
| Require an issue reference | `"references-empty": [2, "never"]` |
| Treat a rule as advice only | Change its level to `1` |

## Commit template

To show the contract in the editor whenever someone runs `git commit` without `-m`:

```sh
cp path/to/conventional-commits-framework/assets/commit-template.txt .gitmessage
git config commit.template .gitmessage
```

Git removes the `#` guidance lines when it records the commit.

## Precedence for agents

1. Explicit instructions from the user in the current task.
2. Agent instruction files and contributing guides in the repository.
3. Enforced tooling configuration (commitlint, hooks, CI).
4. The repository's consistent history.
5. This skill's defaults.

The contract's completeness rules (every field filled, explicit breaking declaration, the co-author trailer) still apply unless the user or repository explicitly opts out. A project may use different lengths or types; it does not thereby permit empty bodies.
