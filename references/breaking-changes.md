# Breaking changes

A breaking change is any change that can make an existing, correct consumer fail or behave differently without that consumer changing. Release tools turn it into a **major** version, so it must never be missed, and it must never be declared by accident.

## Detect

Treat a change as breaking when it does any of the following to a **public contract** (anything a user, API client, downstream package, script, or deployment relies on):

| Surface | Breaking examples |
| :--- | :--- |
| Code API | Remove or rename an exported function, class, type, or option; add a required parameter; narrow accepted input; widen thrown errors |
| HTTP/RPC API | Remove an endpoint or field; rename a field; change a status code, type, or default; tighten validation; require new auth |
| CLI | Remove or rename a command or flag; change output format that scripts parse; change exit codes |
| Configuration | Remove or rename a key or environment variable; change a default that alters behavior |
| Data | Incompatible schema or file-format change; migration without backward-compatible reads |
| Runtime support | Drop a Node, Python, OS, or browser version; raise a peer-dependency floor |
| Behavior | Same signature, different semantics: ordering, rounding, time zones, retries, permissions |

These are usually **not** breaking: additive optional fields or parameters, new endpoints, internal refactors, performance changes, bug fixes that restore documented behavior, and changes to explicitly experimental or private APIs. Pre-1.0 (`0.y.z`) projects may break in minor releases by SemVer, but the commit is still marked so the changelog says so.

When unsure, ask "can a consumer who upgrades without reading the changelog get a failure?" If yes, it is breaking. If the answer depends on product policy, ask the user.

## Declare

Every commit makes an explicit declaration. A non-breaking commit ends its trailers with:

```text
Breaking: none
```

A breaking commit uses **both** markers:

1. `!` immediately before the colon in the header: `feat(api)!: ...`, `refactor(config)!: ...`
2. A `BREAKING-CHANGE` trailer stating **what breaks** and **how to migrate**, with continuation lines indented by two spaces:

```text
feat(api)!: remove legacy v1 login endpoint

The v1 login endpoint bypassed rate limiting and has been deprecated
since 2.3. Removing it closes the gap and drops 400 lines of
compatibility code.

BREAKING-CHANGE: POST /v1/login is removed. Clients must call
  POST /v2/sessions, which takes the same credentials and returns a
  session object; see docs/migrate-v2.md.
Refs: #512
Co-Authored-By: Claude Code <noreply@anthropic.com>
```

Any type can be breaking. Use the type that describes the change itself (`feat`, `fix`, `refactor`, `build`, ...); the `!` and trailer carry the major bump.

## Three format traps

These were verified against `conventional-commits-parser` 7.1.3, `git interpret-trailers`, and `@commitlint/cli` 21.2.4.

1. **`BREAKING CHANGE: none` declares a breaking change.** Parsers record any text after the token, matched case-insensitively, as a breaking note, so `BREAKING CHANGE: none`, `BREAKING-CHANGE: none`, and `breaking change: n/a` all trigger a major release. Use `Breaking: none`, which no release tool treats as a breaking note.
2. **The spaced token hides your trailers.** Git trailer keys cannot contain spaces, so a footer containing `BREAKING CHANGE:` is not a trailer block for git. `Co-Authored-By` and `Refs` in the same block become invisible to `git interpret-trailers`, `%(trailers)`, and commitlint's `trailer-exists`. The spec states that `BREAKING-CHANGE` is synonymous, and every parser accepts it.
3. **Unindented continuation lines break the block too.** A second line of breaking detail that does not start with whitespace ends the trailer block for git. Indent continuations by two spaces; parsers keep them in the note text.

## Write the migration note

A good `BREAKING-CHANGE` trailer is 1-4 lines and answers:

- **What** stopped working (the exact name, endpoint, flag, or behavior).
- **Who** is affected, if not everyone.
- **What to do instead**, concretely, with a link for longer guides.

Weak: `BREAKING-CHANGE: API changed.`
Strong: `BREAKING-CHANGE: hash() now takes an options object; replace hash(data, "sha256") with hash(data, { algorithm: "sha256" }).`

## Ship breaking changes safely

Breaking changes deserve their own atomic commits. Where possible, stage them across releases: add the new path (`feat`), deprecate the old path with a warning (`feat` or `refactor`, non-breaking), then remove it (`!` with `BREAKING-CHANGE`). This gives consumers a migration window. Never smuggle a breaking change into a commit typed as a refactor or a fix without the markers. Agents must confirm with the user before making a breaking change they were not explicitly asked for.
