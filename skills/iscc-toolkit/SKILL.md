---
name: iscc-toolkit
description: Collection of standalone Python scripts (PEP 723) for common ISCC operations. Run any tool with `uvx` for content identification, similarity comparison, metadata handling, cryptographic signing, and API integration. Use when users need to generate ISCC codes, compare content similarity, extract/embed metadata, sign declarations, or search the ISCC registry.
---

# ISCC Toolkit

A collection of **17 standalone Python scripts** for common ISCC (International Standard Content Code) operations. Each script uses PEP 723 inline metadata and runs directly with `uvx` without installation.

## Quick Start

```bash
# Generate ISCC code from any media file
uvx iscc_generate.py image.jpg

# Compare two ISCC codes for similarity
uvx iscc_compare.py ISCC:KACYPXW445FTYNJ3 ISCC:KACYPXW445FTYNJ4

# Inspect ISCC code structure
uvx iscc_inspect.py ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY

# Extract metadata from media
uvx iscc_metadata_extract.py document.pdf

# Generate keypair for signing
uvx iscc_keypair.py --generate
```

## Tool Categories

### Generation Tools

| Tool | Description |
|------|-------------|
| `iscc_generate.py` | Generate complete ISCC-CODE for any media file |
| `iscc_units.py` | Generate individual ISCC-UNITs (Meta, Content, Data, Instance) |
| `iscc_batch.py` | Batch process directories with parallel execution |
| `iscc_thumbnail.py` | Generate thumbnails from media files |

### Analysis Tools

| Tool | Description |
|------|-------------|
| `iscc_compare.py` | Compare ISCCs for similarity (unit-by-unit) |
| `iscc_inspect.py` | Decompose and inspect ISCC-CODE structure |
| `iscc_validate.py` | Validate ISCC format and structure |
| `iscc_distance.py` | Calculate Hamming distance between ISCCs |
| `iscc_normalize.py` | Normalize text for ISCC processing |

### Metadata Tools

| Tool | Description |
|------|-------------|
| `iscc_metadata_extract.py` | Extract metadata from media files |
| `iscc_metadata_embed.py` | Embed ISCC metadata into media files |
| `iscc_detect.py` | Detect media type and ISCC processing mode |

### Cryptography Tools

| Tool | Description |
|------|-------------|
| `iscc_keypair.py` | Create and manage Ed25519 keypairs |
| `iscc_sign.py` | Sign ISCC notes/declarations |
| `iscc_verify.py` | Verify signatures on ISCC notes |

### API Integration Tools

| Tool | Description |
|------|-------------|
| `iscc_declare.py` | Declare ISCC via ISCC-HUB API |
| `iscc_search.py` | Search ISCC registry via API |

## Output Format

All tools output **JSON by default** for programmatic use. Add `--pretty` for human-readable formatted output:

```bash
# Compact JSON (default)
uvx iscc_generate.py image.jpg
{"iscc": "ISCC:...", "name": "image.jpg", ...}

# Pretty-printed JSON
uvx iscc_generate.py image.jpg --pretty
{
  "iscc": "ISCC:...",
  "name": "image.jpg",
  ...
}
```

## Tool Reference

### iscc_generate.py

Generate complete ISCC-CODE for any media file (text, image, audio, video).

```bash
uvx iscc_generate.py <file> [options]

Options:
  --bits N        Bit length for hash components (default: 64)
  --granular      Include granular features in output
  --meta-only     Generate only Meta-Code (skip content processing)
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_generate.py photo.jpg --pretty
```

### iscc_units.py

Generate specific ISCC units individually.

```bash
uvx iscc_units.py <file> --unit-type <type> [options]

Unit Types:
  meta            Meta-Code from filename/metadata
  content         Content-Code (text/image/audio/video)
  data            Data-Code from file content
  instance        Instance-Code from binary data
  semantic-text   Semantic Text-Code (requires iscc-sct)
  semantic-image  Semantic Image-Code (requires iscc-sci)

Options:
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_units.py document.pdf --unit-type content
```

### iscc_batch.py

Process multiple files in a directory with parallel execution.

```bash
uvx iscc_batch.py <directory> [options]

Options:
  --output FILE   Output file (default: stdout)
  --workers N     Number of parallel workers (default: CPU count)
  --recursive     Process subdirectories recursively
  --force         Reprocess files with existing .iscc.json sidecars
  --format FMT    Output format: json, jsonl, csv (default: json)
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_batch.py ./media --recursive --format jsonl --output results.jsonl
```

### iscc_thumbnail.py

Generate thumbnail images from media files.

```bash
uvx iscc_thumbnail.py <file> [options]

Options:
  --size WxH      Thumbnail size (default: 128x128)
  --format FMT    Output format: webp, jpeg, png (default: webp)
  --quality N     Compression quality 1-100 (default: 80)
  --output FILE   Save to file (default: output as data URL)
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_thumbnail.py video.mp4 --size 256x256 --output thumb.webp
```

### iscc_compare.py

Compare two ISCC codes and calculate similarity.

```bash
uvx iscc_compare.py <iscc1> <iscc2> [options]

Options:
  --pretty        Pretty-print JSON output
```

**Output includes:**
- Overall similarity percentage
- Unit-by-unit comparison (Meta, Content, Data, Instance)
- Hamming distances for each matching unit

**Example:**
```bash
uvx iscc_compare.py "ISCC:KACYPXW445FTYNJ3" "ISCC:KACYPXW445FTYNJ4" --pretty
```

### iscc_inspect.py

Decompose and inspect ISCC-CODE structure.

```bash
uvx iscc_inspect.py <iscc> [options]

Options:
  --pretty        Pretty-print JSON output
```

**Output includes:**
- Individual units with their types
- Human-readable explanation (maintype, subtype, version, length)
- Binary and hexadecimal representations

**Example:**
```bash
uvx iscc_inspect.py "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"
```

### iscc_validate.py

Validate ISCC format and structure.

```bash
uvx iscc_validate.py <iscc> [options]

Options:
  --strict        Enable strict validation mode
  --schema FILE   Validate against IsccMeta JSON schema
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_validate.py "ISCC:KACYPXW445FTYNJ3" --strict
```

### iscc_distance.py

Calculate Hamming distance between ISCC codes.

```bash
uvx iscc_distance.py <iscc1> <iscc2> [options]
uvx iscc_distance.py <iscc> --batch <file> [options]

Options:
  --threshold N   Similarity threshold percentage (default: 70)
  --batch FILE    Compare against multiple ISCCs from file
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_distance.py "ISCC:KACYPXW445FTYNJ3" "ISCC:KACYPXW445FTYNJ4"
```

### iscc_normalize.py

Apply ISCC text normalization.

```bash
uvx iscc_normalize.py [options]

Options:
  --input FILE    Input file (default: stdin)
  --output FILE   Output file (default: stdout)
  --ngrams        Show 13-character n-grams
  --stats         Show character/byte statistics
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
echo "Hello World!" | uvx iscc_normalize.py --stats
```

### iscc_metadata_extract.py

Extract metadata from media files.

```bash
uvx iscc_metadata_extract.py <file> [<file>...] [options]

Options:
  --pretty        Pretty-print JSON output
```

**Supported formats:** PDF, EPUB, DOCX, images (JPEG, PNG, WebP), audio (MP3, FLAC, OGG), video (MP4, MKV, WebM)

**Example:**
```bash
uvx iscc_metadata_extract.py document.pdf image.jpg --pretty
```

### iscc_metadata_embed.py

Embed ISCC metadata into media files.

```bash
uvx iscc_metadata_embed.py --file <media> --metadata <json> [options]

Options:
  --file FILE       Media file to embed metadata into
  --metadata FILE   JSON metadata file (or '-' for stdin)
  --output FILE     Output file (default: modify in place)
  --pretty          Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_metadata_embed.py --file document.pdf --metadata iscc.json --output document_tagged.pdf
```

### iscc_detect.py

Detect media type and ISCC processing mode.

```bash
uvx iscc_detect.py <file> [options]

Options:
  --verbose       Show detailed detection information
  --pretty        Pretty-print JSON output
```

**Output includes:**
- MIME type
- ISCC processing mode (text, image, audio, video)
- File size
- Whether file type is supported

**Example:**
```bash
uvx iscc_detect.py unknown_file --verbose
```

### iscc_keypair.py

Create and manage Ed25519 keypairs for signing.

```bash
uvx iscc_keypair.py [options]

Options:
  --generate          Generate new keypair
  --show              Display existing keypair info
  --controller DID    Set DID controller for new keypair
  --key-id ID         Key identifier for storage
  --pretty            Pretty-print JSON output
```

**Example:**
```bash
# Generate new keypair
uvx iscc_keypair.py --generate --controller "did:web:example.com"

# Show existing keypair
uvx iscc_keypair.py --show
```

### iscc_sign.py

Sign ISCC notes and declarations.

```bash
uvx iscc_sign.py [options]

Options:
  --input FILE    JSON input file (default: stdin)
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_generate.py image.jpg | uvx iscc_sign.py --pretty
```

### iscc_verify.py

Verify signatures on ISCC notes.

```bash
uvx iscc_verify.py [options]

Options:
  --input FILE    Signed JSON input file (default: stdin)
  --pretty        Pretty-print JSON output
```

**Example:**
```bash
cat signed_iscc.json | uvx iscc_verify.py --pretty
```

### iscc_declare.py

Declare ISCC via ISCC-HUB API.

```bash
uvx iscc_declare.py <iscc_code> [options]

Options:
  --datahash HASH   Data hash for declaration
  --force           Override duplicate detection
  --api-url URL     Custom API endpoint (default: https://sb0.iscc.id)
  --pretty          Pretty-print JSON output
```

**Example:**
```bash
uvx iscc_declare.py "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY"
```

### iscc_search.py

Search ISCC registry via API.

```bash
uvx iscc_search.py <query> [options]

Options:
  --type TYPE       Query type: code, id, text (default: auto-detect)
  --index URL       Index URL (default: https://sb0.iscc.id)
  --limit N         Maximum results (default: 10)
  --threshold N     Similarity threshold percentage (default: 70)
  --pretty          Pretty-print JSON output
```

**Example:**
```bash
# Search by ISCC code
uvx iscc_search.py "ISCC:KACYPXW445FTYNJ3"

# Semantic text search
uvx iscc_search.py "machine learning tutorial" --type text --limit 20
```

## Workflow Examples

### Content Identification Pipeline

```bash
# 1. Detect media type
uvx iscc_detect.py myfile.unknown --verbose

# 2. Generate ISCC code
uvx iscc_generate.py myfile.jpg --pretty > iscc.json

# 3. Sign the declaration
cat iscc.json | uvx iscc_sign.py > signed.json

# 4. Declare on registry
uvx iscc_declare.py $(jq -r .iscc iscc.json)
```

### Batch Processing with Deduplication

```bash
# Process directory and output as JSONL
uvx iscc_batch.py ./media --recursive --format jsonl > all_isccs.jsonl

# Compare new file against existing
uvx iscc_distance.py "ISCC:NEW..." --batch all_isccs.jsonl --threshold 80
```

### Similarity Analysis

```bash
# Generate ISCCs for two files
ISCC1=$(uvx iscc_generate.py file1.pdf | jq -r .iscc)
ISCC2=$(uvx iscc_generate.py file2.pdf | jq -r .iscc)

# Compare similarity
uvx iscc_compare.py "$ISCC1" "$ISCC2" --pretty
```

## Dependencies

| Tools | Primary Package |
|-------|-----------------|
| iscc_generate, iscc_units, iscc_batch, iscc_thumbnail, iscc_metadata_*, iscc_detect | `iscc-sdk>=0.7.0` |
| iscc_compare, iscc_inspect, iscc_validate, iscc_distance, iscc_normalize | `iscc-core>=1.0.0` |
| iscc_keypair, iscc_sign, iscc_verify | `iscc-crypto>=0.3.0` |
| iscc_declare, iscc_search | `httpx>=0.27.0` |

## Resources

- **[references/script-usage-guide.md](references/script-usage-guide.md)** - Extended usage examples and patterns
- **[ISCC Documentation](https://iscc.codes)** - Official ISCC documentation
- **[ISCC-HUB API](https://sb0.iscc.id/docs)** - Declaration and search API documentation
