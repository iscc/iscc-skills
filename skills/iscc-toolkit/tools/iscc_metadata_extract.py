#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Metadata Extraction Tool

Extract metadata from media files (text, image, audio, video) for ISCC generation.
Outputs structured metadata in JSON format.
"""

import argparse
import json
import sys
from pathlib import Path

import iscc_sdk as idk


def extract_metadata(file_path):
    # type: (Path) -> dict
    """
    Extract metadata from a media file.

    Args:
        file_path: Path to the media file

    Returns:
        Dictionary containing extracted metadata
    """
    try:
        metadata = idk.extract_metadata(str(file_path))
    except Exception as e:
        raise RuntimeError(f"Failed to extract metadata: {e}") from e

    # Convert to dictionary if needed
    if hasattr(metadata, "dict"):
        # Pydantic model
        return metadata.dict()
    elif hasattr(metadata, "__dict__"):
        # Regular object
        return vars(metadata)
    elif isinstance(metadata, dict):
        return metadata
    else:
        # Fallback - try to serialize
        return {"raw": str(metadata)}


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
        return json.dumps(data, indent=2, ensure_ascii=False, default=str)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False, default=str)


def main():
    # type: () -> int
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract metadata from media files for ISCC generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s --pretty image.jpg
  %(prog)s file1.mp3 file2.mp3 file3.mp3
  %(prog)s *.jpg > metadata.json
        """,
    )

    parser.add_argument(
        "files", nargs="+", type=Path, help="Media file(s) to extract metadata from"
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
                metadata = extract_metadata(file_path)
                result = {"file": str(file_path.resolve()), "metadata": metadata}
                results.append(result)
            except Exception as e:
                errors.append({"file": str(file_path), "error": str(e)})

        # Prepare output
        if len(args.files) == 1 and results:
            # Single file - output metadata directly
            output = results[0]["metadata"]
        else:
            # Multiple files - output array with file paths
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
