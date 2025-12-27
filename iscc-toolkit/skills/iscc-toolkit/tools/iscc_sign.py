# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-crypto>=0.3.0"]
# ///
"""
ISCC Note Signer

Sign ISCC metadata and notes using Ed25519 keypairs from platform storage or environment.
Outputs signed JSON in ISCC-SIG format.
"""

import argparse
import sys

try:
    from iscc_crypto import key_from_env, sign_iscc_note, sign_json
except ImportError:
    print("Error: iscc-crypto package is not installed.", file=sys.stderr)
    print("Install it with: pip install iscc-crypto>=0.3.0", file=sys.stderr)
    sys.exit(1)

from iscc_utils import format_output, read_input


def load_keypair():
    # type: () -> dict
    """
    Load keypair from environment or platform storage.

    The key_from_env() function automatically falls back to platform storage.

    Returns:
        Keypair dictionary

    Raises:
        Exception: If no keypair is found
    """
    keypair = key_from_env()
    return keypair


def sign_data(data, keypair, use_iscc_note=False):
    # type: (dict, dict, bool) -> dict
    """
    Sign the data using the provided keypair.

    Args:
        data: JSON data to sign
        keypair: Keypair to use for signing
        use_iscc_note: If True, use sign_iscc_note(); otherwise use sign_json()

    Returns:
        Signed JSON data with signature
    """
    if use_iscc_note:
        signed_data = sign_iscc_note(data, keypair)
    else:
        signed_data = sign_json(data, keypair)

    return signed_data


def main():
    # type: () -> None
    """Main entry point for the ISCC note signer."""
    parser = argparse.ArgumentParser(
        description="Sign ISCC metadata and notes with Ed25519 signatures"
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Input JSON file path (use '-' for stdin, default: stdin)",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument(
        "--iscc-note",
        action="store_true",
        help="Use sign_iscc_note() instead of sign_json()",
    )

    args = parser.parse_args()

    try:
        # Load keypair from environment or platform storage
        try:
            keypair = load_keypair()
        except Exception as e:
            error_msg = {
                "error": "Keypair not found",
                "message": f"Could not load keypair from environment or platform storage: {e}",
            }
            print(format_output(error_msg, args.pretty), file=sys.stderr)
            sys.exit(1)

        # Read input data
        try:
            data = read_input(args.input)
        except (ValueError, FileNotFoundError) as e:
            error_msg = {"error": "Input error", "message": str(e)}
            print(format_output(error_msg, args.pretty), file=sys.stderr)
            sys.exit(1)

        # Sign the data
        try:
            signed_data = sign_data(data, keypair, use_iscc_note=args.iscc_note)
        except Exception as e:
            error_msg = {"error": "Signing failed", "message": str(e)}
            print(format_output(error_msg, args.pretty), file=sys.stderr)
            sys.exit(1)

        # Output signed data
        print(format_output(signed_data, args.pretty))
        sys.exit(0)

    except KeyboardInterrupt:
        error_msg = {"error": "Interrupted", "message": "Operation cancelled by user"}
        print(format_output(error_msg, args.pretty), file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        error_msg = {"error": "Unexpected error", "message": str(e)}
        print(format_output(error_msg, args.pretty), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
