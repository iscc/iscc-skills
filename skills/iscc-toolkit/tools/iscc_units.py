#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["iscc-sdk[all]>=0.7.0"]
# ///
"""
ISCC Unit Generator

Generate individual ISCC-UNITs: Meta-Code, Content-Code, Data-Code, Instance-Code,
and semantic codes for text and images.
"""

import argparse
import json
import sys
from pathlib import Path

import iscc_sdk as idk


def generate_meta_code(file_path, bits):
    # type: (Path, Optional[int]) -> dict
    """
    Generate Meta-Code from file metadata.

    Args:
        file_path: Path to file
        bits: Bit length for code

    Returns:
        Dictionary with meta code and metadata
    """
    fp_str = str(file_path)
    kwargs = {}
    if bits is not None:
        kwargs["bits"] = bits

    result = idk.code_meta(fp_str, **kwargs)

    if hasattr(result, "dict"):
        return result.dict()
    elif hasattr(result, "model_dump"):
        return result.model_dump()
    else:
        return dict(result)


def generate_content_code(file_path, bits):
    # type: (Path, Optional[int]) -> dict
    """
    Generate Content-Code from file content.

    Args:
        file_path: Path to file
        bits: Bit length for code

    Returns:
        Dictionary with content code
    """
    fp_str = str(file_path)
    kwargs = {}
    if bits is not None:
        kwargs["bits"] = bits

    result = idk.code_content(fp_str, **kwargs)

    if hasattr(result, "dict"):
        return result.dict()
    elif hasattr(result, "model_dump"):
        return result.model_dump()
    else:
        return dict(result)


def generate_data_code(file_path, bits):
    # type: (Path, Optional[int]) -> dict
    """
    Generate Data-Code from raw file data.

    Args:
        file_path: Path to file
        bits: Bit length for code

    Returns:
        Dictionary with data code
    """
    with open(file_path, "rb") as stream:
        kwargs = {}
        if bits is not None:
            kwargs["bits"] = bits

        result = idk.code_data(stream, **kwargs)

        if hasattr(result, "dict"):
            return result.dict()
        elif hasattr(result, "model_dump"):
            return result.model_dump()
        else:
            return dict(result)


def generate_instance_code(file_path, bits):
    # type: (Path, Optional[int]) -> dict
    """
    Generate Instance-Code from file.

    Args:
        file_path: Path to file
        bits: Bit length for code

    Returns:
        Dictionary with instance code
    """
    with open(file_path, "rb") as stream:
        kwargs = {}
        if bits is not None:
            kwargs["bits"] = bits

        result = idk.code_instance(stream, **kwargs)

        if hasattr(result, "dict"):
            return result.dict()
        elif hasattr(result, "model_dump"):
            return result.model_dump()
        else:
            return dict(result)


def generate_semantic_text(file_path, bits):
    # type: (Path, Optional[int]) -> dict
    """
    Generate Semantic-Code-Text from text file.

    Args:
        file_path: Path to text file
        bits: Bit length for code

    Returns:
        Dictionary with semantic text code
    """
    # Read text content
    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    kwargs = {}
    if bits is not None:
        kwargs["bits"] = bits

    result = idk.code_semantic_text(text, **kwargs)

    if hasattr(result, "dict"):
        return result.dict()
    elif hasattr(result, "model_dump"):
        return result.model_dump()
    else:
        return dict(result)


def generate_semantic_image(file_path, bits):
    # type: (Path, Optional[int]) -> dict
    """
    Generate Semantic-Code-Image from image file.

    Args:
        file_path: Path to image file
        bits: Bit length for code

    Returns:
        Dictionary with semantic image code
    """
    fp_str = str(file_path)
    kwargs = {}
    if bits is not None:
        kwargs["bits"] = bits

    result = idk.code_semantic_image(fp_str, **kwargs)

    if hasattr(result, "dict"):
        return result.dict()
    elif hasattr(result, "model_dump"):
        return result.model_dump()
    else:
        return dict(result)


def generate_unit(file_path, unit_type, bits):
    # type: (Path, str, Optional[int]) -> dict
    """
    Generate specified ISCC unit type.

    Args:
        file_path: Path to file
        unit_type: Type of unit to generate
        bits: Bit length for code

    Returns:
        Dictionary with generated unit
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    generators = {
        "meta": generate_meta_code,
        "content": generate_content_code,
        "data": generate_data_code,
        "instance": generate_instance_code,
        "semantic-text": generate_semantic_text,
        "semantic-image": generate_semantic_image,
    }

    generator = generators.get(unit_type)
    if not generator:
        raise ValueError(f"Unknown unit type: {unit_type}")

    try:
        return generator(file_path, bits)
    except Exception as e:
        raise RuntimeError(f"Failed to generate {unit_type} code: {e}") from e


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
        description="Generate individual ISCC units",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Unit types:
  meta            Generate Meta-Code from metadata
  content         Generate Content-Code from content
  data            Generate Data-Code from raw data
  instance        Generate Instance-Code (checksum)
  semantic-text   Generate Semantic-Code-Text
  semantic-image  Generate Semantic-Code-Image

Examples:
  %(prog)s --unit-type meta document.pdf
  %(prog)s --unit-type content --bits 128 image.jpg
  %(prog)s --unit-type semantic-text article.txt
  %(prog)s --unit-type instance --pretty video.mp4
        """,
    )

    parser.add_argument("file", type=Path, help="File to process")

    parser.add_argument(
        "--unit-type",
        required=True,
        choices=[
            "meta",
            "content",
            "data",
            "instance",
            "semantic-text",
            "semantic-image",
        ],
        help="Type of ISCC unit to generate",
    )

    parser.add_argument(
        "--bits",
        type=int,
        choices=[64, 128, 192, 256],
        help="Bit length for ISCC codes (default: 64)",
    )

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    try:
        result = generate_unit(args.file, args.unit_type, args.bits)
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
