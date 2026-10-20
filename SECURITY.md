# Security Policy

## Supported versions

This project does not publish versioned releases. Only the latest commit on `main` is supported; fixes are not backported.

| Version | Supported |
| :--- | :---: |
| `main` (latest) | ✅ |
| Older commits | ❌ |

## Scope

The skill is Markdown guidance plus offline Python scripts that use only the standard library. Relevant reports include:

- A script in `scripts/` that runs commands, writes files, or reaches the network when it should not.
- Guidance in `SKILL.md` or `references/` that would lead an agent to leak secrets, bypass hooks or CI, or rewrite published history.
- A workflow in `.github/workflows/` that grants excess permissions or runs untrusted code.

Commit-message rules that are wrong but not unsafe are ordinary bugs; use the [issue forms](https://github.com/YourAKShaw/conventional-commits-framework/issues/new/choose).

## Reporting a vulnerability

Do not open a public issue. Report privately through [GitHub private vulnerability reporting](https://github.com/YourAKShaw/conventional-commits-framework/security/advisories/new) with:

- The affected file and commit.
- Steps to reproduce and the impact you observed.
- A suggested fix, if you have one.

You can expect an acknowledgement within 7 days and a fix or decision within 30 days. Reporters are credited in the advisory unless they ask otherwise.
