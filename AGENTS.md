# AGENTS.md

Working rules for AI agents in this repo.

The project roadmap and current status live in [`PLAN.md`](PLAN.md) (a thin
index); the detail is under [`docs/`](docs/). Read `PLAN.md` before starting
work — it points to everything else.

## How we work

Two modes, and the mode picks the method:

- **Building** (a feature or change): follow the lifecycle
  `/spec → /plan → /build → /review → /ship` (slash commands in
  [`.claude/commands/`](.claude/commands/), skills in
  [`.claude/skills/`](.claude/skills/)), with test-driven development and small
  atomic commits as the default.
- **Experimenting** (learning something — a prompt, variance, a failure, "is X
  worth building?"): follow the
  **[experiment playbook](docs/experiments/playbook.md)** — hypothesis → logged,
  timestamped run → empirical results → attributable conclusion → a `REPORT.md`.
  This is the ML side the coding skills don't cover. An experiment's report
  *feeds* a `/spec` or a decision; don't build straight from a hunch.

Before touching code, read [`docs/conventions.md`](docs/conventions.md) (codebase
map, commands, hazards). **Source-of-truth rule:** where a doc and the code
disagree, the **code wins** unless the doc is explicitly the spec being
implemented; docs known to have drifted carry a **Provisional** banner
(currently: `docs/patch-extraction.md` and the D1–D8 decision log). Record
decisions worth remembering in [`docs/decisions/`](docs/decisions/).

## Communicating with the user

- **Voice input.** The user often interacts via voice, so their messages are
  produced by speech-to-text and may contain transcription errors: wrong
  homophones, dropped or merged words, mis-split phrases, and mistranscribed
  proper nouns. Read for intent rather than literal text. For example, "cloud"
  can mean "Claude". When a word looks out of place, infer the intended meaning
  from context instead of taking it at face value.

- **Identifiers are especially fragile.** Speech-to-text often cannot reproduce
  the exact spelling of file paths, variable names, and function names,
  particularly special characters and separators such as dots, hyphens, dashes,
  slashes, underscores, and camelCase boundaries (e.g. "doc" may be "dot",
  "dash" and "hyphen" may be dropped or swapped). Do your best to reconstruct
  the most plausible intended identifier — cross-check it against names that
  actually exist in the codebase when possible.

- **Flag and confirm your guesses.** Whenever you infer an identifier or resolve
  an ambiguous term, call it out **explicitly** in your summary — list only the
  specific guesses you made — and ask the user to confirm each one. Be ready to
  update if a guess is wrong.

- **Latest instruction wins.** The user's thinking may not be fully formed when
  they first describe something, and they refine it as they go. Always follow
  the most recent instruction over earlier ones. If a request seems to
  contradict something said before, the latest wording takes precedence — the
  user will clarify if there is a genuine conflict.

- **Reply in the user's language — this is important and often missed.** Look at
  the language of the user's **most recent message** and write your chat reply in
  **that same language**. If they wrote in Chinese, reply in Chinese; if in
  English, reply in English. Check this on **every** turn, because the user
  switches languages mid-conversation — do not default to English out of habit
  just because the code, this file, or the earlier conversation is in English.
  The language of the repository does **not** determine the language of your
  reply. This applies to the whole chat reply, including summaries and follow-up
  questions.

## Language of the codebase

- The two rules below are independent: **what you write into the repo** is always
  English, but **how you talk to the user** follows their language (see above).
  A Chinese message still gets a Chinese reply even though any code or docs you
  produce in that same turn are written in English.
- All code, comments, documentation, commit messages, and README content must
  be written in **English**, regardless of the language the user is speaking or
  typing in.
- Accept user input in any language, but keep everything that lands in the
  repository in English.

## Naming conventions

- **Strict camelCase / PascalCase for acronyms and initialisms.** Treat an
  acronym as an ordinary word: capitalize only its first letter. Write
  `SweBenchProInstance`, not `SWEbenchProInstance`; `Http`, not `HTTP`;
  `JsonParser`, not `JSONParser`; `httpClient`, not `HTTPClient`. This keeps word
  boundaries unambiguous and casing mechanical. (snake_case identifiers such as
  module names are unaffected.)
