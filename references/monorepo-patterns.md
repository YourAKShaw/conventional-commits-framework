# Monorepo patterns

In a monorepo the scope does the routing work: it says which package changed, which changelog the entry belongs to, and which package version a release tool bumps. Getting it right matters more than in a single-package repository.

## Scope = package

Use the package (or app) name as the scope, in the form the repository already uses:

| Repository style | Scope form | Example |
| :--- | :--- | :--- |
| Short directory names | Folder under `packages/` or `apps/` | `feat(web-app): add order status badges` |
| Published npm names | Full package name | `fix(@acme/http-client): retry on ECONNRESET` |
| Package name without org | Name after the slash | `fix(http-client): retry on ECONNRESET` |
| Nested domains | Area/package | `feat(payments/ledger): add reversal entries` |

Pick one form and keep it. Mixing `ui`, `ui-kit`, and `@acme/ui-kit` for the same package splits its history across three scopes and breaks per-package changelogs.

To find the established form:

```sh
git log --format=%s -200 | sed -nE 's/^[a-z]+\(([^)]*)\).*/\1/p' | sort | uniq -c | sort -rn
```

## Changes that touch several packages

1. **Split by package when the parts stand alone.** A new component in `ui-kit` and its first use in `web-app` are two commits: `feat(ui-kit): add status badge` → `feat(web-app): show order status badges`. Each package's changelog gets its own entry.
2. **Keep one commit when the parts cannot work apart**, such as a lockstep API change in a producer and its only consumer. Use the package that owns the contract as the scope and name the others in the body. If the project's tooling supports multiple scopes, `feat(api,web-app): ...` is valid for commitlint's `scope-enum`, which splits on `/`, `\`, and `,`.
3. **Repository-wide changes** (root tooling, CI, formatting across all packages) use a stable repository scope the project already uses, such as `repo`, `workspace`, or `root`, or the tool name: `build(turbo): cache test outputs`, `ci(actions): ...`.

Breaking changes in a monorepo name the affected package in the `BREAKING-CHANGE` trailer, because consumers usually depend on one package, not the repository.

## Enforce scopes from the workspace

commitlint publishes presets that generate `scope-enum` from the workspace's packages:

| Workspace tool | Preset |
| :--- | :--- |
| npm/Yarn workspaces (`workspaces` in `package.json`) | `@commitlint/config-workspace-scopes` |
| pnpm (`pnpm-workspace.yaml`) | `@commitlint/config-pnpm-scopes` |
| Nx | `@commitlint/config-nx-scopes` |
| Lerna | `@commitlint/config-lerna-scopes` |
| Rush | `@commitlint/config-rush-scopes` |

```js
export default {
  extends: ['@commitlint/config-conventional', '@commitlint/config-pnpm-scopes'],
};
```

Run `npx commitlint --print-config` to see the scopes a preset produced, and add non-package scopes (`deps`, `release`, `repo`) to `scope-enum` yourself if the project uses them. These presets enforce exact names, so check the generated list before adopting the contract config, which also requires a scope on every commit.

## Release tools and scopes

Per-package release tools read the scope or the changed paths to decide what to version:

- **release-please** in manifest mode assigns commits to packages by the **files changed**, not by scope. A commit touching two packages appears in both changelogs, which is another reason to split commits by package.
- **Changesets** uses its own changeset files for versioning; Conventional Commits then serve history and review, not the version bump.
- **semantic-release** has no native monorepo mode; plugins such as `semantic-release-monorepo` filter commits by path.
- **Nx Release** and **Lerna** with conventional commits use the commits affecting each project's files.

Whatever the tool, an atomic commit that touches one package produces the cleanest per-package changelog.
