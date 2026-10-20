// commitlint configuration for the Complete Commit Contract.
// Install: npm i -D @commitlint/cli @commitlint/config-conventional
// Set CO_AUTHOR once to the trailer your repository uses, then never change it.

const CO_AUTHOR = 'Co-Authored-By: Claude Code <noreply@anthropic.com>';

const lines = (raw) => (raw || '').split('\n').map((line) => line.trimEnd());

export default {
  extends: ['@commitlint/config-conventional'],
  plugins: [
    {
      rules: {
        'breaking-declared': ({ raw, notes }) => {
          const declared = lines(raw).filter((line) => line.startsWith('Breaking: '));
          const breaking = (notes || []).length > 0;
          if (breaking === (declared.length > 0)) {
            return [false, "declare exactly one of 'Breaking: none' or 'BREAKING-CHANGE: <impact>'"];
          }
          if (declared.length && declared.some((line) => line !== 'Breaking: none')) {
            return [false, "the non-breaking form is exactly 'Breaking: none'"];
          }
          return [true];
        },
        'breaking-token': ({ raw }) => [
          !lines(raw).some((line) => line.startsWith('BREAKING CHANGE:')),
          'write BREAKING-CHANGE (hyphen); the spaced form hides the git trailer block',
        ],
        'co-author-exact': ({ raw }, when = 'always', expected = CO_AUTHOR) => {
          const coAuthors = lines(raw).filter((line) => /^co-authored-by:/i.test(line));
          if (when === 'never') return [true];
          return [
            coAuthors.length > 0 && coAuthors.every((line) => line === expected),
            `AI-assisted commits must end with exactly: ${expected}`,
          ];
        },
      },
    },
  ],
  rules: {
    'header-max-length': [2, 'always', 72],
    'scope-empty': [2, 'never'],
    'scope-case': [2, 'always', 'kebab-case'],
    'subject-min-length': [2, 'always', 10],
    'body-leading-blank': [2, 'always'],
    'body-empty': [2, 'never'],
    'body-min-length': [2, 'always', 40],
    'footer-leading-blank': [2, 'always'],
    'footer-empty': [2, 'never'],
    'breaking-change-exclamation-mark': [2, 'always'],
    'breaking-declared': [2, 'always'],
    'breaking-token': [2, 'always'],
    // Set to [0] for repositories or commits with no AI involvement.
    'co-author-exact': [2, 'always', CO_AUTHOR],
  },
};
