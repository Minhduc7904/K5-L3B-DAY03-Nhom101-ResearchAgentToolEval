---
name: text_stats
track: group
kind: local_formatter
requires_env: []
inputs: [text, limit]
outputs: [chars, words, reading_seconds, limit, over_limit, remaining]
side_effect: false
---
# text_stats

Counts characters and words of a text the model already has, estimates the reading time
(200 words per minute) and checks it against a length limit (default 280, a tweet).
Use it before posting or threading a text: language models are unreliable at counting characters.
Pure local tool: no network, no API key.

- `remaining` is negative when the text is over the limit.
- Counts are over the text as given (code points, not bytes).

Errors come back as a dict with an `error` key instead of raising: `EmptyText` (empty or not a
string), `TooLong` (over 100,000 chars), `InvalidLimit` (not a positive integer).
