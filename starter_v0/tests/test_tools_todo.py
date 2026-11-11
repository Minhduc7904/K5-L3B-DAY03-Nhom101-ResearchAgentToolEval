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
    result = TOOL_FUNCTIONS["clarify"](question="Chọn một", response_type="choice", options=["A", "B"])
    assert result["options"] == ["A", "B"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "section": "A"},
        {"title": "b1", "section": "B"},
        {"title": "a2", "section": "A"},
    ]
    markdown = TOOL_FUNCTIONS["format"](items=items, template="sections")["markdown"]
    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    # a1 and a2 are grouped under the single "## A" heading, before "## B".
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": "one"}, {"title": "two"}, {"title": "three"}]
    parts = TOOL_FUNCTIONS["format"](items=items, template="thread")["markdown"].split(chr(10) * 2)
    assert [part.split(" ")[0] for part in parts] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty, template="sections")
        assert result["item_count"] == 0
        assert result["markdown"].strip() == ""


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Họp 9h", confirmed=True)

    assert result == {"tool": "send_telegram", "status": "sent"}
    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot123:abc/sendMessage" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100"
    assert calls[0]["json"]["text"] == "Họp 9h"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))
    result = TOOL_FUNCTIONS["send"](text="x", confirmed=True)
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "k")
    calls = fake_http(FakeResponse({"results": []}))
    TOOL_FUNCTIONS["lookup"](query="x", timeframe=None)
    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "k")
    fake_http(FakeResponse({"data": {
        "markdown": "# Hello",
        "metadata": {"title": "T", "sourceURL": "https://example.com/a"},
    }}))
    result = TOOL_FUNCTIONS["fetch"](url="https://www.example.com/a")
    assert result["items"][0] == {
        "title": "T", "url": "https://example.com/a", "source": "example.com", "summary": "# Hello",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "k")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))
    result = TOOL_FUNCTIONS["fetch"](url="https://example.com/a")
    assert len(result["items"][0]["summary"]) == 4000
    assert result["items"][0]["title"] == "https://example.com/a"  # falls back to the url


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    raw = [{"screen_name": "karpathy", "text": "no id"}]
    raw += [{"screen_name": "karpathy", "tweet_id": str(i), "text": f"tweet {i}"} for i in range(1, 7)]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="karpathy", limit=3)

    assert calls[0]["params"] == {"screenname": "karpathy"}
    assert [item["url"] for item in result["items"]] == [
        "https://x.com/karpathy/status/1",
        "https://x.com/karpathy/status/2",
        "https://x.com/karpathy/status/3",
    ]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "k")
    calls = fake_http(FakeResponse({"timeline": []}))
    TOOL_FUNCTIONS["social_search"](query="gpt-5", search_type="Top")
    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "gpt-5", "search_type": "Top"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    policy = TOOL_FUNCTIONS["policy"]
    assert policy(query="")["results"] == []
    assert policy(query="the of and")["results"] == []  # stopwords only


def test_policy_area_filter_only_returns_that_area() -> None:
    results = TOOL_FUNCTIONS["policy"](query="confidential customer data", policy_area="data_privacy")["results"]
    assert results
    assert {item["policy_area"] for item in results} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = TOOL_FUNCTIONS["policy"](query="injection probe", policy_area="source_citation")["results"]
    hit = next(item for item in results if item["section"] == "Injection probe")
    assert any("ignore the citation policy" in line for line in hit["untrusted_text"])
    assert "ignore the citation policy" not in hit["facts"]


# ---------------- regression: bug found by the tests above ----------------

@pytest.mark.parametrize("not_confirmed", ["false", "False", "no", "", 0, None])
def test_send_regression_only_boolean_true_counts_as_confirmation(monkeypatch, fake_http, not_confirmed) -> None:
    """Bug: `if not confirmed` treated the string "false" (truthy) as a confirmation, so a model that
    sent confirmed="false" would have posted to Telegram. Only the boolean True may send."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:abc")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=not_confirmed)

    assert result["status"] == "needs_confirmation"
    assert calls == []


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


# ---------------- cite (group tool) ----------------

cite_tool = TOOL_FUNCTIONS["cite"]


def test_cite_apa_with_authors_year_and_url() -> None:
    result = cite_tool(title="Attention Is All You Need", authors=["A. Vaswani", "N. Shazeer"], year=2017,
                       url="https://arxiv.org/abs/1706.03762")
    assert result["style"] == "apa"
    assert result["citation"] == (
        "A. Vaswani, N. Shazeer (2017). Attention Is All You Need. https://arxiv.org/abs/1706.03762"
    )


def test_cite_bibtex_builds_key_and_fields() -> None:
    result = cite_tool(title="Attention Is All You Need", authors="A. Vaswani and N. Shazeer", year="2017",
                       url="https://arxiv.org/abs/1706.03762", style="bibtex")
    citation = result["citation"]
    assert citation.startswith("@misc{vaswani2017attention,")
    assert "author = {A. Vaswani and N. Shazeer}" in citation
    assert "year = {2017}" in citation


def test_cite_does_not_invent_missing_metadata() -> None:
    result = cite_tool(title="Bài viết không rõ nguồn", year="gần đây", style="ieee")
    assert result["citation"] == 'Unknown author, "Bài viết không rõ nguồn," n.d.'
    assert result["has_url"] is False


@pytest.mark.parametrize("bad_title", ["", "   ", None, 42, ["x"]])
def test_cite_bad_title_returns_error_dict(bad_title) -> None:
    result = cite_tool(title=bad_title)
    assert result["error"] == "MissingTitle"
    assert "citation" not in result


def test_cite_unknown_style_and_bad_authors_return_error_dicts() -> None:
    assert cite_tool(title="T", style="mla")["error"] == "UnknownStyle"
    assert cite_tool(title="T", authors=[1, 2])["error"] == "InvalidAuthors"


# ---------------- dedupe (group tool) ----------------

dedupe_tool = TOOL_FUNCTIONS["dedupe"]


def test_dedupe_removes_same_url_after_normalizing_and_keeps_first() -> None:
    items = [
        {"title": "A", "url": "https://www.example.com/post/?utm_source=x"},
        {"title": "A again", "url": "https://example.com/post#top"},
        {"title": "B", "url": "https://example.com/other"},
    ]
    result = dedupe_tool(items=items)
    assert [item["title"] for item in result["items"]] == ["A", "B"]
    assert result["removed"] == 1
    assert result["kept"] == 2


def test_dedupe_by_title_ignores_case_accents_and_punctuation() -> None:
    items = [{"title": "OpenAI ra mắt GPT-5!", "url": "https://a.com/1"},
             {"title": "openai ra mat gpt 5", "url": "https://b.com/2"}]
    assert dedupe_tool(items=items, key="title")["removed"] == 1
    assert dedupe_tool(items=items, key="url")["removed"] == 0  # different URLs


def test_dedupe_keeps_items_with_nothing_to_compare() -> None:
    items = [{"summary": "no key"}, {"summary": "no key"}, {"title": "", "url": ""}]
    result = dedupe_tool(items=items)
    assert result["kept"] == 3
    assert result["removed"] == 0


def test_dedupe_empty_input_does_not_crash() -> None:
    for empty in (None, []):
        result = dedupe_tool(items=empty)
        assert result["items"] == []
        assert result["removed"] == 0


@pytest.mark.parametrize("bad_items", ["not a list", [1, 2], [{"url": "https://a.com"}, "x"], {"url": "x"}])
def test_dedupe_bad_items_return_error_dict(bad_items) -> None:
    assert dedupe_tool(items=bad_items)["error"] == "InvalidItems"


def test_dedupe_unknown_key_returns_error_dict() -> None:
    assert dedupe_tool(items=[], key="author")["error"] == "UnknownKey"


# ---------------- text_stats (group tool) ----------------

stats_tool = TOOL_FUNCTIONS["text_stats"]


def test_text_stats_counts_chars_words_and_reading_time() -> None:
    result = stats_tool(text="một hai ba bốn năm")
    assert result["chars"] == len("một hai ba bốn năm")
    assert result["words"] == 5
    assert result["reading_seconds"] == 2  # 5 words at 200 wpm = 1.5 s, rounded
    assert result["over_limit"] is False


def test_text_stats_flags_text_over_the_limit() -> None:
    result = stats_tool(text="x" * 281)
    assert result["over_limit"] is True
    assert result["remaining"] == -1
    assert stats_tool(text="x" * 280)["over_limit"] is False
    assert stats_tool(text="x" * 50, limit=40)["over_limit"] is True


@pytest.mark.parametrize("bad_text", ["", "   \n", None, 7, ["x"]])
def test_text_stats_bad_text_returns_error_dict(bad_text) -> None:
    assert stats_tool(text=bad_text)["error"] == "EmptyText"


@pytest.mark.parametrize("bad_limit", [0, -5, "280", 2.5, True, None])
def test_text_stats_bad_limit_returns_error_dict(bad_limit) -> None:
    assert stats_tool(text="hello", limit=bad_limit)["error"] == "InvalidLimit"


def test_text_stats_too_long_returns_error_dict() -> None:
    assert stats_tool(text="x" * 100_001)["error"] == "TooLong"


# ---------------- regressions found by independent review ----------------

def test_dedupe_regression_vietnamese_d_stroke_is_not_dropped() -> None:
    items = [{"title": "Đà Nẵng"}, {"title": "À Nẵng"}, {"title": "Điện thoại mới"}, {"title": "Iện thoại mới"}]
    assert dedupe_tool(items=items, key="title")["removed"] == 0
    assert dedupe_tool(items=[{"title": "Đà Nẵng"}, {"title": "đà nẵng!"}], key="title")["removed"] == 1


def test_dedupe_regression_titles_without_latin_letters_are_kept() -> None:
    items = [{"title": "日本語"}, {"title": "中文"}, {"title": "!!!"}, {"title": "???"}]
    assert dedupe_tool(items=items, key="title")["removed"] == 0


def test_dedupe_query_parameter_order_does_not_matter() -> None:
    items = [{"url": "https://a.com/x?a=1&b=2"}, {"url": "https://a.com/x?b=2&a=1"}]
    assert dedupe_tool(items=items)["removed"] == 1


def test_cite_regression_surname_first_author_gives_correct_bibtex_key() -> None:
    result = cite_tool(title="Attention Is All You Need", authors=["Vaswani, A."], year=2017, style="bibtex")
    assert result["citation"].startswith("@misc{vaswani2017attention,")


def test_cite_apa_title_ending_with_period_is_not_doubled() -> None:
    result = cite_tool(title="A title.", authors=["Ng, A."], year=2020)
    assert result["citation"] == "Ng, A. (2020). A title."
