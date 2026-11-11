---
name: dedupe
track: group
kind: local_formatter
requires_env: []
inputs: [items, key]
outputs: [items, kept, removed]
side_effect: false
---
# dedupe

Removes duplicate results when the same story comes back from several searches (for example
`lookup` and `social_search` run in one turn). Pure local tool: no network, no API key.

- `key="url"` (default): two items are the same if their normalized URLs match. Normalization lowercases the host,
  drops `www.`, the fragment, a trailing `/`, and tracking parameters (`utm_*`, `fbclid`, `gclid`, `ref`, `ref_src`), and sorts
  the remaining query parameters. It does not merge `http` with `https`, default ports or different path casing.
- `key="title"`: compares titles after folding accents (including Vietnamese `đ`), case and punctuation. A title with no
  latin letters or digits (for example Chinese or `!!!`) cannot be compared, so it is kept.
- An item missing the chosen key falls back to the other one; an item with neither is kept
  (nothing to compare).
- The first occurrence is kept and the order is preserved.

Errors come back as a dict with an `error` key instead of raising: `UnknownKey`, `InvalidItems`
(not a list, or a list with non-object entries).
