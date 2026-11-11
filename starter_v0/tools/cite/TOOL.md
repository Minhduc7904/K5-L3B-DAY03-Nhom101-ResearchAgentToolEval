---
name: cite
track: group
kind: local_formatter
requires_env: []
inputs: [title, authors, year, url, style]
outputs: [citation, style, has_url]
side_effect: false
---
# cite

Formats one source (paper, article, tweet thread) as a citation string. Pure local formatter:
no network, no API key. Use it after `papers`, `lookup` or `fetch` have returned the metadata,
so every factual item in a digest has a source (see `company_policy/source-citation-policy.md`).

Styles: `apa` (default), `ieee`, `bibtex` (a `@misc{...}` entry; the key is surname + year + first
title word, ASCII-folded).

Notes:

- `authors` is a list of names or one string (`"A. Ng; B. Lee"` or `"A. Ng and B. Lee"`).
- A missing or malformed `year` becomes `n.d.`; missing authors become `Unknown author`.
- The tool never invents metadata: it only formats what the model passes in.

Errors come back as a dict with an `error` key instead of raising: `MissingTitle`,
`UnknownStyle`, `InvalidAuthors`.
