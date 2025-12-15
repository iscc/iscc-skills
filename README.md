# ISCC Skills

> **Status: Experimental** - This project is under active development. APIs and skill definitions may change without notice.

Claude Code skills for the [ISCC (International Standard Content Code)](https://iscc.io) ecosystem. Skills are packaged knowledge modules that extend Claude's capabilities for ISCC-related tasks.

## Available Skills

| Skill | Description |
|-------|-------------|
| **iscc-brand-guidelines** | ISCC brand colors, typography, and logo assets for consistent visual styling |
| **iscc-python-developer** | Python development guide for ISCC libraries (iscc-core, iscc-sdk, iscc-sct, iscc-sci) |
| **iscc-standards-expert** | ISO 24138:2024 specification knowledge and ISCC Enhancement Proposals (IEPs) |
| **iscc-toolkit** | 17 standalone Python scripts (PEP 723) for ISCC operations, runnable with `uvx` |

## Prerequisites

The `iscc-python-developer` and `iscc-standards-expert` skills require the DeepWiki MCP server for fetching current documentation:

```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

## Installation

Add the skills plugin to Claude Code:

```bash
claude plugins add https://github.com/iscc/iscc-skills
```

Or install from a local clone:

```bash
git clone https://github.com/iscc/iscc-skills.git
claude plugins add ./iscc-skills
```

## Usage

Once installed, the skills are automatically activated when relevant. You can also invoke them explicitly:

- Ask about ISCC specifications → triggers `iscc-standards-expert`
- Write Python code with ISCC libraries → triggers `iscc-python-developer`
- Apply ISCC branding to artifacts → triggers `iscc-brand-guidelines`

## Development

```bash
# Install dependencies
uv sync

# Run main entry point
uv run python main.py

# Run tests
uv run pytest -q
```

## Skill Structure

Each skill is a directory containing:

```
skills/<skill-name>/
├── SKILL.md           # Main skill definition with YAML frontmatter
├── references/        # Optional supporting documentation
└── assets/            # Optional binary assets (images, etc.)
```

## Related Projects

- [iscc-core](https://github.com/iscc/iscc-core) - Low-level codec, ISO 24138 reference implementation
- [iscc-sdk](https://github.com/iscc/iscc-sdk) - High-level SDK for ISCC generation
- [iscc-ieps](https://github.com/iscc/iscc-ieps) - ISCC Enhancement Proposals (specifications)

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
