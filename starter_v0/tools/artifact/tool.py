from __future__ import annotations

import hashlib
import html as html_lib
import re
from typing import Any

MAX_CHARS = 200_000

# Inline code only, plus two public CDNs for chart libraries. connect-src 'none' blocks
# fetch/XHR/WebSocket, so the page cannot send data anywhere.
CSP = (
    "default-src 'none'; "
    "script-src 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
    "style-src 'unsafe-inline'; img-src data: blob:; font-src data:; "
    "connect-src 'none'; form-action 'none'; base-uri 'none'"
)

TEMPLATE = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ margin: 0; padding: 16px; font: 14px/1.5 system-ui, sans-serif; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def render_artifact(title: str = "", html: str = "") -> dict[str, Any]:
    if not isinstance(html, str) or not html.strip():
        return {"tool": "render_artifact", "error": "EmptyHtml", "message": "html must be a non-empty string with the page content"}
    if len(html) > MAX_CHARS:
        return {"tool": "render_artifact", "error": "TooLarge", "message": f"html is {len(html)} chars, limit is {MAX_CHARS}"}
    title = (title if isinstance(title, str) else "").strip() or "Artifact"
    head = re.search(r"<head(\s[^>]*)?>", html, re.IGNORECASE)  # not <header>
    if head:
        # Model sent a full document: put the CSP first inside its own <head>.
        document = f'{html[:head.end()]}\n<meta http-equiv="Content-Security-Policy" content="{CSP}">{html[head.end():]}'
    else:
        document = TEMPLATE.format(csp=CSP, title=html_lib.escape(title), body=html.strip())
    artifact_id = hashlib.sha1(document.encode("utf-8")).hexdigest()[:10]
    return {
        "tool": "render_artifact",
        "status": "rendered",
        "artifact": {"id": artifact_id, "title": title, "html": document},
    }
