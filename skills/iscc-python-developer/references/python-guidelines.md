# Python & uv Guidelines

## Dependency Management with uv

Use `uv` exclusively for dependency management. Do not use pip, poetry, or easy_install.

### Essential Commands

```bash
# Project setup
uv init myproj && cd myproj
uv add iscc-sdk iscc-core          # Add ISCC dependencies
uv sync --locked                    # Reproducible install

# Running code
uv run python script.py             # Run in project venv
uv run pytest -q                    # Run tests

# Python versions
uv python install 3.12
uv python pin 3.12
```

### Adding ISCC Libraries

```bash
uv add iscc-sdk                     # High-level SDK
uv add iscc-core                    # Low-level codec
uv add iscc-sct                     # Semantic text
uv add iscc-sci                     # Semantic image
uv add iscc-vdb                     # Similarity search
```

## Code Style

### Type Comments (PEP 484 Style)

Use type comments on the first line below function definitions. Do not use inline type annotations in function signatures.

```python
def generate_iscc(file_path, include_meta=True):
    # type: (Path, bool) -> IsccMeta
    """
    Generate ISCC code from a media file.

    :param file_path: Path to the media file.
    :param include_meta: Include metadata in generation.
    :return: ISCC metadata object with generated code.
    """
    pass
```

### Type Annotation Rules

- Use built-in collection types: `list[str]`, `dict[str, int]` (PEP 585)
- Use pipe for unions: `str | None`, `int | float` (PEP 604)
- Exception: Use inline annotations when required by frameworks (FastAPI, Typer)

### Function Design

- Keep functions short and pure
- Minimize function arguments
- No nested functions
- No underscore-prefixed private functions
- Module-level imports only (no local imports)
- Absolute imports only

### Testing

- Use pytest
- Create reusable fixtures in `tests/conftest.py`
- Avoid mocking/monkeypatching - refactor code if needed
- Write Sans I/O code (testable without mocking)
- Tests must run fast
