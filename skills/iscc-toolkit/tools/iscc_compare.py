# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-core>=1.0.0"]
# ///
"""Compare ISCCs and calculate similarity metrics.

This script compares two ISCC codes and provides detailed similarity analysis
including Hamming distance, unit-by-unit comparison, and similarity percentage.
"""

import argparse
import json
import sys

try:
    import iscc_core as ic
except ImportError:  # pragma: no cover
    print(
        "Error: iscc-core is not installed. Run this script with: uvx iscc_compare.py",
        file=sys.stderr,
    )
    sys.exit(1)


def compare_iscc(iscc_a, iscc_b, pretty=False):
    # type: (str, str, bool) -> dict
    """
    Compare two ISCC codes and return detailed similarity metrics.

    :param iscc_a: First ISCC code
    :param iscc_b: Second ISCC code
    :param pretty: Whether to format output for human readability
    :return: Dictionary containing comparison results
    """
    try:
        # Perform comparison using iscc-core
        comparison = ic.iscc_compare(iscc_a, iscc_b)

        # Calculate overall Hamming distance
        distance = ic.iscc_distance(iscc_a, iscc_b)

        # Decompose both ISCCs to show unit structure
        units_a = ic.iscc_decompose(iscc_a)
        units_b = ic.iscc_decompose(iscc_b)

        # Calculate similarity percentage (0-100)
        # Total bits compared
        total_bits = min(len(iscc_a), len(iscc_b)) * 5  # Each base32 char = 5 bits
        matching_bits = total_bits - distance
        similarity_pct = (matching_bits / total_bits * 100) if total_bits > 0 else 0

        result = {
            "iscc_a": iscc_a,
            "iscc_b": iscc_b,
            "hamming_distance": distance,
            "similarity_percentage": round(similarity_pct, 2),
            "units_a": units_a,
            "units_b": units_b,
            "matching_units": comparison.get("matching_units", []),
            "comparison": comparison,
        }

        return result

    except Exception as e:
        return {"error": str(e), "iscc_a": iscc_a, "iscc_b": iscc_b}


def format_pretty(result):
    # type: (dict) -> str
    """
    Format comparison results for human-readable output.

    :param result: Comparison result dictionary
    :return: Formatted string
    """
    if "error" in result:
        return f"ERROR: {result['error']}"

    lines = []
    lines.append("=" * 60)
    lines.append("ISCC Comparison Results")
    lines.append("=" * 60)
    lines.append(f"ISCC A: {result['iscc_a']}")
    lines.append(f"ISCC B: {result['iscc_b']}")
    lines.append("-" * 60)
    lines.append(f"Hamming Distance: {result['hamming_distance']}")
    lines.append(f"Similarity: {result['similarity_percentage']}%")
    lines.append("-" * 60)
    lines.append(f"Units in A: {len(result['units_a'])}")
    for i, unit in enumerate(result["units_a"], 1):
        lines.append(f"  {i}. {unit}")
    lines.append(f"Units in B: {len(result['units_b'])}")
    for i, unit in enumerate(result["units_b"], 1):
        lines.append(f"  {i}. {unit}")
    lines.append("-" * 60)
    lines.append(f"Matching Units: {result['matching_units']}")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    # type: () -> None
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Compare two ISCC codes and calculate similarity metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ISCC:AAAA... ISCC:BBBB...
  %(prog)s --pretty ISCC:AAAA... ISCC:BBBB...
        """,
    )

    parser.add_argument("iscc_a", help="First ISCC code to compare")

    parser.add_argument("iscc_b", help="Second ISCC code to compare")

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output human-readable format instead of JSON",
    )

    args = parser.parse_args()

    # Perform comparison
    result = compare_iscc(args.iscc_a, args.iscc_b, args.pretty)

    # Output results
    if args.pretty:
        print(format_pretty(result))
    else:
        print(json.dumps(result, indent=2))

    # Exit with error code if comparison failed
    if "error" in result:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
