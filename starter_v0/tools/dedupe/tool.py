from __future__ import annotations

import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from tools._shared import fold_text

KEYS = ("url", "title")
TRACKING_PARAMS = {"fbclid", "gclid", "ref", "ref_src"}


def _normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    query = sorted((k, v) for k, v in parse_qsl(parsed.query) if not k.lower().startswith("utm_") and k.lower() not in TRACKING_PARAMS)
    path = parsed.path.rstrip("/")
    return urlunparse((parsed.scheme.lower(), host, path, "", urlencode(query), ""))


def _normalize_title(title: str) -> str:
    # fold_text does not decompose Vietnamese "đ", so map it first; otherwise "Đà Nẵng" and "À Nẵng" collide.
    return " ".join(re.findall(r"[a-z0-9]+", fold_text(title.replace("đ", "d").replace("Đ", "D"))))


def _identity(item: dict[str, Any], key: str) -> str:
    url = item.get("url") if isinstance(item.get("url"), str) else ""
    title = item.get("title") if isinstance(item.get("title"), str) else ""
    first, second = (("url", url), ("title", title)) if key == "url" else (("title", title), ("url", url))
    for kind, value in (first, second):
        normalized = _normalize_url(value) if kind == "url" and value.strip() else _normalize_title(value) if kind == "title" else ""
        if normalized:  # a title with no latin letters or digits (CJK, "!!!") normalizes to "": nothing to compare
            return f"{kind}:{normalized}"
    return ""


def dedupe_items(items: list[dict[str, Any]] | None = None, key: str = "url") -> dict[str, Any]:
    tool = "dedupe_items"
    if key not in KEYS:
        return {"tool": tool, "error": "UnknownKey", "message": f"key must be one of {list(KEYS)}"}
    if items is None:
        items = []
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        return {"tool": tool, "error": "InvalidItems", "message": "items must be a list of objects with title/url"}

    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    for item in items:
        identity = _identity(item, key)
        if identity and identity in seen:
            continue  # first occurrence wins, order is preserved
        if identity:
            seen.add(identity)
        kept.append(item)
    return {"tool": tool, "key": key, "items": kept, "kept": len(kept), "removed": len(items) - len(kept)}
