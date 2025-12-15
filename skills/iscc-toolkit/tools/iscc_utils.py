# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
ISCC Toolkit Shared Utilities

Common functions used across multiple ISCC toolkit scripts.
"""

import json
import sys
from pathlib import Path


def format_output(data, pretty=False):
    # type: (dict, bool) -> str
    """
    Format output as JSON.

    Args:
        data: Data to format
        pretty: If True, format with indentation

    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def read_input(input_path):
    # type: (str | None) -> dict
    """
    Read JSON input from file or stdin.

    Args:
        input_path: Path to input file or '-' for stdin

    Returns:
        Parsed JSON data

    Raises:
        ValueError: If JSON is invalid
        FileNotFoundError: If input file doesn't exist
    """
    if input_path is None or input_path == "-":
        # Read from stdin
        try:
            data = json.load(sys.stdin)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from stdin: {e}") from e
    else:
        # Read from file
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in file {input_path}: {e}") from e
