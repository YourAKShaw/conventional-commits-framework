# Integration examples

Local hooks give fast feedback, CI is the guarantee, and release tools consume the result. Versions below were current in October 2026; pin to whatever your repository already uses.

**Agents never bypass these checks.** Do not use `git commit --no-verify`, `HUSKY=0`, or disabled CI to get a commit through. Fix the message, or report the conflict to the user.

## Local commit-msg hooks

### Husky 9 + commitlint (Node.js projects)

```sh
npm install --save-dev husky @commitlint/cli @commitlint/config-conventional
npx husky init
echo 'npx --no -- commitlint --edit "$1"' > .husky/commit-msg
```

`husky init` also creates a `pre-commit` hook that runs `npm test`; edit or remove it as the project requires. Add the [contract config](../assets/commitlint.config.mjs) as `commitlint.config.mjs`.

### Lefthook

```yaml
# lefthook.yml
commit-msg:
  commands:
    commitlint:
      run: npx --no -- commitlint --edit {1}
```

### pre-commit framework or plain git (no Node.js)

Copy `scripts/lint-commit.py` from this skill into the repository (for example as `scripts/lint-commit.py`), then:

```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit, commit-msg]
repos:
  - repo: local
    hooks:
      - id: commit-contract
        name: Complete Commit Contract
        entry: python3 scripts/lint-commit.py --trailer "Co-Authored-By: Claude Code <noreply@anthropic.com>"
        language: system
        stages: [commit-msg]
```

Or, without any framework, a hook for one clone:

```sh
printf '#!/bin/sh\nexec python3 scripts/lint-commit.py "$1"\n' > .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

## CI on GitHub Actions

### Check every commit in a pull request

```yaml
# .github/workflows/commits.yml
name: Commit messages
on: pull_request
permissions:
  contents: read
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v7
        with:
          node-version: 22
      - run: npm ci
      - run: >
          npx commitlint --verbose
          --from ${{ github.event.pull_request.base.sha }}
          --to ${{ github.event.pull_request.head.sha }}
```

Without Node.js, replace the last three steps with `actions/setup-python@v7` and `python3 scripts/lint-commit.py --range "$BASE..$HEAD"`, passing the two SHAs through `env`.

### Check the PR title in squash-merge repositories

When PRs are squash-merged, the title becomes the commit header on `main`:

```yaml
# .github/workflows/pr-title.yml
name: PR title
on:
  pull_request_target:
    types: [opened, edited, synchronize, reopened]
permissions:
  pull-requests: read
jobs:
  title:
    runs-on: ubuntu-latest
    steps:
      - uses: amannn/action-semantic-pull-request@v6
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          requireScope: true
```

This workflow uses `pull_request_target` and does not check out PR code, which keeps it safe for forks. Do not add a checkout of the PR head to a `pull_request_target` workflow.

Configure the repository's squash-merge default to "Pull request title and description" so the PR body supplies the commit body. Then the PR description must satisfy the contract too: body text, `Breaking: none` or `BREAKING-CHANGE`, and the co-author trailer.

## Release automation

All of these read the commit types and breaking markers this skill produces.

| Tool | Role | Note |
| :--- | :--- | :--- |
| **release-please** (`googleapis/release-please-action@v5`) | Opens a release PR with version bump and changelog | Plain Conventional Commits only; emoji are ignored |
| **semantic-release** (25.x) | Computes the version and publishes in CI | Default rules: `feat` minor, `fix`/`perf`/`revert` patch, breaking major |
| **git-cliff** | Generates changelogs from a template | Highly configurable grouping by type and scope |
| **conventional-changelog** | Library and CLI behind many of the above | Uses `conventional-commits-parser` |
| **Commitizen** (`cz-cli`) | Interactive prompts for humans | Agents write messages directly instead |

Minimal release-please workflow:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]
permissions:
  contents: write
  pull-requests: write
jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v5
        with:
          release-type: node
```

## Checking a branch before pushing

Agents run this before pushing or opening a PR:

```sh
python3 scripts/lint-commit.py --range origin/main..HEAD \
  --trailer "Co-Authored-By: Claude Code <noreply@anthropic.com>"
# or, in a commitlint project:
npx commitlint --from origin/main --to HEAD --verbose
```

If an unpushed commit fails, fix it with `git commit --amend` (latest commit) or an interactive rebase reword. If it was already pushed to a shared branch, leave history alone and tell the user.
