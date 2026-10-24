// commitlint configuration for the Complete Commit Contract.
// Install: npm i -D @commitlint/cli @commitlint/config-conventional
// Keep accepted agent trailers in sync with the repository's documented policy.

const CO_AUTHORS = [
  'Co-Authored-By: Claude Code <noreply@anthropic.com>',
  'Co-Authored-By: ChatGPT <noreply@openai.com>',
];

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
        'co-author-exact': ({ raw }, when = 'always', expected = CO_AUTHORS) => {
          if (when === 'never') return [true];
          const coAuthors = lines(raw).filter((line) => /^co-authored-by:/i.test(line));
          const emails = expected.map((line) => line.slice(line.lastIndexOf('<')));
          const varied = coAuthors.some((line) => !expected.includes(line) && emails.some((email) => line.endsWith(email)));
          const wrongKey = coAuthors.some((line) => !line.startsWith('Co-Authored-By: '));
          return [
            coAuthors.some((line) => expected.includes(line)) && !varied && !wrongKey,
            `AI-assisted commits need one accepted agent trailer: ${expected.join(' or ')}`,
          ];
        },
      },
    },
  ],
  rules: {
    'header-max-length': [2, 'always', 72],
    'scope-empty': [2, 'never'],
    'scope-case': [2, 'always', 'lower-case'],
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
    'co-author-exact': [2, 'always', CO_AUTHORS],
  },
};
