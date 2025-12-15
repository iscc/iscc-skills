# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-crypto>=0.3.0"]
# ///
"""
ISCC Keypair Manager

Generate, store, and display Ed25519 keypairs for ISCC cryptographic operations.
Supports platform-secure storage and environment-based key retrieval.
"""

import argparse
import sys

try:
    from iscc_crypto import (
        key_from_env,
        key_from_platform,
        key_generate,
        key_to_platform,
    )
except ImportError:
    print("Error: iscc-crypto package is not installed.", file=sys.stderr)
    print("Install it with: pip install iscc-crypto>=0.3.0", file=sys.stderr)
    sys.exit(1)

from iscc_utils import format_output


def generate_keypair(controller=None, key_id=None):
    # type: (str | None, str | None) -> dict
    """
    Generate a new Ed25519 keypair.

    Args:
        controller: Optional DID controller for the keypair
        key_id: Optional key identifier

    Returns:
        Dictionary with keypair information
    """
    keypair = key_generate(controller=controller, key_id=key_id)
    return keypair


def save_keypair(keypair, key_id=None):
    # type: (dict, str | None) -> None
    """
    Save keypair to platform-secure storage.

    Args:
        keypair: The keypair dictionary to save
        key_id: Optional key identifier for storage
    """
    key_to_platform(keypair, key_id=key_id)


def load_keypair_from_platform(key_id=None):
    # type: (str | None) -> dict | None
    """
    Load keypair from platform-secure storage.

    Args:
        key_id: Optional key identifier to load specific keypair

    Returns:
        Keypair dictionary or None if not found
    """
    try:
        keypair = key_from_platform(key_id=key_id)
        return keypair
    except Exception:
        return None


def load_keypair_from_env():
    # type: () -> dict | None
    """
    Load keypair from environment variables.

    Returns:
        Keypair dictionary or None if not found
    """
    try:
        keypair = key_from_env()
        return keypair
    except Exception:
        return None


def get_keypair_info(keypair):
    # type: (dict) -> dict
    """
    Extract displayable information from keypair.

    Args:
        keypair: The keypair dictionary

    Returns:
        Dictionary with public key and controller info
    """
    info = {
        "public_key": keypair.get("public_key"),
        "key_id": keypair.get("key_id"),
        "controller": keypair.get("controller"),
    }
    # Remove None values
    return {k: v for k, v in info.items() if v is not None}


def main():
    # type: () -> None
    """Main entry point for the keypair manager."""
    parser = argparse.ArgumentParser(
        description="Generate and manage Ed25519 keypairs for ISCC operations"
    )
    parser.add_argument("--generate", action="store_true", help="Generate a new keypair")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display existing keypair from storage or environment",
    )
    parser.add_argument("--controller", type=str, help="DID controller for the keypair")
    parser.add_argument("--key-id", type=str, help="Key identifier for storage/retrieval")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    # Validate arguments
    if not args.generate and not args.show:
        parser.error("Either --generate or --show must be specified")

    if args.generate and args.show:
        parser.error("Cannot specify both --generate and --show")

    try:
        if args.generate:
            # Generate new keypair
            keypair = generate_keypair(controller=args.controller, key_id=args.key_id)

            # Save to platform storage
            save_keypair(keypair, key_id=args.key_id)

            # Get displayable info
            info = get_keypair_info(keypair)
            info["status"] = "generated"
            info["saved_to"] = "platform_storage"

            print(format_output(info, args.pretty))
            sys.exit(0)

        elif args.show:
            # Try loading from platform storage first
            keypair = load_keypair_from_platform(key_id=args.key_id)
            source = "platform_storage"

            # If not found in platform storage, try environment
            if keypair is None:
                keypair = load_keypair_from_env()
                source = "environment"

            if keypair is None:
                error_msg = {
                    "error": "No keypair found",
                    "message": "No keypair found in platform storage or environment",
                }
                print(format_output(error_msg, args.pretty), file=sys.stderr)
                sys.exit(1)

            # Get displayable info
            info = get_keypair_info(keypair)
            info["source"] = source

            print(format_output(info, args.pretty))
            sys.exit(0)

    except Exception as e:
        error_msg = {"error": "Operation failed", "message": str(e)}
        print(format_output(error_msg, args.pretty), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
