from __future__ import annotations

from typing import Any

MAX_CHARS = 100_000
WORDS_PER_MINUTE = 200


def text_stats(text: str = "", limit: int = 280) -> dict[str, Any]:
    tool = "text_stats"
    if not isinstance(text, str) or not text.strip():
        return {"tool": tool, "error": "EmptyText", "message": "text must be a non-empty string"}
    if len(text) > MAX_CHARS:
        return {"tool": tool, "error": "TooLong", "message": f"text is {len(text)} chars, limit is {MAX_CHARS}"}
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        return {"tool": tool, "error": "InvalidLimit", "message": "limit must be a positive integer"}

    words = len(text.split())
    chars = len(text)
    return {
        "tool": tool,
        "chars": chars,
        "words": words,
        "reading_seconds": round(words * 60 / WORDS_PER_MINUTE),
        "limit": limit,
        "over_limit": chars > limit,
        "remaining": limit - chars,
    }
