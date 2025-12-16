"""Tests for iscc_compare.py tool."""

import sys

import pytest

sys.path.insert(0, "skills/iscc-toolkit/tools")

from iscc_compare import compare_iscc, format_pretty, main

# Test ISCCs generated from iscc-core
ISCC_TEXT_1 = "ISCC:EAASKDNZNYGUUF5A"  # gen_text_code_v0("Hello World")
ISCC_TEXT_2 = "ISCC:EAAQZ4BEQZMRALNE"  # gen_text_code_v0("Hello World Again")
ISCC_META_1 = "ISCC:AAASIOC2VIDHWPNS"  # gen_meta_code_v0("Test Title")


def test_compare_iscc_same_codes():
    # type: () -> None
    """Compare identical ISCC codes returns zero distance."""
    result = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_1)

    assert "error" not in result
    assert result["iscc_a"] == ISCC_TEXT_1
    assert result["iscc_b"] == ISCC_TEXT_1
    assert result["hamming_distance"] == 0
    assert result["similarity_percentage"] == 100.0
    assert result["units_a"] == result["units_b"]


def test_compare_iscc_different_codes():
    # type: () -> None
    """Compare different ISCC codes returns non-zero distance."""
    result = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_2)

    assert "error" not in result
    assert result["iscc_a"] == ISCC_TEXT_1
    assert result["iscc_b"] == ISCC_TEXT_2
    assert result["hamming_distance"] > 0
    assert 0 <= result["similarity_percentage"] <= 100
    assert "comparison" in result
    assert "units_a" in result
    assert "units_b" in result


def test_compare_iscc_invalid_code():
    # type: () -> None
    """Compare with invalid ISCC code returns error."""
    result = compare_iscc("INVALID", ISCC_TEXT_1)

    assert "error" in result
    assert result["iscc_a"] == "INVALID"
    assert result["iscc_b"] == ISCC_TEXT_1


def test_compare_iscc_pretty_param_unused():
    # type: () -> None
    """The pretty parameter doesn't affect the result dict."""
    result_plain = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_2, pretty=False)
    result_pretty = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_2, pretty=True)

    assert result_plain == result_pretty


def test_format_pretty_success():
    # type: () -> None
    """Format successful comparison result for human readability."""
    result = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_2)
    formatted = format_pretty(result)

    assert "ISCC Comparison Results" in formatted
    assert ISCC_TEXT_1 in formatted
    assert ISCC_TEXT_2 in formatted
    assert "Hamming Distance:" in formatted
    assert "Similarity:" in formatted
    assert "Units in A:" in formatted
    assert "Units in B:" in formatted
    assert "Matching Units:" in formatted


def test_format_pretty_error():
    # type: () -> None
    """Format error result returns error message."""
    result = {"error": "Test error message", "iscc_a": "A", "iscc_b": "B"}
    formatted = format_pretty(result)

    assert formatted == "ERROR: Test error message"


def test_main_json_output(capsys, monkeypatch):
    # type: (pytest.CaptureFixture, pytest.MonkeyPatch) -> None
    """Main function outputs JSON by default."""
    monkeypatch.setattr(sys, "argv", ["iscc_compare.py", ISCC_TEXT_1, ISCC_TEXT_2])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert '"iscc_a":' in captured.out
    assert '"iscc_b":' in captured.out
    assert '"hamming_distance":' in captured.out


def test_main_pretty_output(capsys, monkeypatch):
    # type: (pytest.CaptureFixture, pytest.MonkeyPatch) -> None
    """Main function outputs pretty format with --pretty flag."""
    monkeypatch.setattr(sys, "argv", ["iscc_compare.py", "--pretty", ISCC_TEXT_1, ISCC_TEXT_2])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "ISCC Comparison Results" in captured.out
    assert "Hamming Distance:" in captured.out


def test_main_error_exit_code(capsys, monkeypatch):
    # type: (pytest.CaptureFixture, pytest.MonkeyPatch) -> None
    """Main function exits with code 1 on error."""
    monkeypatch.setattr(sys, "argv", ["iscc_compare.py", "INVALID", "ALSO_INVALID"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert '"error":' in captured.out
