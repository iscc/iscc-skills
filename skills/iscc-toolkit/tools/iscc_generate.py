#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Code Generator

Generate complete ISCC-CODE for any media file (text, image, audio, video).
Returns full IsccMeta object with all generated units and metadata.
"""

import argparse
import json
import sys
from pathlib import Path

import iscc_sdk as idk


def generate_iscc(file_path, bits, granular, meta_only):
    # type: (Path, int, bool, bool) -> dict
    """
    Generate ISCC code from a media file.

    Args:
        file_path: Path to media file
        bits: Bit length for ISCC codes (64, 128, 192, or 256)
        granular: Include granular features (semantic codes)
        meta_only: Skip content processing, only generate from metadata

    Returns:
        Dictionary containing IsccMeta fields
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    # Generate ISCC code
    try:
        # Convert to string for SDK compatibility
        fp_str = str(file_path)

        # Configure options
        kwargs = {}
        if bits is not None:
            kwargs["bits"] = bits
        if granular:
            kwargs["granular"] = granular
        if meta_only:
            kwargs["meta_only"] = meta_only

        iscc_meta = idk.code_iscc(fp_str, **kwargs)

        # Convert to dictionary for JSON serialization
        if hasattr(iscc_meta, "dict"):
            return iscc_meta.dict()
        elif hasattr(iscc_meta, "model_dump"):
            return iscc_meta.model_dump()
        else:
            # Fallback for dict-like objects
            return dict(iscc_meta)

    except Exception as e:
        raise RuntimeError(f"Failed to generate ISCC: {e}") from e


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
        description="Generate ISCC code from media files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s --bits 128 image.jpg
  %(prog)s --granular --pretty video.mp4
  %(prog)s --meta-only audio.mp3
        """,
    )

    parser.add_argument("file", type=Path, help="Media file to process")

    parser.add_argument(
        "--bits",
        type=int,
        choices=[64, 128, 192, 256],
        help="Bit length for ISCC codes (default: 64)",
    )

    parser.add_argument(
        "--granular",
        action="store_true",
        help="Include granular features (semantic codes)",
    )

    parser.add_argument(
        "--meta-only",
        action="store_true",
        help="Skip content processing, only generate from metadata",
    )

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        result = generate_iscc(args.file, args.bits, args.granular, args.meta_only)
        print(format_output(result, args.pretty))
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
