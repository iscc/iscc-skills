#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Metadata Embedding Tool

Embed ISCC metadata into media files. Supports PDF, EPUB, DOCX, images, and audio.
Metadata can be provided as a JSON file or via stdin.
"""

import argparse
import json
import sys
from pathlib import Path

import iscc_sdk as idk


def read_metadata(metadata_source):
    # type: (str | Path) -> dict
    """
    Read metadata from file or stdin.

    Args:
        metadata_source: Path to JSON file or '-' for stdin

    Returns:
        Metadata dictionary
    """
    if metadata_source == "-":
        # Read from stdin
        try:
            data = sys.stdin.read()
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from stdin: {e}") from e
    else:
        # Read from file
        metadata_path = Path(metadata_source)
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        try:
            with metadata_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {metadata_path}: {e}") from e


def embed_metadata(file_path, metadata, output_path):
    # type: (Path, dict, Path | None) -> Path
    """
    Embed metadata into a media file.

    Args:
        file_path: Path to input media file
        metadata: Metadata dictionary to embed
        output_path: Optional output path (defaults to overwriting input)

    Returns:
        Path to output file
    """
    # Determine output path
    if output_path is None:
        target_path = file_path
    else:
        target_path = output_path

    try:
        # Embed metadata using SDK
        result = idk.embed_metadata(str(file_path), metadata, str(target_path))

        # Return path based on result type
        if isinstance(result, str):
            return Path(result)
        elif isinstance(result, Path):
            return result
        else:
            # Assume embedding succeeded, return target path
            return target_path

    except Exception as e:
        raise RuntimeError(f"Failed to embed metadata: {e}") from e


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
        description="Embed ISCC metadata into media files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file document.pdf --metadata metadata.json --output output.pdf
  %(prog)s --file image.jpg --metadata metadata.json
  %(prog)s --file audio.mp3 --metadata - < metadata.json
  %(prog)s -f doc.pdf -m meta.json -o /path/to/output.pdf

Supported formats:
  - PDF (.pdf)
  - EPUB (.epub)
  - Word documents (.docx)
  - Images (JPEG, PNG, WebP with EXIF support)
  - Audio (MP3, FLAC, M4A with ID3/Vorbis tags)
        """,
    )

    parser.add_argument(
        "--file",
        "-f",
        required=True,
        type=Path,
        help="Media file to embed metadata into",
    )

    parser.add_argument(
        "--metadata", "-m", required=True, help="JSON metadata file or '-' for stdin"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path (default: overwrite input file)",
    )

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        # Validate input file exists
        if not args.file.exists():
            print(f"Error: Input file not found: {args.file}", file=sys.stderr)
            return 1

        if not args.file.is_file():
            print(f"Error: Not a regular file: {args.file}", file=sys.stderr)
            return 1

        # Read metadata
        try:
            metadata = read_metadata(args.metadata)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Embed metadata
        try:
            output_path = embed_metadata(args.file, metadata, args.output)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Output success result
        result = {
            "status": "success",
            "input_file": str(args.file.resolve()),
            "output_file": str(output_path.resolve()),
            "metadata_embedded": True,
        }

        print(format_output(result, args.pretty))
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
