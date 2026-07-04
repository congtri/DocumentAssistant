# Commit Message Rules

When generating commit messages, use the following format:

Change: <short summary of the overall change>

- <file name>: <description of changes>
- <file name>: <description of changes>
- <file name>: <description of changes>

Rules:

- The first line must start with `Change:`.
- Summarize the purpose of the change in one sentence.
- Include the most important modified files.
- Describe what changed in each file.
- Use English.
- Keep descriptions concise.
- Do not use Conventional Commits.
- Do not include Git hashes, author names, or timestamps.

Example:

Change: Add initial chatbot API and configuration support

- src/api/chat.py: implement chat completion endpoint
- src/core/config.py: add model configuration loader
- tests/test_chat.py: add API unit tests
- README.md: document setup and usage

Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:
- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
