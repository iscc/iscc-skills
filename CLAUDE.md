# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Claude Code skills for the ISCC (International Standard Content Code) ecosystem. Skills are packaged knowledge modules that extend Claude's capabilities for ISCC-related tasks.

## Current Status

**4 skills implemented:**
- `iscc-brand-guidelines` - Brand colors, typography, logo assets for ISCC visual identity
- `iscc-python-developer` - Python development guidance with ISCC libraries (uses DeepWiki)
- `iscc-standards-expert` - ISO 24138:2024 specification knowledge (uses DeepWiki)
- `iscc-toolkit` - 18 standalone PEP 723 scripts for ISCC operations (uvx-runnable)

**Not yet implemented:**
- `.skill` package files (zip archives for distribution)
- Tests

## Repository Structure

```
iscc-skills/
├── .claude-plugin/marketplace.json  # Plugin metadata for skill distribution
├── skills/                          # Individual skill definitions
│   ├── iscc-brand-guidelines/       # Brand colors, typography, logo assets
│   │   ├── SKILL.md
│   │   └── assets/                  # PNG logos and favicon
│   ├── iscc-python-developer/       # Python development with ISCC libraries
│   │   ├── SKILL.md
│   │   └── references/              # Guidelines and repo documentation
│   ├── iscc-standards-expert/       # ISO 24138:2024 specification knowledge
│   │   └── SKILL.md
│   └── iscc-toolkit/                # Standalone scripts for ISCC operations
│       ├── SKILL.md
│       ├── references/              # Usage guide
│       └── tools/                   # 17 Python scripts (PEP 723)
├── notes/                           # Design reference materials
└── pyproject.toml                   # Project configuration (uv/ruff)
```

## Skill Architecture

Each skill is a directory containing:
- `SKILL.md` - Main skill definition with YAML frontmatter (`name`, `description`) and markdown content
- `references/` - Optional supporting documentation
- `assets/` - Optional binary assets (images, etc.)
- `tools/` - Optional executable scripts (iscc-toolkit only)

## Commands

```bash
# Development environment
uv sync                    # Install dependencies (prek for packaging)
```

## DeepWiki Integration

The iscc-python-developer and iscc-standards-expert skills rely on the DeepWiki MCP server for fetching current documentation from ISCC repositories:

```bash
claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp
```

Key repositories to query:
- `iscc/iscc-core` - Low-level codec, ISO 24138 reference implementation
- `iscc/iscc-sdk` - High-level SDK for ISCC generation
- `iscc/iscc-sct` - Semantic text similarity
- `iscc/iscc-sci` - Semantic image similarity
- `iscc/iscc-ieps` - ISCC Enhancement Proposals (specifications)

## Python Code Style (for ISCC projects)

- Use PEP 484 type comments (first line below function def), not inline annotations
- Use `uv` exclusively for dependency management
- Import aliases: `iscc_sdk as idk`, `iscc_core as ic`, `iscc_sct as sct`
- Use `pathlib.Path` for cross-platform file paths
- Module-level absolute imports only
