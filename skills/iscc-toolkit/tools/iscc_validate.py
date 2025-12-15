# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-core>=1.0.0"]
# ///
"""Validate ISCC structure and format.

This script validates ISCC-CODE strings for proper format, structure, and
unit composition rules. Supports strict validation mode and JSON schema
validation for IsccMeta objects.
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


def validate_iscc(iscc_code, strict=False):
    # type: (str, bool) -> dict
    """
    Validate an ISCC code for structural correctness.

    :param iscc_code: ISCC code to validate
    :param strict: Enable strict validation mode
    :return: Dictionary containing validation results
    """
    result = {
        "iscc_code": iscc_code,
        "valid": False,
        "errors": [],
        "warnings": [],
        "details": {},
    }

    try:
        # Check if the ISCC can be validated using iscc_validate if available
        # Otherwise try to decode and decompose
        try:
            validation_result = ic.iscc_validate(iscc_code)
            result["valid"] = validation_result
            result["details"]["validated_via"] = "iscc_validate"
        except AttributeError:
            # iscc_validate may not be available, try decoding instead
            ic.decode(iscc_code)  # Validates by attempting decode
            result["valid"] = True
            result["details"]["validated_via"] = "decode"

        # Try to decompose the ISCC
        try:
            units = ic.iscc_decompose(iscc_code)
            result["details"]["unit_count"] = len(units)
            result["details"]["units"] = units

            # Validate minimum unit requirements
            if len(units) < 2:
                result["errors"].append("ISCC-CODE must contain at least 2 units (DATA + INSTANCE)")
                if strict:
                    result["valid"] = False

            # Get explanation for each unit
            unit_explanations = []
            for unit in units:
                try:
                    explanation = ic.iscc_explain(unit)
                    unit_explanations.append(explanation)
                except Exception as e:
                    result["warnings"].append(f"Could not explain unit {unit}: {str(e)}")

            result["details"]["unit_details"] = unit_explanations

        except Exception as e:
            result["errors"].append(f"Decomposition failed: {str(e)}")
            if strict:
                result["valid"] = False

        # Try to get overall explanation
        try:
            explanation = ic.iscc_explain(iscc_code)
            result["details"]["explanation"] = explanation
        except Exception as e:
            result["warnings"].append(f"Could not explain ISCC: {str(e)}")

    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Validation failed: {str(e)}")

    return result


def validate_metadata_schema(metadata_json, strict=False):
    # type: (str, bool) -> dict
    """
    Validate IsccMeta JSON against schema.

    :param metadata_json: JSON string containing IsccMeta object
    :param strict: Enable strict validation mode
    :return: Dictionary containing validation results
    """
    result = {"valid": False, "errors": [], "warnings": []}

    try:
        # Parse JSON
        metadata = json.loads(metadata_json)

        # Check for required fields in IsccMeta
        required_fields = ["iscc"]
        for field in required_fields:
            if field not in metadata:
                result["errors"].append(f"Missing required field: {field}")

        # If ISCC field exists, validate it
        if "iscc" in metadata:
            iscc_validation = validate_iscc(metadata["iscc"], strict)
            if not iscc_validation["valid"]:
                result["errors"].extend(iscc_validation["errors"])
            result["iscc_validation"] = iscc_validation

        # If no errors, mark as valid
        if not result["errors"]:
            result["valid"] = True

    except json.JSONDecodeError as e:
        result["errors"].append(f"Invalid JSON: {str(e)}")
    except Exception as e:
        result["errors"].append(f"Schema validation failed: {str(e)}")

    return result


def format_pretty(result, is_schema=False):
    # type: (dict, bool) -> str
    """
    Format validation results for human-readable output.

    :param result: Validation result dictionary
    :param is_schema: Whether this is a schema validation result
    :return: Formatted string
    """
    lines = []
    lines.append("=" * 70)
    lines.append("ISCC Validation Report")
    lines.append("=" * 70)

    if not is_schema:
        lines.append(f"ISCC Code: {result['iscc_code']}")
        lines.append("-" * 70)

    status = "VALID" if result["valid"] else "INVALID"
    symbol = "✓" if result["valid"] else "✗"
    lines.append(f"Status: {symbol} {status}")
    lines.append("-" * 70)

    if result.get("errors"):
        lines.append("Errors:")
        for error in result["errors"]:
            lines.append(f"  • {error}")
        lines.append("-" * 70)

    if result.get("warnings"):
        lines.append("Warnings:")
        for warning in result["warnings"]:
            lines.append(f"  • {warning}")
        lines.append("-" * 70)

    if "details" in result and result["details"]:
        lines.append("Details:")
        for key, value in result["details"].items():
            if key != "unit_details":
                lines.append(f"  {key}: {value}")

        if "unit_details" in result["details"]:
            lines.append("\n  Unit Details:")
            for i, unit_detail in enumerate(result["details"]["unit_details"], 1):
                lines.append(f"    Unit {i}:")
                for k, v in unit_detail.items():
                    lines.append(f"      {k}: {v}")

    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    # type: () -> None
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Validate ISCC structure and format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ISCC:AAAA...
  %(prog)s --strict ISCC:AAAA...
  %(prog)s --schema metadata.json
  %(prog)s --pretty --strict ISCC:AAAA...
        """,
    )

    parser.add_argument("input", help="ISCC code to validate or path to JSON file with --schema")

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Output human-readable format instead of JSON",
    )

    parser.add_argument("--strict", action="store_true", help="Enable strict validation mode")

    parser.add_argument(
        "--schema", action="store_true", help="Validate IsccMeta JSON schema from file"
    )

    args = parser.parse_args()

    # Perform validation
    if args.schema:
        # Read JSON file
        try:
            json_path = Path(args.input)
            if not json_path.exists():
                print(f"Error: File not found: {args.input}", file=sys.stderr)
                sys.exit(1)
            with open(json_path, encoding="utf-8") as f:
                metadata_json = f.read()
            result = validate_metadata_schema(metadata_json, args.strict)
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Validate ISCC code
        result = validate_iscc(args.input, args.strict)

    # Output results
    if args.pretty:
        print(format_pretty(result, args.schema))
    else:
        print(json.dumps(result, indent=2))

    # Exit with error code if validation failed
    if not result["valid"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
