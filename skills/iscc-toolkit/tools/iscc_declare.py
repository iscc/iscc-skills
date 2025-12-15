#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-crypto>=0.3.0", "httpx>=0.27.0"]
# ///
"""
ISCC Declaration Tool

Declare an ISCC code to the ISCC registry via API. Creates a signed IsccNote
and submits it to the declaration endpoint.
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC

import httpx
from iscc_crypto import create_nonce, key_generate, sign_json

DEFAULT_API_URL = "https://sb0.iscc.id/declaration"


def create_iscc_note(iscc_code, datahash, keypair):
    # type: (str, str, object) -> dict
    """
    Create a signed IsccNote for declaration.

    Args:
        iscc_code: ISCC code to declare
        datahash: Data hash (required)
        keypair: KeyPair object from iscc_crypto

    Returns:
        Dictionary containing signed IsccNote fields
    """
    from datetime import datetime

    # Create timestamp in ISO 8601 format with Z suffix
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Generate nonce using iscc_crypto (32 hex chars)
    nonce = create_nonce(0)

    # Build note data
    note_data = {
        "iscc_code": iscc_code,
        "datahash": datahash,
        "nonce": nonce,
        "timestamp": timestamp,
    }

    # Sign the note using iscc_crypto's sign_json
    signed_note = sign_json(note_data, keypair)

    return signed_note


async def declare_iscc(iscc_code, api_url, force, datahash):
    # type: (str, str, bool, str) -> dict
    """
    Declare ISCC code to the registry.

    Args:
        iscc_code: ISCC code to declare
        api_url: API endpoint URL
        force: Override duplicate detection
        datahash: Data hash (required)

    Returns:
        API response as dictionary
    """
    # Generate a new keypair for signing
    keypair = key_generate()

    # Create signed note
    note = create_iscc_note(iscc_code, datahash, keypair)

    # Add force flag if requested
    if force:
        note["force"] = True

    # Submit declaration
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(api_url, json=note)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Try to extract error message from response
            try:
                error_data = e.response.json()
                error_msg = json.dumps(error_data, indent=2)
            except Exception:
                error_msg = e.response.text or str(e)
            raise RuntimeError(f"API error ({e.response.status_code}): {error_msg}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Request failed: {e}") from e


def format_output(data, pretty):
    # type: (dict, bool) -> str
    """
    Format output as JSON.

    Args:
        data: Data to format
        pretty: Use human-readable formatting

    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def main():
    # type: () -> int
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Declare ISCC code to the ISCC registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY
  %(prog)s --force --datahash abc123 ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY
  %(prog)s --api-url https://index.iscc.id/declaration ISCC:KACYPXW445FTYNJ3
        """,
    )

    parser.add_argument("iscc_code", help="ISCC code to declare")

    parser.add_argument("--force", action="store_true", help="Override duplicate detection")

    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Declaration API endpoint (default: {DEFAULT_API_URL})",
    )

    parser.add_argument("--datahash", required=True, help="Data hash (required)")

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    # Validate ISCC code format
    if not args.iscc_code.startswith("ISCC:"):
        print("Error: ISCC code must start with 'ISCC:' prefix", file=sys.stderr)
        return 1

    try:
        # Run async declaration
        result = asyncio.run(declare_iscc(args.iscc_code, args.api_url, args.force, args.datahash))

        # Output result
        print(format_output(result, args.pretty))
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
