---
name: artifact
track: core
kind: local_formatter
requires_env: []
inputs: [title, html]
outputs: [artifact, status]
side_effect: false
---
# artifact

Turns an answer into an interactive HTML page (a table you can filter, a chart, a small
calculator). The web UI renders it inline under the assistant's message.

Simplified from how Claude Artifacts and ChatGPT Canvas work:

1. The model writes self-contained content: HTML with inline `<style>` and `<script>`.
   Chart libraries may load from `cdn.jsdelivr.net` or `cdnjs.cloudflare.com`.
2. The tool wraps it in a full document with a Content-Security-Policy `<meta>`:
   `connect-src 'none'` blocks fetch/XHR/WebSocket, and images and fonts only load from `data:`,
   so the page cannot load other resources or send data anywhere.
3. The UI renders it in `<iframe sandbox="allow-scripts" srcdoc=...>`. Without
   `allow-same-origin`, the frame has an opaque origin: its scripts run but cannot touch
   the app's DOM, cookies or `/api`.

`html` is the content that goes inside `<body>`. The tool adds the doctype, charset, viewport,
title and base styles. If the model sends a full document anyway (it often does), the tool
inserts the CSP as the first tag inside that document's `<head>` instead of wrapping it again. The result has `artifact: {id, title, html}`; the server sends it to
the UI as `artifacts[]`, and the transcript keeps the full document as evidence.

Errors come back as a dict with an `error` key instead of raising: `EmptyHtml`
(empty or not a string) and `TooLarge` (over 200,000 chars).
