# Type and scope catalog

Choosing the type is where Conventional Commits goes wrong most often: type confusion accounts for about 57.7% of the developer issues analysed by Zeng et al. (ICSE 2025). The spec itself defines only `feat` and `fix`; every other type comes from the Angular convention by way of `@commitlint/config-conventional`. Always prefer the repository's own type list when it has one.

## The eleven standard types

These are the `type-enum` defaults in `@commitlint/config-conventional`. Version effects are the defaults of semantic-release and release-please; a project can configure them differently.

| Type | Use for | Default release effect | Example |
| :--- | :--- | :--- | :--- |
| `feat` | New user-facing capability or public API | **minor** | `feat(auth): add passkey sign-in` |
| `fix` | Corrects behavior that was wrong | **patch** | `fix(cart): keep discounts after currency switch` |
| `perf` | Same behavior, measurably faster or cheaper | patch (semantic-release default) | `perf(search): cache tokenized queries` |
| `refactor` | Restructures code without changing behavior | none | `refactor(parser): extract token reader` |
| `style` | Formatting only: whitespace, quotes, semicolons, import order | none | `style(api): apply prettier to handlers` |
| `test` | Adds or corrects tests only | none | `test(auth): cover expired refresh tokens` |
| `docs` | Documentation only: README, guides, doc comments | none | `docs(readme): add offline install steps` |
| `build` | Build system, packaging, and dependencies | none | `build(deps): bump vite to 5.4.2` |
| `ci` | CI/CD configuration and scripts | none | `ci(actions): cache pnpm store between jobs` |
| `chore` | Maintenance that fits nowhere else and ships nothing | none | `chore(release): prepare v1.4.0` |
| `revert` | Reverts an earlier commit | patch (semantic-release default) | `revert(auth): undo passkey sign-in` |

Any type becomes a **major** release when the commit carries `!` and a `BREAKING-CHANGE` trailer ([breaking changes](breaking-changes.md)).

Angular's own guidelines have since dropped `chore` and `style`, yet commitlint and most tooling still accept them. Follow the repository.

## Decision procedure

Ask these in order and stop at the first "yes":

1. Does it **remove or incompatibly change** a public contract? Pick the type below, then add `!` and `BREAKING-CHANGE`.
2. Does it **undo** a previous commit? → `revert`
3. Does it change **observable behavior to correct a defect**? → `fix`
4. Does it **add observable capability** for users or API consumers? → `feat`
5. Is the only goal **speed or resource use**, with identical behavior? → `perf`
6. Is it **code restructuring** with identical behavior? → `refactor`
7. Is it **formatting only**, with no change to the syntax tree that matters? → `style`
8. Does it touch **only tests**? → `test`
9. Does it touch **only documentation**? → `docs`
10. Does it touch **only CI configuration**? → `ci`
11. Does it change **how the project is built, packaged, or which dependencies it uses**? → `build`
12. Otherwise → `chore`

If two answers seem true, the commit probably holds two changes; see [atomic commits](atomic-commits.md).

## Resolving the common confusions

| Dilemma | Rule |
| :--- | :--- |
| `fix` or `feat` | Was the old behavior a defect against intended behavior? `fix`. Is this behavior new? `feat`. |
| `refactor` or `perf` | Was speed the goal, with a measurement to show it? `perf`. Otherwise `refactor`. |
| `refactor` or `style` | Did code structure change (names, functions, modules)? `refactor`. Only layout? `style`. |
| `build` or `chore` | Does it affect the build output, packaging, or dependencies? `build`. |
| `build` or `ci` | Does it run only in the pipeline (workflow files)? `ci`. Also locally? `build`. |
| `docs` for a docs bug | A typo or wrong statement in docs is `docs`, not `fix`; `fix` implies a patch release. |
| `test` while fixing a bug | The test ships with the fix in one `fix` commit. A test added later on its own is `test`. |
| Dependency bumps | `build(deps)` by default. Use `fix(deps)` only when the bump fixes a user-visible bug and a patch release is wanted; release tools do not release on `build` or `chore`. |
| Security fix | `fix(<area>)`, with the security impact in the body. Avoid a custom `security` type. |
| Hotfix | `fix`. Urgency is not a type. |
| Initial commit | `feat(init)` or `chore(init)`, following the repository's existing history. |

**Avoid invented types** such as `feature`, `bugfix`, `hotfix`, `patch`, `minor`, `update`, or `security`. They fall outside `type-enum` and are ignored or rejected by release tools. When a repository already defines custom types (Vue adds `dx`, `workflow`, and `types`), use them as the repository defines them.

## Choosing a scope

The scope names **what part of the system changed**, in a word or two. This skill's contract requires a scope on every commit, because it is what makes `git log --oneline` scannable.

1. **Use the repository's list** if `scope-enum`, a contributing guide, or history defines one.
2. **Otherwise derive it from the change**: the module, package, service, or feature area that owns most of the diff (`src/auth/session.ts` → `auth`).
3. **For non-code areas** use a stable noun: `readme`, `docs`, `deps`, `release`, `actions`, `docker`, `license`, `git`.
4. **For monorepos** use the package name ([monorepo patterns](monorepo-patterns.md)).
5. **Reuse existing scopes.** Check `git log --format=%s | sed -nE 's/^[a-z]+\(([^)]*)\).*/\1/p' | sort | uniq -c | sort -rn | head -20` and pick a known scope before inventing one.

Scopes are lower-case kebab-case nouns of roughly 2-20 characters. Avoid scopes that describe the change instead of the location (`(bug)`, `(update)`, `(misc)`), vague catch-alls (`(core)` when the project has no core module, `(all)`), and file names with extensions.

If one change truly spans several areas, prefer splitting it. When it cannot be split (a cross-cutting rename), use the nearest common area or a repository-wide scope that the project already uses, such as `repo`.
