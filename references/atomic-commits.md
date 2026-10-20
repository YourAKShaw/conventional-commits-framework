# Atomic commits: the smallest logical change

An agent commits **the smallest change that is complete on its own**. Large work is delivered as a sequence of small, well-described commits, not one commit containing everything.

Small commits are what make Conventional Commits useful. One commit has one type, so a changelog entry, a version bump, a `git revert`, and a `git bisect` step all act on exactly one idea. A commit that mixes a feature, a refactor, and a dependency bump can only be labelled honestly as none of them.

## What "smallest" means

A commit is atomic when all of these are true:

1. **One purpose.** It fits one type and one subject without "and". `feat(auth): add passkey login and refactor session store` is two commits.
2. **Complete.** The repository builds, and existing tests pass, at this commit. Tests that cover the change land in the same commit or the next one, never several commits later.
3. **Self-explaining.** Its message, read alone, tells a reviewer what changed and why.
4. **Independently revertable.** Reverting it removes exactly one idea without breaking unrelated work.

"Smallest" is about logical scope, not line count. A one-line fix and a 300-line generated migration can each be atomic; a 20-line diff that also renames an unrelated variable is not.

## Split along these seams

| Keep separate | Example sequence |
| :--- | :--- |
| Refactor vs behavior change | `refactor(cart): extract price calculator` → `feat(cart): apply tiered discounts` |
| Formatting vs logic | `style(api): apply formatter to handlers` → `fix(api): return 404 for missing orders` |
| Dependency vs code using it | `build(deps): add zod 3.23` → `feat(api): validate order payloads with zod` |
| Rename/move vs edit | `refactor(utils): move date helpers to lib/time` → `fix(time): handle DST in addDays` |
| Each independent fix | `fix(cache): …` and `fix(auth): …` are two commits even if found together |
| Docs for new behavior | Same commit as the behavior, or the very next `docs(...)` commit |
| Generated output | Lockfiles and codegen go with the change that produced them, not on their own |

## Workflow for large work

When a task is bigger than one logical change, the agent plans the commit sequence before writing code:

1. **Outline the commits.** List them as headers first, ordered so each one leaves the repository working:
   ```text
   build(deps): add argon2 password hashing library
   refactor(auth): isolate password hashing behind a hasher interface
   feat(auth): hash new passwords with argon2id
   feat(auth): rehash legacy bcrypt passwords on successful login
   test(auth): cover legacy rehash and failed-login paths
   docs(auth): document the password hashing migration
   ```
2. **Work one item at a time.** Implement, verify, stage only that change, commit with a complete message, then move to the next item.
3. **Stage precisely.** Use `git add <paths>` or `git add -p` to stage one concern. Check `git diff --staged` before every commit.
4. **Re-plan when the work changes shape.** If a step turns out to need a prerequisite, commit the prerequisite first.
5. **Never batch at the end.** Do not let many concerns accumulate in the working tree and commit them together. If that happened anyway, split them with `git add -p` into separate commits rather than writing one commit that lists everything.

## Signals that a commit is too big

- The subject needs "and", "also", a comma list, or a vague word such as `update`, `changes`, or `misc`.
- The body has several unrelated paragraphs or a bullet list of unrelated items.
- More than one type fits, or the honest type is `chore` only because it hides several things.
- Reviewers would need to read it in several passes, or a revert would undo something you want to keep.

As a heuristic rather than a rule, most atomic commits touch a handful of files and stay well under a few hundred changed lines, excluding generated files.

## Signals that a commit is too small

Atomic does not mean fragmented. Combine when:

- A commit would leave the build or tests broken until the next one.
- Two commits fix typos in the same paragraph, or the second commit only fixes a mistake introduced by the first. Before pushing, fold the fix-up into the original with `git commit --fixup <sha>` and `git rebase -i --autosquash`; after pushing, leave history alone.
- A test and the code it covers would be meaningless apart.

## Squash-merge repositories

Some projects squash each PR into one commit on `main`, so the PR title becomes the commit header. Keep commits atomic on the branch anyway (reviewers read them, and bisecting a branch still helps). Keep the PR to one logical change so the squashed commit is atomic too, and write the PR title and description to the same contract.
