"""Tests for text processing utilities."""

from chatgpt_search.utils import (
    clean_text,
    extract_text_from_parts,
    parse_date_filter,
    separate_code,
    strip_citeturn,
    strip_pua,
    truncate,
)


def test_strip_pua_removes_citation_markers():
    text = "Hello\ue000 World\uf8ff End"
    assert strip_pua(text) == "Hello World End"


def test_strip_pua_preserves_normal_text():
    text = "Hello World"
    assert strip_pua(text) == "Hello World"


def test_separate_code_extracts_fenced_blocks():
    text = "Some text\n```python\nprint('hello')\n```\nMore text"
    prose, code = separate_code(text)
    assert "print('hello')" not in prose
    assert "print('hello')" in code
    assert "Some text" in prose
    assert "More text" in prose


def test_separate_code_handles_no_code():
    text = "Just regular text without code"
    prose, code = separate_code(text)
    assert prose == text
    assert code == ""


def test_separate_code_multiple_blocks():
    text = "Text\n```\nblock1\n```\nMiddle\n```\nblock2\n```\nEnd"
    prose, code = separate_code(text)
    assert "block1" in code
    assert "block2" in code
    assert "Middle" in prose


def test_extract_text_from_parts_strings():
    parts = ["Hello", "World"]
    assert extract_text_from_parts(parts) == "Hello\nWorld"


def test_extract_text_from_parts_skips_dicts():
    parts = ["Hello", {"asset_pointer": "file://image.png", "width": 100}]
    assert extract_text_from_parts(parts) == "Hello"


def test_extract_text_from_parts_empty():
    assert extract_text_from_parts([]) == ""


def test_strip_citeturn_removes_citation_markup():
    text = "Hello citeturn0search1 world citeturn2view0 end"
    assert strip_citeturn(text) == "Hello  world  end"


def test_strip_citeturn_preserves_normal_text():
    text = "No citation markup here"
    assert strip_citeturn(text) == "No citation markup here"


def test_strip_citeturn_handles_various_patterns():
    assert strip_citeturn("citeturn0search1") == ""
    assert strip_citeturn("citeturn2view0") == ""
    assert strip_citeturn("citeturn12search34") == ""
    assert strip_citeturn("prefix citeturn0search1 suffix") == "prefix  suffix"


def test_clean_text_strips_citeturn():
    text = "Hello citeturn0search1 world"
    result = clean_text(text)
    assert "citeturn" not in result
    assert "Hello" in result
    assert "world" in result


def test_clean_text_strips_pua_and_normalizes():
    text = "Hello\ue000\n\n\n\n\nWorld"
    result = clean_text(text)
    assert "\ue000" not in result
    assert "\n\n\n" not in result


def test_parse_date_filter_full_date():
    ts = parse_date_filter("2025-06-15")
    assert ts > 0


def test_parse_date_filter_month():
    ts = parse_date_filter("2025-06")
    assert ts > 0


def test_parse_date_filter_year():
    ts = parse_date_filter("2025")
    assert ts > 0


def test_parse_date_filter_invalid():
    try:
        parse_date_filter("not-a-date")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_truncate_short():
    assert truncate("short", 200) == "short"


def test_truncate_long():
    long_text = "x" * 300
    result = truncate(long_text, 200)
    assert len(result) == 200
    assert result.endswith("...")
