# commitlint rules reference

commitlint is the de facto validator for Conventional Commits. This page explains each built-in rule in plain terms, so you can validate a message by reasoning and translate a project's config into expectations. Verified against `@commitlint/rules` **21.2.4**, which ships **38 rules**. Older plans and articles cite 36 because `breaking-change-exclamation-mark` and `scope-delimiter-style` were added later; check the project's installed version when exact behavior matters.

## How a rule is configured

```js
'rule-name': [level, applicable, value]
```

- **level**: `0` disabled, `1` warning, `2` error (blocks the commit or CI check).
- **applicable**: `'always'` or `'never'` (inverts the rule).
- **value**: the rule's argument, such as a length or a list.

Columns below: **Conventional** is the `@commitlint/config-conventional` setting (`—` = not set, so the rule is off). **Contract** is the setting in this skill's [commitlint config](../assets/commitlint.config.mjs).

## Type

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `type-empty` | A type is present | error, never empty | inherited |
| `type-enum` | Type is in the allowed list | error: build, chore, ci, docs, feat, fix, perf, refactor, revert, style, test | inherited |
| `type-case` | Type letter case | error, lower-case | inherited |
| `type-min-length` | Type has at least N characters | — | — |
| `type-max-length` | Type has at most N characters | — | — |

## Scope

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `scope-empty` | A scope is present (`never` = required) | — | **error, required** |
| `scope-enum` | Scope is in the allowed list; multi-scopes split on `/`, `\`, `,` | — | set per project |
| `scope-case` | Scope letter case | — | **error, kebab-case** |
| `scope-min-length` | Scope has at least N characters | — | — |
| `scope-max-length` | Scope has at most N characters | — | — |
| `scope-delimiter-style` | Characters between multiple scopes are in the allowed list (default `/`, `\`, `,`) | — | — |

## Subject

The subject is the text after `: ` in the header.

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `subject-empty` | Subject is present | error, never empty | inherited |
| `subject-case` | Subject letter case | error, never sentence-, start-, pascal-, or upper-case | inherited |
| `subject-full-stop` | Subject ends with the given character | error, never `.` | inherited |
| `subject-min-length` | Subject has at least N characters | — | **error, 10** |
| `subject-max-length` | Subject has at most N characters | — | (header limit covers it) |
| `subject-exclamation-mark` | Header has the `!` breaking marker before the colon. It does **not** check the end of the subject. | — | — |

## Header

The header is the whole first line: `type(scope)!: subject`.

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `header-max-length` | Header has at most N characters | error, 100 | **error, 72** |
| `header-min-length` | Header has at least N characters | — | — |
| `header-case` | Header letter case | — | — |
| `header-full-stop` | Header ends with the given character | — | — |
| `header-trim` | No leading or trailing whitespace | error | inherited |

## Body

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `body-leading-blank` | Blank line between header and body | warning | **error** |
| `body-empty` | A body is present (`never` = required) | — | **error, required** |
| `body-min-length` | Body has at least N characters | — | **error, 40** |
| `body-max-length` | Body has at most N characters in total | — | — |
| `body-max-line-length` | Every body line has at most N characters | error, 100 | inherited (wrap at 72 by habit) |
| `body-case` | Body letter case | — | — |
| `body-full-stop` | Body ends with the given character | — | — |

## Footer

The footer is the trailing block of `Token: value` lines, including `BREAKING-CHANGE`.

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `footer-leading-blank` | Blank line before the footer | warning | **error** |
| `footer-empty` | A footer is present (`never` = required) | — | **error, required** |
| `footer-min-length` | Footer has at least N characters | — | — |
| `footer-max-length` | Footer has at most N characters | — | — |
| `footer-max-line-length` | Every footer line has at most N characters | error, 100 | inherited |

## References, trailers, and breaking changes

| Rule | Checks | Conventional | Contract |
| :--- | :--- | :--- | :--- |
| `references-empty` | Message references an issue, such as `#123` (`never` = required) | — | — (Refs only when real) |
| `signed-off-by` | Message has the given `Signed-off-by:` trailer | — | set per project (DCO) |
| `trailer-exists` | Message has the given trailer, parsed by `git interpret-trailers`; the key match is case-sensitive | — | replaced by `co-author-exact` |
| `breaking-change-exclamation-mark` | Header `!` and a `BREAKING CHANGE:` or `BREAKING-CHANGE:` footer appear together or not at all | — | **error** |

## Contract plugin rules

The skill's [commitlint config](../assets/commitlint.config.mjs) adds three local plugin rules for what built-in rules cannot express:

| Rule | Checks |
| :--- | :--- |
| `breaking-declared` | Exactly one of `Breaking: none` or a breaking note is present |
| `breaking-token` | The footer uses `BREAKING-CHANGE` (hyphen), because the spaced form breaks git trailer parsing |
| `co-author-exact` | Every `Co-Authored-By` line equals the repository's one recorded trailer |

## Validating by hand

When no tool is available, check in this order and report every failure with its rule name:

1. **Header shape**: `type(scope)!: subject`, one space after the colon, no surrounding whitespace.
2. **Type**: allowed and lower-case.
3. **Scope**: present, kebab-case, from the project list when one exists.
4. **Subject**: present, lower-case start, imperative, no trailing period, and a header of 72 characters or fewer.
5. **Body**: present after a blank line, explains why, lines wrapped (100 characters at most).
6. **Footer**: present after a blank line; trailers are `Token: value` (`BREAKING-CHANGE` is the one token allowed in upper case).
7. **Breaking consistency**: `!` if and only if `BREAKING-CHANGE`; otherwise `Breaking: none`.
8. **Co-author**: matches the repository's recorded trailer exactly.

Distinguish **errors** (violate the spec or the project config) from **suggestions** (style improvements the config does not enforce), and do not present suggestions as violations.
