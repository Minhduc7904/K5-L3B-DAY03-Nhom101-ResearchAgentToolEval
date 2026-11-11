from __future__ import annotations

import re
from typing import Any

from tools._shared import fold_text

STYLES = ("apa", "bibtex", "ieee")


def _clean_authors(authors: Any) -> list[str] | None:
    if authors is None or authors == "":
        return []
    if isinstance(authors, str):
        authors = [part.strip() for part in re.split(r";|\band\b", authors) if part.strip()]
    if not isinstance(authors, list) or not all(isinstance(item, str) for item in authors):
        return None
    return [item.strip() for item in authors if item.strip()]


def _clean_year(year: Any) -> str:
    text = str(year).strip() if year is not None else ""
    return text if re.fullmatch(r"\d{4}", text) else "n.d."


def _bibtex_key(authors: list[str], year: str, title: str) -> str:
    first = authors[0] if authors else "anon"
    surname = first.split(",")[0].split()[-1] if "," in first else first.split()[-1]  # "Vaswani, A." and "A. Vaswani"
    first_word = (re.findall(r"[a-z0-9]+", fold_text(title)) or ["untitled"])[0]
    surname = "".join(re.findall(r"[a-z0-9]+", fold_text(surname))) or "anon"
    return f"{surname}{year if year != 'n.d.' else 'nd'}{first_word}"


def make_citation(
    title: str = "",
    authors: list[str] | str | None = None,
    year: int | str | None = None,
    url: str = "",
    style: str = "apa",
) -> dict[str, Any]:
    tool = "make_citation"
    if not isinstance(title, str) or not title.strip():
        return {"tool": tool, "error": "MissingTitle", "message": "title must be a non-empty string"}
    style = (style or "apa").strip().lower() if isinstance(style, str) else ""
    if style not in STYLES:
        return {"tool": tool, "error": "UnknownStyle", "message": f"style must be one of {list(STYLES)}"}
    names = _clean_authors(authors)
    if names is None:
        return {"tool": tool, "error": "InvalidAuthors", "message": "authors must be a list of strings or one string"}

    title = title.strip()
    url = url.strip() if isinstance(url, str) else ""
    year_text = _clean_year(year)

    if style == "apa":
        who = ", ".join(names) if names else "Unknown author"
        citation = f"{who} ({year_text}). {title.rstrip('.')}." + (f" {url}" if url else "")
    elif style == "ieee":
        who = ", ".join(names) if names else "Unknown author"
        citation = f'{who}, "{title}," {year_text}' + ("" if year_text.endswith(".") else ".")
        citation += f" [Online]. Available: {url}" if url else ""
    else:
        fields = [f"  title = {{{title}}}"]
        if names:
            fields.append(f"  author = {{{' and '.join(names)}}}")
        fields.append(f"  year = {{{year_text}}}")
        if url:
            fields.append(f"  url = {{{url}}}")
        citation = f"@misc{{{_bibtex_key(names, year_text, title)},\n" + ",\n".join(fields) + "\n}"

    return {"tool": tool, "style": style, "citation": citation, "has_url": bool(url)}
