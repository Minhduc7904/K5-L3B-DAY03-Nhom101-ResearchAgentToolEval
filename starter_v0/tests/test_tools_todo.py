"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

# ---------------- artifact (group tool) ----------------

artifact_tool = TOOL_FUNCTIONS["artifact"]


def test_artifact_wraps_body_in_document_with_csp() -> None:
    result = artifact_tool(title="So sánh model", html="<table><tr><td>GPT</td></tr></table>")
    page = result["artifact"]["html"]

    assert result["status"] == "rendered"
    assert result["artifact"]["title"] == "So sánh model"
    assert page.startswith("<!doctype html>")
    assert "<title>So sánh model</title>" in page
    assert "<table><tr><td>GPT</td></tr></table>" in page
    assert "connect-src 'none'" in page  # page cannot send data anywhere
    # CSP must come before the content, or it does not apply to it.
    assert page.index("Content-Security-Policy") < page.index("<table>")


def test_artifact_full_document_gets_csp_inside_its_own_head() -> None:
    doc = "<!DOCTYPE html><html><head><style>b{}</style></head><body><b>x</b></body></html>"
    page = artifact_tool(title="T", html=doc)["artifact"]["html"]

    assert page.count("<html") == 1  # not wrapped a second time
    assert page.index("<head>") < page.index("Content-Security-Policy") < page.index("<style>")


def test_artifact_header_tag_is_not_mistaken_for_head() -> None:
    # A <header> in a body fragment must not receive the CSP: in <body> the browser ignores it.
    page = artifact_tool(title="T", html="<header>Top</header><p>x</p>")["artifact"]["html"]
    assert page.startswith("<!doctype html>")
    assert page.index("Content-Security-Policy") < page.index("<header>")


def test_artifact_id_is_stable_for_same_content() -> None:
    a = artifact_tool(title="T", html="<p>x</p>")["artifact"]["id"]
    b = artifact_tool(title="T", html="<p>x</p>")["artifact"]["id"]
    c = artifact_tool(title="T", html="<p>y</p>")["artifact"]["id"]
    assert a == b != c


def test_artifact_title_is_escaped_and_defaults_when_missing() -> None:
    page = artifact_tool(title="</title><script>alert(1)</script>", html="<p>x</p>")["artifact"]["html"]
    assert "<title>&lt;/title&gt;&lt;script&gt;" in page
    assert artifact_tool(title="  ", html="<p>x</p>")["artifact"]["title"] == "Artifact"
    assert artifact_tool(title=None, html="<p>x</p>")["artifact"]["title"] == "Artifact"


@pytest.mark.parametrize("bad_html", ["", "   ", None, 123, ["<p>x</p>"]])
def test_artifact_bad_html_from_model_returns_error_dict(bad_html) -> None:
    result = artifact_tool(title="T", html=bad_html)
    assert result["error"] == "EmptyHtml"
    assert "artifact" not in result


def test_artifact_too_large_returns_error_dict() -> None:
    result = artifact_tool(title="T", html="x" * 200_001)
    assert result["error"] == "TooLarge"
    assert "artifact" not in result
