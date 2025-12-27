#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27.0"]
# ///
"""
ISCC Search Tool

Search the ISCC registry by ISCC code, ISCC-ID, or text content.
Supports exact lookup and semantic text similarity search.
"""

import argparse
import asyncio
import json
import sys

import httpx

DEFAULT_INDEX_URL = "https://sb0.iscc.id"
PRODUCTION_INDEX_URL = "https://index.iscc.id"


def detect_query_type(query):
    # type: (str) -> str
    """
    Auto-detect query type based on format.

    Args:
        query: Search query string

    Returns:
        Query type: 'code', 'id', or 'text'
    """
    query_upper = query.upper()

    # Check for ISCC code format (starts with ISCC:)
    if query_upper.startswith("ISCC:"):
        return "code"

    # Check for ISCC-ID format (starts with ISCC and is hex-like)
    if query_upper.startswith("ISCC") and len(query) >= 16:
        # Simple heuristic: if mostly hex chars after ISCC prefix
        hex_part = query[4:].replace("-", "")
        if all(c in "0123456789ABCDEF" for c in hex_part.upper()):
            return "id"

    # Default to text search
    return "text"


async def lookup_exact(query, index_url, query_type):
    # type: (str, str, str) -> dict
    """
    Perform exact lookup by ISCC code or ISCC-ID.

    Args:
        query: ISCC code or ISCC-ID
        index_url: Base URL of index
        query_type: 'code' or 'id'

    Returns:
        API response as dictionary
    """
    # Construct lookup URL
    lookup_url = f"{index_url}/lookup/{query}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(lookup_url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"results": [], "message": "No matches found"}
            # Try to extract error message
            try:
                error_data = e.response.json()
                error_msg = error_data.get("detail", str(e))
            except Exception:
                error_msg = str(e)
            raise RuntimeError(f"API error: {error_msg}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Request failed: {e}") from e


async def search_text(query, index_url, limit, threshold):
    # type: (str, str, int, Optional[float]) -> dict
    """
    Perform semantic text search.

    Args:
        query: Text to search for
        index_url: Base URL of index
        limit: Maximum number of results
        threshold: Similarity threshold (0-100)

    Returns:
        API response as dictionary
    """
    search_url = f"{index_url}/search"

    # Build request body
    request_body = {
        "text": query,
        "limit": limit,
    }

    if threshold is not None:
        request_body["threshold"] = threshold

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(search_url, json=request_body)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Try to extract error message
            try:
                error_data = e.response.json()
                error_msg = error_data.get("detail", str(e))
            except Exception:
                error_msg = str(e)
            raise RuntimeError(f"API error: {error_msg}") from e
        except httpx.RequestError as e:
            raise RuntimeError(f"Request failed: {e}") from e


async def search_iscc(query, index_url, limit, threshold, query_type):
    # type: (str, str, int, Optional[float], Optional[str]) -> dict
    """
    Search ISCC registry.

    Args:
        query: Search query (code, ID, or text)
        index_url: Base URL of index
        limit: Maximum number of results
        threshold: Similarity threshold for text search
        query_type: Force specific query type or auto-detect

    Returns:
        API response as dictionary
    """
    # Auto-detect query type if not specified
    if query_type is None:
        query_type = detect_query_type(query)

    # Route to appropriate search method
    if query_type in ("code", "id"):
        return await lookup_exact(query, index_url, query_type)
    elif query_type == "text":
        return await search_text(query, index_url, limit, threshold)
    else:
        raise ValueError(f"Invalid query type: {query_type}")


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
        description="Search ISCC registry by code, ID, or text content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search by ISCC code (auto-detected)
  %(prog)s ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY

  # Search by ISCC-ID (auto-detected)
  %(prog)s ISCC4ABCDEF1234567890

  # Semantic text search (auto-detected)
  %(prog)s "climate change and renewable energy"

  # Force query type
  %(prog)s --type text "ISCC:SOMETHING"

  # Use production index
  %(prog)s --index https://index.iscc.id "search query"

  # Limit results and set threshold
  %(prog)s --limit 5 --threshold 85 "machine learning algorithms"
        """,
    )

    parser.add_argument("query", help="Search query (ISCC code, ISCC-ID, or text)")

    parser.add_argument(
        "--index",
        default=DEFAULT_INDEX_URL,
        help=f"Index URL (default: {DEFAULT_INDEX_URL})",
    )

    parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of results (default: 10)"
    )

    parser.add_argument(
        "--threshold", type=float, help="Similarity threshold for text search (0-100)"
    )

    parser.add_argument(
        "--type",
        choices=["code", "id", "text"],
        help="Force specific query type (default: auto-detect)",
    )

    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")

    args = parser.parse_args()

    # Validate threshold if provided
    if args.threshold is not None:
        if not 0 <= args.threshold <= 100:
            print("Error: Threshold must be between 0 and 100", file=sys.stderr)
            return 1

    try:
        # Run async search
        result = asyncio.run(
            search_iscc(args.query, args.index, args.limit, args.threshold, args.type)
        )

        # Output result
        print(format_output(result, args.pretty))
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
