# Emoji reference

Emoji are an optional decoration on top of Conventional Commits, never a replacement for the type. **Use them only when the repository already does**, and then copy its exact style. Never introduce emoji into a repository whose history has none.

[Gitmoji](https://gitmoji.dev) is the dominant emoji vocabulary. Release tools such as release-please parse plain Conventional Commits and do not read emoji, so the type must always carry the meaning.

## Placement: after the colon

```text
feat(auth): :sparkles: add passkey sign-in       ← shortcode form
feat(auth): ✨ add passkey sign-in               ← unicode form
✨ feat(auth): add passkey sign-in               ← breaks Conventional Commits parsers
```

Put the emoji at the start of the subject, after `: `. Verified with `conventional-commits-parser` 7.1.3, the type and scope still parse and the emoji becomes part of the subject. An emoji **before** the type makes the header unparseable, so the commit is dropped from changelogs and version calculations.

Rules when a repository uses emoji:

- **One form.** Shortcodes (`:sparkles:`) or unicode (`✨`), whichever history uses. Do not mix, for the same reason the co-author trailer never varies.
- **One emoji per commit**, matching the type and the actual change.
- **Length still counts.** The emoji is part of the header; keep the header at 72 characters or fewer and the text after the emoji at 10-50.
- **Lower-case text after it**: `:bug: fix ...` is wrong because the verb duplicates the type; write `fix(api): :bug: return 404 for missing orders`.

## Type-to-gitmoji mapping

| Type | Gitmoji | Shortcode | Gitmoji meaning |
| :--- | :---: | :--- | :--- |
| `feat` | ✨ | `:sparkles:` | Introduce new features |
| `fix` | 🐛 | `:bug:` | Fix a bug |
| `fix` (critical, urgent) | 🚑️ | `:ambulance:` | Critical hotfix |
| `fix` (security) | 🔒️ | `:lock:` | Fix security or privacy issues |
| `docs` | 📝 | `:memo:` | Add or update documentation |
| `style` | 🎨 | `:art:` | Improve structure or format of the code |
| `refactor` | ♻️ | `:recycle:` | Refactor code |
| `perf` | ⚡️ | `:zap:` | Improve performance |
| `test` | ✅ | `:white_check_mark:` | Add, update, or pass tests |
| `build` | 📦️ | `:package:` | Add or update compiled files or packages |
| `build(deps)` upgrade | ⬆️ | `:arrow_up:` | Upgrade dependencies |
| `build(deps)` add | ➕ | `:heavy_plus_sign:` | Add a dependency |
| `ci` | 👷 | `:construction_worker:` | Add or update CI build system |
| `ci` (fix a failing build) | 💚 | `:green_heart:` | Fix CI build |
| `chore` (configuration) | 🔧 | `:wrench:` | Add or update configuration files |
| `chore(git)` ignore files | 🙈 | `:see_no_evil:` | Add or update a .gitignore file |
| `chore(license)` | 📄 | `:page_facing_up:` | Add or update license |
| `chore(release)` | 🔖 | `:bookmark:` | Release or version tags |
| `revert` | ⏪️ | `:rewind:` | Revert changes |
| removal of code or files | 🔥 | `:fire:` | Remove code or files |
| initial commit | 🎉 | `:tada:` | Begin a project |

`💥 :boom:` means "introduce breaking changes". Use it **only** on commits that carry `!` and a `BREAKING-CHANGE` trailer, and never as a substitute for them.

When the meaning is ambiguous, choose by the type first, then by the most specific gitmoji for the actual change. A security fix is `fix(auth): :lock: ...`, not `security: ...`.

## Tooling

- **Plain Conventional Commits with optional emoji:** commitlint accepts an emoji after the colon, but `subject-case` and length rules apply to the whole subject.
- **Emoji-driven release tools** (`semantic-release-gitmoji`, `gitmoji-changelog`) treat the emoji as the source of truth. Repositories using them follow gitmoji's own format; read their config before committing.
- **Generators** such as `gitmoji-cli`, `devmoji`, and `cz-conventional-gitmoji` insert emoji automatically. If a hook adds the emoji, the agent writes the message without it.
