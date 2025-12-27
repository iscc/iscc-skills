# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-core>=1.0.0"]
# ///
"""Normalize text using ISCC text processing pipeline.

This script applies ISCC text normalization and provides detailed statistics
about the transformation. Supports both normalization and whitespace collapsing,
with options to display n-grams and character statistics.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import iscc_core as ic
except ImportError:
    print(
        "Error: iscc-core is not installed. Install with: pip install iscc-core",
        file=sys.stderr,
    )
    sys.exit(1)


def normalize_text(text, collapse=False, show_ngrams=False, show_stats=False):
    # type: (str, bool, bool, bool) -> dict
    """
    Normalize text using ISCC text processing pipeline.

    :param text: Input text to normalize
    :param collapse: Apply whitespace collapsing
    :param show_ngrams: Show 13-character n-grams
    :param show_stats: Show detailed character/byte statistics
    :return: Dictionary containing normalization results
    """
    try:
        # Apply normalization
        if collapse:
            normalized = ic.text_collapse(text)
            operation = "text_collapse"
        else:
            normalized = ic.text_normalize(text)
            operation = "text_normalize"

        result = {
            "operation": operation,
            "original_text": text,
            "normalized_text": normalized,
            "original_length": len(text),
            "normalized_length": len(normalized),
            "length_reduction": len(text) - len(normalized),
            "reduction_percentage": round((len(text) - len(normalized)) / len(text) * 100, 2)
            if len(text) > 0
            else 0,
        }

        # Add statistics if requested
        if show_stats:
            original_bytes = text.encode("utf-8")
            normalized_bytes = normalized.encode("utf-8")

            stats = {
                "original": {
                    "characters": len(text),
                    "bytes": len(original_bytes),
                    "unique_chars": len(set(text)),
                    "whitespace_count": sum(1 for c in text if c.isspace()),
                    "alphanumeric_count": sum(1 for c in text if c.isalnum()),
                    "punctuation_count": sum(
                        1 for c in text if not c.isalnum() and not c.isspace()
                    ),
                },
                "normalized": {
                    "characters": len(normalized),
                    "bytes": len(normalized_bytes),
                    "unique_chars": len(set(normalized)),
                    "whitespace_count": sum(1 for c in normalized if c.isspace()),
                    "alphanumeric_count": sum(1 for c in normalized if c.isalnum()),
                    "punctuation_count": sum(
                        1 for c in normalized if not c.isalnum() and not c.isspace()
                    ),
                },
            }
            result["statistics"] = stats

        # Add n-grams if requested
        if show_ngrams:
            ngrams = []
            ngram_size = 13
            for i in range(len(normalized) - ngram_size + 1):
                ngram = normalized[i : i + ngram_size]
                ngrams.append(ngram)

            result["ngrams"] = {
                "size": ngram_size,
                "count": len(ngrams),
                "samples": ngrams[:10],  # Show first 10 n-grams as samples
            }

        return result

    except Exception as e:
        return {
            "error": str(e),
            "original_text": text[:100] + "..." if len(text) > 100 else text,
        }


def normalize_from_file(input_path, output_path, collapse, show_ngrams, show_stats):
    # type: (Path, Path, bool, bool, bool) -> dict
    """
    Normalize text from input file and optionally write to output file.

    :param input_path: Path to input text file
    :param output_path: Optional path to output file
    :param collapse: Apply whitespace collapsing
    :param show_ngrams: Show n-grams
    :param show_stats: Show statistics
    :return: Dictionary containing normalization results
    """
    try:
        # Read input file
        with open(input_path, encoding="utf-8") as f:
            text = f.read()

        # Normalize
        result = normalize_text(text, collapse, show_ngrams, show_stats)

        # Write output file if specified
        if output_path and "error" not in result:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["normalized_text"])
            result["output_file"] = str(output_path)

        result["input_file"] = str(input_path)

        return result

    except Exception as e:
        return {"error": str(e), "input_file": str(input_path)}


def format_pretty(result):
    # type: (dict) -> str
    """
    Format normalization results for human-readable output.

    :param result: Normalization result dictionary
    :return: Formatted string
    """
    if "error" in result:
        return f"ERROR: {result['error']}"

    lines = []
    lines.append("=" * 70)
    lines.append("ISCC Text Normalization")
    lines.append("=" * 70)

    if "input_file" in result:
        lines.append(f"Input File: {result['input_file']}")
        if "output_file" in result:
            lines.append(f"Output File: {result['output_file']}")
        lines.append("-" * 70)

    lines.append(f"Operation: {result['operation']}")
    lines.append("-" * 70)

    # Show text samples
    lines.append("Original Text (first 200 chars):")
    sample = result["original_text"][:200]
    lines.append(f"  {repr(sample)}")
    if len(result["original_text"]) > 200:
        lines.append("  ...")

    lines.append("\nNormalized Text (first 200 chars):")
    sample = result["normalized_text"][:200]
    lines.append(f"  {repr(sample)}")
    if len(result["normalized_text"]) > 200:
        lines.append("  ...")

    lines.append("-" * 70)

    # Show length information
    lines.append(f"Original Length: {result['original_length']} characters")
    lines.append(f"Normalized Length: {result['normalized_length']} characters")
    reduction = result["length_reduction"]
    pct = result["reduction_percentage"]
    lines.append(f"Length Reduction: {reduction} characters ({pct}%)")

    # Show statistics if available
    if "statistics" in result:
        lines.append("-" * 70)
        lines.append("Detailed Statistics:")
        lines.append("\n  Original:")
        for key, value in result["statistics"]["original"].items():
            lines.append(f"    {key}: {value}")
        lines.append("\n  Normalized:")
        for key, value in result["statistics"]["normalized"].items():
            lines.append(f"    {key}: {value}")

    # Show n-grams if available
    if "ngrams" in result:
        lines.append("-" * 70)
        lines.append(f"N-grams ({result['ngrams']['size']}-character):")
        lines.append(f"  Total Count: {result['ngrams']['count']}")
        lines.append("  Sample N-grams (first 10):")
        for i, ngram in enumerate(result["ngrams"]["samples"], 1):
            lines.append(f"    {i}. {repr(ngram)}")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    # type: () -> None
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Normalize text using ISCC text processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Sample text to normalize"
  %(prog)s --collapse "Text   with    extra spaces"
  %(prog)s --stats --ngrams "Sample text"
  %(prog)s --input text.txt --output normalized.txt
  %(prog)s --pretty --stats --input text.txt

The normalization pipeline applies:
  - Unicode NFKC normalization
  - Case folding (lowercase)
  - Whitespace normalization
  - Character filtering (keeps alphanumeric + basic punctuation)

The collapse operation additionally:
  - Collapses multiple whitespace to single space
  - Strips leading/trailing whitespace
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "text", nargs="?", help="Text to normalize (use quotes for text with spaces)"
    )

    input_group.add_argument("--input", type=Path, metavar="FILE", help="Read text from file")

    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="Write normalized text to file (requires --input)",
    )

    parser.add_argument(
        "--collapse",
        action="store_true",
        help="Use text_collapse instead of text_normalize (includes whitespace collapsing)",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output human-readable format instead of JSON",
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show detailed character and byte statistics",
    )

    parser.add_argument(
        "--ngrams",
        action="store_true",
        help="Show 13-character n-grams from normalized text",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.output and not args.input:
        print("Error: --output requires --input", file=sys.stderr)
        sys.exit(1)

    # Perform normalization
    if args.input:
        if not args.input.exists():
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        result = normalize_from_file(
            args.input, args.output, args.collapse, args.ngrams, args.stats
        )
    else:
        result = normalize_text(args.text, args.collapse, args.ngrams, args.stats)

    # Output results
    if args.pretty:
        print(format_pretty(result))
    else:
        print(json.dumps(result, indent=2))

    # Exit with error code if normalization failed
    if "error" in result:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
