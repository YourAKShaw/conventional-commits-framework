## What changed and why?

<!-- Describe the problem and the resulting behavior. Link related issues; use "Closes #123" only when this PR resolves the issue. -->

## Verification

<!-- List commands or scenarios actually run and their results. Explain checks not run. For tool-behavior claims, name the tool and version. -->

## Risks or compatibility

<!-- Note changed rules or defaults, host assumptions, and limits. Write "None identified" when appropriate. -->

## Checklist

- [ ] The PR title follows `type(scope): subject`, and each commit is one logical change.
- [ ] `python3 scripts/lint-commit.py --range origin/main..HEAD` passes (with `--trailer` or `--human` as appropriate).
- [ ] `python3 scripts/validate-skill.py` passes, and the test suites pass for script changes.
- [ ] The contract stays identical across SKILL.md, the protocol, the checker, the commitlint config, and the template.
- [ ] Examples and output contain no secrets or private information, and verification claims reflect checks actually performed.
