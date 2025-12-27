#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Text Extraction Tool

Extract plaintext from media files (EPUB, PDF, DOCX, etc.) with optional
ISCC-specific normalization. Outputs text for further processing or storage.
"""

import argparse
import json
import sys
from pathlib import Path

import iscc_sdk as idk


def extract_text(file_path, normalize, collapse):
    # type: (Path, bool, bool) -> tuple[str, dict]
    """
    Extract and optionally normalize text from a media file.

    Args:
        file_path: Path to media file
        normalize: Apply iscc_core.text_clean (same as iscc-sdk before gen_text_code)
        collapse: Apply iscc_core.text_collapse (aggressive: lowercase, no whitespace/punctuation)

    Returns:
        Tuple of (extracted_text, stats_dict)
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # Extract plaintext from media file
    text = idk.text_extract(str(file_path))
    original_length = len(text)

    # Apply normalization
    normalization = "none"

    if normalize:
        # Same normalization as iscc-sdk applies before ic.gen_text_code_v0()
        import iscc_core as ic

        text = ic.text_clean(text)
        normalization = "text_clean"

    if collapse:
        # Aggressive normalization used internally by ic.gen_text_code_v0()
        import iscc_core as ic

        text = ic.text_collapse(text)
        normalization = "text_collapse"

    stats = {
        "file": str(file_path.resolve()),
        "original_chars": original_length,
        "output_chars": len(text),
        "normalization": normalization,
    }

    return text, stats


def format_output(text, stats, pretty, text_only):
    # type: (str, dict, bool, bool) -> str
    """
    Format output as JSON or plain text.

    Args:
        text: Extracted text
        stats: Statistics dictionary
        pretty: Use human-readable JSON formatting
        text_only: Output only the text without JSON wrapper

    Returns:
        Formatted string
    """
    if text_only:
        return text

    data = {**stats, "text": text}
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def main():
    # type: () -> int
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract plaintext from media files with optional ISCC normalization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Normalization Modes:
  --normalize   Apply ic.text_clean() - same as iscc-sdk before gen_text_code()
  --collapse    Apply ic.text_collapse() - aggressive (lowercase, no whitespace)

Examples:
  %(prog)s document.epub
  %(prog)s --normalize book.pdf
  %(prog)s --normalize --output normalized.txt document.docx
  %(prog)s --collapse --text-only novel.epub > collapsed.txt
  %(prog)s --pretty ebook.epub
        """,
    )

    parser.add_argument("file", type=Path, help="Media file to extract text from")

    parser.add_argument(
        "--normalize",
        "-n",
        action="store_true",
        help="Apply ic.text_clean() (same normalization as iscc-sdk before gen_text_code)",
    )

    parser.add_argument(
        "--collapse",
        action="store_true",
        help="Apply ic.text_collapse() (aggressive: lowercase, no whitespace/punctuation)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        metavar="FILE",
        help="Write extracted text to file (text only, no JSON)",
    )

    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Output only the text without JSON wrapper",
    )

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        text, stats = extract_text(args.file, args.normalize, args.collapse)

        # Write to file if output specified
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
            stats["output_file"] = str(args.output.resolve())
            # Print stats only when writing to file
            if args.pretty:
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(stats, separators=(",", ":"), ensure_ascii=False))
        else:
            # Print to stdout
            print(format_output(text, stats, args.pretty, args.text_only))

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
