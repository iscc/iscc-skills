#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Thumbnail Generator

Generate thumbnail images from media files. Outputs as data URL (base64) or saves
to file. Supports configurable size, format, and quality.
"""

import argparse
import base64
import sys
from pathlib import Path

import iscc_sdk as idk


def generate_thumbnail(file_path, size, img_format, quality):
    # type: (Path, Optional[int], str, Optional[int]) -> str
    """
    Generate thumbnail from media file.

    Args:
        file_path: Path to media file
        size: Maximum dimension in pixels
        img_format: Output format (webp, jpeg, png)
        quality: Quality for lossy formats (1-100)

    Returns:
        Data URL (base64-encoded image)
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    try:
        # Build kwargs
        kwargs = {}
        if size is not None:
            kwargs["size"] = size
        if img_format is not None:
            kwargs["format"] = img_format
        if quality is not None:
            kwargs["quality"] = quality

        # Generate thumbnail
        fp_str = str(file_path)
        data_url = idk.thumbnail(fp_str, **kwargs)

        return data_url

    except Exception as e:
        raise RuntimeError(f"Failed to generate thumbnail: {e}") from e


def save_thumbnail_to_file(data_url, output_path):
    # type: (str, Path) -> None
    """
    Save data URL thumbnail to file.

    Args:
        data_url: Base64 data URL
        output_path: Output file path
    """
    # Parse data URL: data:image/webp;base64,<data>
    if not data_url.startswith("data:"):
        raise ValueError("Invalid data URL format")

    try:
        # Split header and data
        header, data = data_url.split(",", 1)

        # Decode base64
        image_data = base64.b64decode(data)

        # Write to file
        output_path.write_bytes(image_data)

    except Exception as e:
        raise RuntimeError(f"Failed to save thumbnail: {e}") from e


def main():
    # type: () -> int
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate thumbnails from media files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.jpg
  %(prog)s --size 256 --format jpeg video.mp4
  %(prog)s --output thumb.webp --quality 90 document.pdf
  %(prog)s --format png image.jpg > thumbnail_data_url.txt
        """,
    )

    parser.add_argument("file", type=Path, help="Media file to process")

    parser.add_argument("--size", type=int, help="Maximum dimension in pixels (default: 128)")

    parser.add_argument(
        "--format",
        choices=["webp", "jpeg", "png"],
        default="webp",
        help="Output image format (default: webp)",
    )

    parser.add_argument(
        "--quality", type=int, help="Quality for lossy formats, 1-100 (default: 75)"
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (if not specified, prints data URL to stdout)",
    )

    args = parser.parse_args()

    # Validate quality
    if args.quality is not None:
        if args.quality < 1 or args.quality > 100:
            print("Error: Quality must be between 1 and 100", file=sys.stderr)
            return 1

    # Validate size
    if args.size is not None:
        if args.size < 1:
            print("Error: Size must be positive", file=sys.stderr)
            return 1

    try:
        # Generate thumbnail
        data_url = generate_thumbnail(args.file, args.size, args.format, args.quality)

        # Output
        if args.output:
            # Save to file
            save_thumbnail_to_file(data_url, args.output)
            print(f"Thumbnail saved to {args.output}", file=sys.stderr)
        else:
            # Print data URL
            print(data_url)

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
