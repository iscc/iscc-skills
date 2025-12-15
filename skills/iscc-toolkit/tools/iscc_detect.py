#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Media Type Detection Tool

Detect MIME type, processing mode, and file characteristics for ISCC generation.
Reports whether a file is supported for ISCC code generation.
"""

import argparse
import json
import sys
from pathlib import Path

import iscc_sdk as idk


def detect_media_type(file_path, verbose):
    # type: (Path, bool) -> dict
    """
    Detect media type and ISCC processing characteristics.

    Args:
        file_path: Path to the media file
        verbose: Include detailed detection information

    Returns:
        Dictionary containing detection results
    """
    # Get file size
    file_size = file_path.stat().st_size

    # Detect MIME type
    try:
        mediatype = idk.mediatype_detect(str(file_path))
    except Exception as e:
        raise RuntimeError(f"Failed to detect media type: {e}") from e

    # Determine ISCC processing mode
    try:
        mode = idk.mediatype_to_mode(mediatype)
    except Exception:
        mode = None

    # Check if supported for ISCC generation
    try:
        is_supported = idk.mediatype_is_supported(mediatype)
    except Exception:
        is_supported = False

    # Build result
    result = {
        "file": str(file_path.resolve()),
        "mediatype": mediatype,
        "mode": mode,
        "supported": is_supported,
    }

    if verbose:
        result["size_bytes"] = file_size
        result["size_human"] = format_size(file_size)
        result["extension"] = file_path.suffix.lower()

    return result


def format_size(size_bytes):
    # type: (int) -> str
    """
    Format file size in human-readable form.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human-readable size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_output(data, pretty):
    # type: (dict | list, bool) -> str
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
        description="Detect media type and ISCC processing mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpg
  %(prog)s --verbose document.pdf
  %(prog)s --pretty audio.mp3
  %(prog)s *.jpg
        """,
    )

    parser.add_argument("files", nargs="+", type=Path, help="Media file(s) to analyze")

    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed detection information"
    )

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        results = []
        errors = []

        for file_path in args.files:
            # Validate file exists
            if not file_path.exists():
                errors.append({"file": str(file_path), "error": "File not found"})
                continue

            if not file_path.is_file():
                errors.append({"file": str(file_path), "error": "Not a regular file"})
                continue

            try:
                result = detect_media_type(file_path, args.verbose)
                results.append(result)
            except Exception as e:
                errors.append({"file": str(file_path), "error": str(e)})

        # Prepare output
        if len(args.files) == 1 and results:
            # Single file - output result directly
            output = results[0]
        else:
            # Multiple files - output array with separate errors
            output = {"results": results}
            if errors:
                output["errors"] = errors

        print(format_output(output, args.pretty))

        # Return non-zero if any errors occurred
        return 1 if errors else 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
