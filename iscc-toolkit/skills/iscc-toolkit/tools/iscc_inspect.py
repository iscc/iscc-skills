# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-core>=1.0.0"]
# ///
"""Decompose and inspect ISCC-CODEs.

This script decomposes an ISCC-CODE into its individual units and provides
detailed information about each unit's structure including maintype, subtype,
version, length, and binary representations.
"""

import argparse
import json
import sys

try:
    import iscc_core as ic
except ImportError:
    print(
        "Error: iscc-core is not installed. Install with: pip install iscc-core",
        file=sys.stderr,
    )
    sys.exit(1)


def inspect_iscc(iscc_code, show_binary=False, show_hex=False):
    # type: (str, bool, bool) -> dict
    """
    Decompose and inspect an ISCC code.

    :param iscc_code: ISCC code to inspect
    :param show_binary: Include binary representation
    :param show_hex: Include hexadecimal representation
    :return: Dictionary containing inspection results
    """
    try:
        # Decompose ISCC into individual units
        units = ic.iscc_decompose(iscc_code)

        # Get human-readable explanation
        explanation = ic.iscc_explain(iscc_code)

        # Collect detailed information for each unit
        unit_details = []
        for unit in units:
            try:
                unit_info = {"iscc": unit, "explanation": ic.iscc_explain(unit)}

                # Add binary representation if requested
                if show_binary:
                    # Decode to get binary digest
                    decoded = ic.decode(unit)
                    unit_info["binary"] = bin(int.from_bytes(decoded, byteorder="big"))

                # Add hex representation if requested
                if show_hex:
                    decoded = ic.decode(unit)
                    unit_info["hex"] = decoded.hex()

                unit_details.append(unit_info)
            except Exception as e:
                unit_details.append({"iscc": unit, "error": str(e)})

        result = {
            "iscc_code": iscc_code,
            "explanation": explanation,
            "units": unit_details,
            "unit_count": len(units),
        }

        return result

    except Exception as e:
        return {"error": str(e), "iscc_code": iscc_code}


def format_pretty(result):
    # type: (dict) -> str
    """
    Format inspection results for human-readable output.

    :param result: Inspection result dictionary
    :return: Formatted string
    """
    if "error" in result:
        return f"ERROR: {result['error']}"

    lines = []
    lines.append("=" * 70)
    lines.append("ISCC Inspection Report")
    lines.append("=" * 70)
    lines.append(f"ISCC Code: {result['iscc_code']}")
    lines.append("-" * 70)
    lines.append("Overall Structure:")
    for key, value in result["explanation"].items():
        lines.append(f"  {key}: {value}")
    lines.append("-" * 70)
    lines.append(f"Units: {result['unit_count']}")
    lines.append("-" * 70)

    for i, unit in enumerate(result["units"], 1):
        lines.append(f"\nUnit {i}: {unit['iscc']}")
        if "error" in unit:
            lines.append(f"  ERROR: {unit['error']}")
            continue

        if "explanation" in unit:
            for key, value in unit["explanation"].items():
                lines.append(f"  {key}: {value}")

        if "hex" in unit:
            lines.append(f"  Hex: {unit['hex']}")

        if "binary" in unit:
            lines.append(f"  Binary: {unit['binary']}")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    # type: () -> None
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Decompose and inspect ISCC-CODE structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ISCC:AAAA...
  %(prog)s --pretty --hex ISCC:AAAA...
  %(prog)s --binary --hex ISCC:AAAA...
        """,
    )

    parser.add_argument("iscc_code", help="ISCC code to inspect")

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output human-readable format instead of JSON",
    )

    parser.add_argument(
        "--binary",
        action="store_true",
        help="Include binary representation of each unit",
    )

    parser.add_argument(
        "--hex",
        action="store_true",
        help="Include hexadecimal representation of each unit",
    )

    args = parser.parse_args()

    # Perform inspection
    result = inspect_iscc(args.iscc_code, args.binary, args.hex)

    # Output results
    if args.pretty:
        print(format_pretty(result))
    else:
        print(json.dumps(result, indent=2))

    # Exit with error code if inspection failed
    if "error" in result:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
