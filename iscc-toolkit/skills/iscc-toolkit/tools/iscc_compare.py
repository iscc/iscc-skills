# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-core>=1.0.0"]
# ///
"""Compare ISCCs and calculate similarity metrics.

This script compares two ISCC codes and provides detailed similarity analysis
with per-unit-type breakdown. Output schema is aligned with search.iscc.id API.
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


# Maintype names for output
MAINTYPE_NAMES = {
    ic.MT.META: "meta",
    ic.MT.SEMANTIC: "semantic",
    ic.MT.CONTENT: "content",
    ic.MT.DATA: "data",
    ic.MT.INSTANCE: "instance",
    ic.MT.ID: "id",
}


def compare_iscc(iscc_a, iscc_b):
    # type: (str, str) -> dict
    """
    Compare two ISCCs and return similarity metrics per unit type.

    :param iscc_a: First ISCC code
    :param iscc_b: Second ISCC code
    :return: Dictionary with score, types breakdown, and input codes
    """
    try:
        # Decompose both ISCCs into Code objects
        units_a = [ic.Code(u) for u in ic.iscc_decompose(iscc_a)]
        units_b = [ic.Code(u) for u in ic.iscc_decompose(iscc_b)]

        types = {}
        scores = []

        # Find compatible unit pairs (same maintype, subtype, version)
        for ca in units_a:
            for cb in units_b:
                cat = (ca.maintype, ca.subtype, ca.version)
                cbt = (cb.maintype, cb.subtype, cb.version)
                if cat != cbt:
                    continue

                type_name = MAINTYPE_NAMES.get(ca.maintype, ca.maintype.name.lower())

                # Instance and ID types use exact match
                if ca.maintype in (ic.MT.INSTANCE, ic.MT.ID):
                    match = ca.hash_bytes == cb.hash_bytes
                    types[type_name] = {"match": match}
                    scores.append(1.0 if match else 0.0)
                else:
                    # Use NPH for normalized comparison of potentially different lengths
                    nph = ic.iscc_nph_similarity(ca.hash_bytes, cb.hash_bytes)
                    score = nph["similarity"]
                    bits = nph["common_prefix_bits"]
                    # Calculate distance from similarity and bits
                    distance = round((1.0 - score) * bits)
                    types[type_name] = {
                        "score": round(score, 4),
                        "distance": distance,
                        "bits": bits,
                    }
                    scores.append(score)

        # Calculate overall score (average of type scores)
        overall_score = round(sum(scores) / len(scores), 4) if scores else None

        return {
            "iscc_a": iscc_a,
            "iscc_b": iscc_b,
            "score": overall_score,
            "types": types,
        }

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
    lines.append("ISCC Comparison")
    lines.append("-" * 50)
    lines.append(f"A: {result['iscc_a']}")
    lines.append(f"B: {result['iscc_b']}")
    lines.append("-" * 50)

    types = result.get("types", {})
    if types:
        lines.append(f"{'TYPE':<12} {'SCORE':>8} {'DISTANCE':>10} {'BITS':>6}")
        for type_name, data in types.items():
            if "match" in data:
                match_str = "match" if data["match"] else "no match"
                lines.append(f"{type_name:<12} {match_str:>8}")
            else:
                score_str = f"{data['score']:.2f}"
                lines.append(
                    f"{type_name:<12} {score_str:>8} {data['distance']:>10} {data['bits']:>6}"
                )
    else:
        lines.append("No compatible units to compare")

    lines.append("-" * 50)
    score = result.get("score")
    if score is not None:
        lines.append(f"{'OVERALL':<12} {score:.2f}")
    else:
        lines.append("OVERALL      n/a")

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
    result = compare_iscc(args.iscc_a, args.iscc_b)

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
