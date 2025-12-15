# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-core>=1.0.0"]
# ///
"""Calculate Hamming distance between ISCC codes.

This script calculates Hamming distance between ISCC codes and provides
similarity assessment. Supports both single comparisons and batch mode for
comparing one ISCC against multiple candidates.
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


def calculate_distance(iscc_a, iscc_b, threshold=None):
    # type: (str, str, int) -> dict
    """
    Calculate Hamming distance between two ISCC codes.

    :param iscc_a: First ISCC code
    :param iscc_b: Second ISCC code
    :param threshold: Optional similarity threshold (0-100)
    :return: Dictionary containing distance metrics
    """
    try:
        # Calculate Hamming distance
        distance = ic.hamming_distance(iscc_a, iscc_b)

        # Calculate similarity percentage
        # Each base32 character represents 5 bits
        total_bits = min(len(iscc_a), len(iscc_b)) * 5
        matching_bits = total_bits - distance
        similarity_pct = (matching_bits / total_bits * 100) if total_bits > 0 else 0

        # Assess match quality
        match_assessment = "no match"
        if similarity_pct >= 90:
            match_assessment = "strong match"
        elif similarity_pct >= 75:
            match_assessment = "good match"
        elif similarity_pct >= 50:
            match_assessment = "weak match"

        # Check against threshold if provided
        meets_threshold = None
        if threshold is not None:
            meets_threshold = similarity_pct >= threshold

        result = {
            "iscc_a": iscc_a,
            "iscc_b": iscc_b,
            "hamming_distance": distance,
            "total_bits": total_bits,
            "matching_bits": matching_bits,
            "similarity_percentage": round(similarity_pct, 2),
            "match_assessment": match_assessment,
        }

        if meets_threshold is not None:
            result["meets_threshold"] = meets_threshold
            result["threshold"] = threshold

        return result

    except Exception as e:
        return {"error": str(e), "iscc_a": iscc_a, "iscc_b": iscc_b}


def batch_compare(reference_iscc, candidate_file, threshold=None):
    # type: (str, Path, int) -> dict
    """
    Compare reference ISCC against multiple candidates from a file.

    :param reference_iscc: Reference ISCC code
    :param candidate_file: Path to file containing candidate ISCCs (one per line)
    :param threshold: Optional similarity threshold
    :return: Dictionary containing batch comparison results
    """
    try:
        # Read candidate ISCCs from file
        with open(candidate_file, encoding="utf-8") as f:
            candidates = [line.strip() for line in f if line.strip()]

        # Compare against each candidate
        comparisons = []
        for candidate in candidates:
            result = calculate_distance(reference_iscc, candidate, threshold)
            comparisons.append(result)

        # Sort by similarity (descending)
        comparisons.sort(key=lambda x: x.get("similarity_percentage", 0), reverse=True)

        # Find best matches
        best_match = comparisons[0] if comparisons else None
        matches_above_threshold = []
        if threshold is not None:
            matches_above_threshold = [c for c in comparisons if c.get("meets_threshold", False)]

        result = {
            "reference_iscc": reference_iscc,
            "total_candidates": len(candidates),
            "comparisons": comparisons,
            "best_match": best_match,
        }

        if threshold is not None:
            result["threshold"] = threshold
            result["matches_above_threshold"] = len(matches_above_threshold)

        return result

    except Exception as e:
        return {
            "error": str(e),
            "reference_iscc": reference_iscc,
            "candidate_file": str(candidate_file),
        }


def format_pretty(result, is_batch=False):
    # type: (dict, bool) -> str
    """
    Format distance calculation results for human-readable output.

    :param result: Distance calculation result dictionary
    :param is_batch: Whether this is a batch comparison result
    :return: Formatted string
    """
    if "error" in result:
        return f"ERROR: {result['error']}"

    lines = []
    lines.append("=" * 70)

    if is_batch:
        lines.append("ISCC Batch Distance Comparison")
        lines.append("=" * 70)
        lines.append(f"Reference ISCC: {result['reference_iscc']}")
        lines.append(f"Total Candidates: {result['total_candidates']}")
        if "threshold" in result:
            lines.append(f"Threshold: {result['threshold']}%")
            lines.append(f"Matches Above Threshold: {result['matches_above_threshold']}")
        lines.append("-" * 70)

        if result.get("best_match"):
            best = result["best_match"]
            lines.append("Best Match:")
            lines.append(f"  ISCC: {best['iscc_b']}")
            lines.append(f"  Distance: {best['hamming_distance']}")
            lines.append(f"  Similarity: {best['similarity_percentage']}%")
            lines.append(f"  Assessment: {best['match_assessment']}")
            lines.append("-" * 70)

        lines.append("\nAll Comparisons (sorted by similarity):")
        for i, comp in enumerate(result["comparisons"], 1):
            if "error" in comp:
                lines.append(f"\n{i}. ERROR: {comp['error']}")
                continue

            status = ""
            if "meets_threshold" in comp:
                status = " ✓" if comp["meets_threshold"] else " ✗"

            lines.append(f"\n{i}. {comp['iscc_b']}{status}")
            dist = comp["hamming_distance"]
            sim = comp["similarity_percentage"]
            match = comp["match_assessment"]
            lines.append(f"   Distance: {dist} | Similarity: {sim}% | {match}")

    else:
        lines.append("ISCC Hamming Distance Calculation")
        lines.append("=" * 70)
        lines.append(f"ISCC A: {result['iscc_a']}")
        lines.append(f"ISCC B: {result['iscc_b']}")
        lines.append("-" * 70)
        lines.append(f"Hamming Distance: {result['hamming_distance']}")
        lines.append(f"Total Bits: {result['total_bits']}")
        lines.append(f"Matching Bits: {result['matching_bits']}")
        lines.append(f"Similarity: {result['similarity_percentage']}%")
        lines.append(f"Assessment: {result['match_assessment']}")

        if "meets_threshold" in result:
            status = "YES ✓" if result["meets_threshold"] else "NO ✗"
            lines.append(f"Meets Threshold ({result['threshold']}%): {status}")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    # type: () -> None
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Calculate Hamming distance between ISCC codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ISCC:AAAA... ISCC:BBBB...
  %(prog)s --threshold 80 ISCC:AAAA... ISCC:BBBB...
  %(prog)s --batch candidates.txt ISCC:AAAA...
  %(prog)s --pretty --threshold 75 --batch candidates.txt ISCC:AAAA...

Batch file format (one ISCC per line):
  ISCC:KACYPXW445FTYNJ4HHKGUM
  ISCC:MEACY4HJF2WM5BDEXSFZQXM
  ISCC:GAAWQ35T3DQVFX3L3MJFG3Y
        """,
    )

    parser.add_argument("iscc_a", help="Reference ISCC code (or first ISCC for single comparison)")

    parser.add_argument("iscc_b", nargs="?", help="Second ISCC code (not used in batch mode)")

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output human-readable format instead of JSON",
    )

    parser.add_argument(
        "--threshold",
        type=int,
        metavar="PCT",
        help="Similarity threshold percentage (0-100)",
    )

    parser.add_argument(
        "--batch",
        type=Path,
        metavar="FILE",
        help="Batch mode: compare against ISCCs from file (one per line)",
    )

    args = parser.parse_args()

    # Validate threshold
    if args.threshold is not None:
        if not 0 <= args.threshold <= 100:
            print("Error: Threshold must be between 0 and 100", file=sys.stderr)
            sys.exit(1)

    # Perform calculation
    if args.batch:
        # Batch mode
        if not args.batch.exists():
            print(f"Error: File not found: {args.batch}", file=sys.stderr)
            sys.exit(1)

        result = batch_compare(args.iscc_a, args.batch, args.threshold)
        is_batch = True
    else:
        # Single comparison mode
        if not args.iscc_b:
            print(
                "Error: Second ISCC required for single comparison (or use --batch)",
                file=sys.stderr,
            )
            sys.exit(1)

        result = calculate_distance(args.iscc_a, args.iscc_b, args.threshold)
        is_batch = False

    # Output results
    if args.pretty:
        print(format_pretty(result, is_batch))
    else:
        print(json.dumps(result, indent=2))

    # Exit with error code if calculation failed
    if "error" in result:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
