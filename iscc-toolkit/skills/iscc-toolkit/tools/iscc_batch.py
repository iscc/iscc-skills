#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk>=0.7.0"]
# ///
"""
ISCC Batch Processor

Recursively process all media files in a directory and generate ISCC codes.
Supports parallel processing, progress reporting, and multiple output formats.
"""

import argparse
import csv
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import iscc_sdk as idk

# Common media file extensions
MEDIA_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".doc",
    ".docx",
    ".odt",
    ".rtf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".tiff",
    ".webp",
    ".svg",
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".m4a",
    ".aac",
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".html",
    ".xml",
    ".json",
    ".csv",
    ".epub",
    ".mobi",
}


def is_media_file(file_path):
    # type: (Path) -> bool
    """
    Check if file is a supported media file.

    Args:
        file_path: Path to check

    Returns:
        True if file extension is supported
    """
    return file_path.suffix.lower() in MEDIA_EXTENSIONS


def has_sidecar(file_path):
    # type: (Path) -> bool
    """
    Check if file has .iscc.json sidecar (already processed).

    Args:
        file_path: Path to media file

    Returns:
        True if sidecar exists
    """
    sidecar_path = file_path.with_suffix(file_path.suffix + ".iscc.json")
    return sidecar_path.exists()


def find_media_files(directory, recursive):
    # type: (Path, bool) -> Iterator[Path]
    """
    Find all media files in directory.

    Args:
        directory: Directory to search
        recursive: Search subdirectories

    Yields:
        Path objects for media files
    """
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"

    for path in directory.glob(pattern):
        if path.is_file() and is_media_file(path):
            yield path


def process_file(file_path, force):
    # type: (Path, bool) -> Optional[dict]
    """
    Process single file and generate ISCC.

    Args:
        file_path: Path to file
        force: Process even if sidecar exists

    Returns:
        Dictionary with file path and ISCC metadata, or None if skipped
    """
    # Skip if already processed (unless force)
    if not force and has_sidecar(file_path):
        return None

    try:
        # Generate ISCC
        iscc_meta = idk.code_iscc(str(file_path))

        # Convert to dict
        if hasattr(iscc_meta, "dict"):
            meta_dict = iscc_meta.dict()
        elif hasattr(iscc_meta, "model_dump"):
            meta_dict = iscc_meta.model_dump()
        else:
            meta_dict = dict(iscc_meta)

        # Add file path
        result = {"file": str(file_path.resolve()), "iscc": meta_dict}

        return result

    except Exception as e:
        # Return error information
        return {"file": str(file_path.resolve()), "error": str(e)}


def batch_process(directory, recursive, force, workers):
    # type: (Path, bool, bool, int) -> list[dict]
    """
    Process all media files in directory.

    Args:
        directory: Directory to process
        recursive: Search subdirectories
        force: Process even if already processed
        workers: Number of parallel workers

    Returns:
        List of results
    """
    # Find all media files
    files = list(find_media_files(directory, recursive))
    total = len(files)

    if total == 0:
        print("No media files found", file=sys.stderr)
        return []

    print(f"Processing {total} files...", file=sys.stderr)
    start_time = time.time()

    results = []
    processed = 0
    skipped = 0
    errors = 0

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(process_file, f, force): f for f in files}

        # Collect results as they complete
        for future in as_completed(future_to_file):
            result = future.result()

            if result is None:
                skipped += 1
            elif "error" in result:
                errors += 1
                results.append(result)
            else:
                processed += 1
                results.append(result)

            # Progress update
            done = processed + skipped + errors
            msg = f"\rProgress: {done}/{total} ({processed} ok, {skipped} skip, {errors} err)"
            print(msg, file=sys.stderr, end="")

    elapsed = time.time() - start_time
    print(f"\n\nCompleted in {elapsed:.2f}s", file=sys.stderr)

    return results


def format_json(results, pretty):
    # type: (list[dict], bool) -> str
    """
    Format results as JSON.

    Args:
        results: List of result dictionaries
        pretty: Use human-readable formatting

    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(results, indent=2, ensure_ascii=False)
    return json.dumps(results, separators=(",", ":"), ensure_ascii=False)


def format_jsonl(results):
    # type: (list[dict]) -> str
    """
    Format results as JSON Lines.

    Args:
        results: List of result dictionaries

    Returns:
        JSON Lines string (one JSON object per line)
    """
    lines = [json.dumps(r, separators=(",", ":"), ensure_ascii=False) for r in results]
    return "\n".join(lines)


def format_csv(results):
    # type: (list[dict]) -> str
    """
    Format results as CSV.

    Args:
        results: List of result dictionaries

    Returns:
        CSV string
    """
    import io  # Local import for rarely-used CSV formatting

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["file", "iscc", "error"])

    # Rows
    for result in results:
        file_path = result.get("file", "")
        error = result.get("error", "")

        if error:
            iscc_code = ""
        else:
            iscc_meta = result.get("iscc", {})
            iscc_code = iscc_meta.get("iscc", "")

        writer.writerow([file_path, iscc_code, error])

    return output.getvalue()


def format_output(results, output_format, pretty):
    # type: (list[dict], str, bool) -> str
    """
    Format results in specified format.

    Args:
        results: List of result dictionaries
        output_format: Output format (json, jsonl, csv)
        pretty: Use human-readable formatting (JSON only)

    Returns:
        Formatted string
    """
    if output_format == "json":
        return format_json(results, pretty)
    elif output_format == "jsonl":
        return format_jsonl(results)
    elif output_format == "csv":
        return format_csv(results)
    else:
        raise ValueError(f"Unknown format: {output_format}")


def main():
    # type: () -> int
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch process media files and generate ISCC codes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/media
  %(prog)s --recursive --workers 8 /path/to/media
  %(prog)s --output results.json --format json /path/to/media
  %(prog)s --force --format csv /path/to/media > results.csv
        """,
    )

    parser.add_argument("directory", type=Path, help="Directory to process")

    parser.add_argument(
        "--recursive", action="store_true", help="Process subdirectories recursively"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Process files even if .iscc.json sidecar exists",
    )

    parser.add_argument(
        "--workers", type=int, default=4, help="Number of parallel workers (default: 4)"
    )

    parser.add_argument(
        "--format",
        choices=["json", "jsonl", "csv"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument("--output", type=Path, help="Output file (default: stdout)")

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    # Validate directory
    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}", file=sys.stderr)
        return 2

    if not args.directory.is_dir():
        print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
        return 2

    try:
        # Process files
        results = batch_process(args.directory, args.recursive, args.force, args.workers)

        # Format output
        output = format_output(results, args.format, args.pretty)

        # Write output
        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Results written to {args.output}", file=sys.stderr)
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
