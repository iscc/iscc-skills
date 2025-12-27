"""Tests for iscc_compare.py tool."""

import sys

import pytest

sys.path.insert(0, "iscc-toolkit/skills/iscc-toolkit/tools")

from iscc_compare import compare_iscc, format_pretty, main

# Test ISCCs - Content-Code (text)
ISCC_TEXT_1 = "ISCC:EAASKDNZNYGUUF5A"  # gen_text_code_v0("Hello World")
ISCC_TEXT_2 = "ISCC:EAAQZ4BEQZMRALNE"  # gen_text_code_v0("Hello World Again")

# Test ISCCs - Meta-Code
ISCC_META_1 = "ISCC:AAASIOC2VIDHWPNS"  # gen_meta_code_v0("Test Title")
ISCC_META_2 = "ISCC:AAASRL3IUZLMXLGM"  # gen_meta_code_v0("Different Title")

# Test ISCCs - Data-Code
ISCC_DATA_1 = "ISCC:GAAW2PNBPYA6SWHM"  # gen_data_code_v0(b"test data")
ISCC_DATA_2 = "ISCC:GABRJFBIAWJX3FBK"  # gen_data_code_v0(b"different data")

# Test ISCCs - Instance-Code
ISCC_INST_1 = "ISCC:IAA26E2JX66FZKI4"  # gen_instance_code_v0(b"test")
ISCC_INST_2 = "ISCC:IAAS2OLB4R2TXJSJ"  # gen_instance_code_v0(b"other")


def test_compare_identical_codes():
    # type: () -> None
    """Compare identical ISCC codes returns score=1.0 and distance=0."""
    result = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_1)

    assert "error" not in result
    assert result["iscc_a"] == ISCC_TEXT_1
    assert result["iscc_b"] == ISCC_TEXT_1
    assert result["score"] == 1.0
    assert "content" in result["types"]
    assert result["types"]["content"]["score"] == 1.0
    assert result["types"]["content"]["distance"] == 0


def test_compare_different_codes():
    # type: () -> None
    """Compare different ISCC codes returns score<1.0 and distance>0."""
    result = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_2)

    assert "error" not in result
    assert result["iscc_a"] == ISCC_TEXT_1
    assert result["iscc_b"] == ISCC_TEXT_2
    assert 0 < result["score"] < 1.0
    assert "content" in result["types"]
    assert result["types"]["content"]["score"] < 1.0
    assert result["types"]["content"]["distance"] > 0
    assert result["types"]["content"]["bits"] > 0


def test_compare_meta_codes():
    # type: () -> None
    """Compare Meta-Code units."""
    result = compare_iscc(ISCC_META_1, ISCC_META_2)

    assert "error" not in result
    assert "meta" in result["types"]
    assert "score" in result["types"]["meta"]
    assert "distance" in result["types"]["meta"]
    assert "bits" in result["types"]["meta"]


def test_compare_data_codes():
    # type: () -> None
    """Compare Data-Code units."""
    result = compare_iscc(ISCC_DATA_1, ISCC_DATA_2)

    assert "error" not in result
    assert "data" in result["types"]
    assert "score" in result["types"]["data"]


def test_compare_instance_match():
    # type: () -> None
    """Instance codes with same hash return match=true."""
    result = compare_iscc(ISCC_INST_1, ISCC_INST_1)

    assert "error" not in result
    assert "instance" in result["types"]
    assert result["types"]["instance"]["match"] is True
    assert result["score"] == 1.0


def test_compare_instance_no_match():
    # type: () -> None
    """Instance codes with different hash return match=false."""
    result = compare_iscc(ISCC_INST_1, ISCC_INST_2)

    assert "error" not in result
    assert "instance" in result["types"]
    assert result["types"]["instance"]["match"] is False
    assert result["score"] == 0.0


def test_compare_no_compatible_units():
    # type: () -> None
    """Comparing incompatible units returns empty types and null score."""
    result = compare_iscc(ISCC_META_1, ISCC_TEXT_1)

    assert "error" not in result
    assert result["types"] == {}
    assert result["score"] is None


def test_compare_invalid_iscc():
    # type: () -> None
    """Compare with invalid ISCC code returns error."""
    result = compare_iscc("INVALID", ISCC_TEXT_1)

    assert "error" in result
    assert result["iscc_a"] == "INVALID"
    assert result["iscc_b"] == ISCC_TEXT_1


def test_format_pretty_success():
    # type: () -> None
    """Format successful comparison result for human readability."""
    result = compare_iscc(ISCC_TEXT_1, ISCC_TEXT_2)
    formatted = format_pretty(result)

    assert "ISCC Comparison" in formatted
    assert ISCC_TEXT_1 in formatted
    assert ISCC_TEXT_2 in formatted
    assert "content" in formatted
    assert "OVERALL" in formatted


def test_format_pretty_with_match():
    # type: () -> None
    """Format instance match result correctly."""
    result = compare_iscc(ISCC_INST_1, ISCC_INST_1)
    formatted = format_pretty(result)

    assert "instance" in formatted
    assert "match" in formatted


def test_format_pretty_no_match():
    # type: () -> None
    """Format instance no-match result correctly."""
    result = compare_iscc(ISCC_INST_1, ISCC_INST_2)
    formatted = format_pretty(result)

    assert "instance" in formatted
    assert "no match" in formatted


def test_format_pretty_no_compatible_units():
    # type: () -> None
    """Format result with no compatible units."""
    result = compare_iscc(ISCC_META_1, ISCC_TEXT_1)
    formatted = format_pretty(result)

    assert "No compatible units to compare" in formatted
    assert "n/a" in formatted


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
    assert '"score":' in captured.out
    assert '"types":' in captured.out


def test_main_pretty_output(capsys, monkeypatch):
    # type: (pytest.CaptureFixture, pytest.MonkeyPatch) -> None
    """Main function outputs pretty format with --pretty flag."""
    monkeypatch.setattr(sys, "argv", ["iscc_compare.py", "--pretty", ISCC_TEXT_1, ISCC_TEXT_2])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "ISCC Comparison" in captured.out
    assert "OVERALL" in captured.out


def test_main_error_exit_code(capsys, monkeypatch):
    # type: (pytest.CaptureFixture, pytest.MonkeyPatch) -> None
    """Main function exits with code 1 on error."""
    monkeypatch.setattr(sys, "argv", ["iscc_compare.py", "INVALID", "ALSO_INVALID"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert '"error":' in captured.out
