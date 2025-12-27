# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is an ISCC (International Standard Content Code) **marketplace** for Claude Code plugins. Each plugin contains a single skill that extends Claude's capabilities for ISCC-related tasks.

## Current Status

**4 plugins (1 skill each):**
- `iscc-brand-guidelines` - Brand colors, typography, logo assets for ISCC visual identity
- `iscc-python-developer` - Python development guidance with ISCC libraries (uses DeepWiki)
- `iscc-standards-expert` - ISO 24138:2024 specification knowledge (uses DeepWiki)
- `iscc-toolkit` - 18 standalone PEP 723 scripts for ISCC operations (uvx-runnable)

## Repository Structure

```
iscc-skills/                              # Marketplace repository
├── .claude-plugin/
│   └── marketplace.json                  # Marketplace manifest (lists all plugins)
│
├── iscc-brand-guidelines/                # Plugin 1
│   ├── .claude-plugin/plugin.json
│   └── skills/iscc-brand-guidelines/
│       ├── SKILL.md
│       └── assets/                       # PNG logos and favicon
│
├── iscc-python-developer/                # Plugin 2
│   ├── .claude-plugin/plugin.json
│   └── skills/iscc-python-developer/
│       ├── SKILL.md
│       └── references/                   # Guidelines and repo documentation
│
├── iscc-standards-expert/                # Plugin 3
│   ├── .claude-plugin/plugin.json
│   └── skills/iscc-standards-expert/
│       └── SKILL.md
│
├── iscc-toolkit/                         # Plugin 4
│   ├── .claude-plugin/plugin.json
│   └── skills/iscc-toolkit/
│       ├── SKILL.md
│       ├── references/                   # Usage guide
│       └── tools/                        # 18 Python scripts (PEP 723)
│
├── notes/                                # Design reference materials
└── pyproject.toml                        # Project configuration (uv/ruff)
```

## Plugin Architecture

Each plugin is a directory containing:
- `.claude-plugin/plugin.json` - Plugin manifest with name, version, description
- `skills/<skill-name>/SKILL.md` - Skill definition with YAML frontmatter
- `skills/<skill-name>/references/` - Optional supporting documentation
- `skills/<skill-name>/assets/` - Optional binary assets (images, etc.)
- `skills/<skill-name>/tools/` - Optional executable scripts

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
