# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-crypto>=0.3.0"]
# ///
"""
ISCC Note Verifier

Verify cryptographic signatures on ISCC notes and metadata.
Checks signature validity and optionally verifies identity against controller.
"""

import argparse
import sys

try:
    from iscc_crypto import verify_iscc_note, verify_json
except ImportError:
    print("Error: iscc-crypto package is not installed.", file=sys.stderr)
    print("Install it with: pip install iscc-crypto>=0.3.0", file=sys.stderr)
    sys.exit(1)

from iscc_utils import format_output, read_input


def verify_signature(data, use_iscc_note=False):
    # type: (dict, bool) -> dict
    """
    Verify the signature on the provided data.

    Args:
        data: Signed JSON data to verify
        use_iscc_note: If True, use verify_iscc_note(); otherwise use verify_json()

    Returns:
        Dictionary with verification results including:
        - valid: Boolean indicating if signature is valid
        - signer: Information about the signer (if available)
        - controller: Controller information (if present)
        - error: Error message (if verification failed)
    """
    try:
        if use_iscc_note:
            result = verify_iscc_note(data)
        else:
            result = verify_json(data)

        # Handle different possible return formats from iscc-crypto
        if isinstance(result, bool):
            # Simple boolean result
            return {
                "valid": result,
                "message": "Signature is valid" if result else "Signature is invalid",
            }
        elif isinstance(result, dict):
            # Detailed result object
            return result
        else:
            # Unexpected result type
            return {
                "valid": bool(result),
                "message": "Verification completed with unexpected result format",
            }

    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Verification failed with error",
        }


def main():
    # type: () -> None
    """Main entry point for the ISCC note verifier."""
    parser = argparse.ArgumentParser(
        description="Verify cryptographic signatures on ISCC notes and metadata"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input signed JSON file path (use '-' for stdin, default: stdin)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument(
        "--iscc-note",
        action="store_true",
        help="Use verify_iscc_note() instead of verify_json()",
    )

    args = parser.parse_args()

    try:
        # Read input data
        try:
            data = read_input(args.input)
        except (ValueError, FileNotFoundError) as e:
            error_msg = {"valid": False, "error": "Input error", "message": str(e)}
            print(format_output(error_msg, args.pretty), file=sys.stderr)
            sys.exit(1)

        # Verify the signature
        result = verify_signature(data, use_iscc_note=args.iscc_note)

        # Extract signer and controller information if present in the original data
        if "signer" not in result and "public_key" in data:
            result["signer"] = {"public_key": data["public_key"]}
        if "controller" not in result and "controller" in data:
            result["controller"] = data["controller"]

        # Output verification result
        print(format_output(result, args.pretty))

        # Exit with appropriate code
        if result.get("valid", False):
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        error_msg = {
            "valid": False,
            "error": "Interrupted",
            "message": "Operation cancelled by user",
        }
        print(format_output(error_msg, args.pretty), file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        error_msg = {"valid": False, "error": "Unexpected error", "message": str(e)}
        print(format_output(error_msg, args.pretty), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
