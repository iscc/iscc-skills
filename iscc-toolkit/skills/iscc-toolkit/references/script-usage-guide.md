# ISCC Toolkit Script Usage Guide

Extended usage examples and patterns for the ISCC Toolkit scripts.

## Running Scripts

All scripts use PEP 723 inline metadata and can be run directly with `uvx`:

```bash
# Run from the tools directory
uvx tools/iscc_generate.py image.jpg

# Or copy script anywhere and run
uvx /path/to/iscc_generate.py image.jpg
```

## Common Patterns

### JSON Output Processing

All tools output JSON by default. Use `jq` for processing:

```bash
# Extract just the ISCC code
uvx iscc_generate.py image.jpg | jq -r '.iscc'

# Get thumbnail as data URL
uvx iscc_generate.py image.jpg | jq -r '.thumbnail'

# Filter batch results by mode
uvx iscc_batch.py ./media --format jsonl | jq 'select(.mode == "image")'
```

### Piping Between Tools

Tools support stdin/stdout for chaining:

```bash
# Generate, sign, and declare in one pipeline
uvx iscc_generate.py image.jpg | uvx iscc_sign.py | uvx iscc_declare.py -

# Extract metadata and embed into copy
uvx iscc_metadata_extract.py original.pdf > meta.json
uvx iscc_metadata_embed.py --file copy.pdf --metadata meta.json
```

### Error Handling

Scripts use standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Invalid arguments

```bash
# Check if file is supported
if uvx iscc_detect.py myfile 2>/dev/null | jq -e '.supported' > /dev/null; then
    uvx iscc_generate.py myfile
else
    echo "Unsupported file type"
fi
```

## Generation Workflows

### Basic ISCC Generation

```bash
# Single file
uvx iscc_generate.py document.pdf --pretty

# With granular features (for similarity search)
uvx iscc_generate.py document.pdf --granular > doc_with_features.json
```

### Unit-by-Unit Generation

```bash
# Generate only Meta-Code (fast, from filename/metadata only)
uvx iscc_units.py document.pdf --unit-type meta

# Generate Content-Code (content-based fingerprint)
uvx iscc_units.py document.pdf --unit-type content

# Generate Data-Code (file content hash)
uvx iscc_units.py document.pdf --unit-type data

# Generate Instance-Code (exact file identifier)
uvx iscc_units.py document.pdf --unit-type instance

# Semantic codes (require additional models)
uvx iscc_units.py article.txt --unit-type semantic-text
uvx iscc_units.py photo.jpg --unit-type semantic-image
```

### Batch Processing

```bash
# Process entire directory
uvx iscc_batch.py ./documents --recursive --output results.json

# Parallel processing with 8 workers
uvx iscc_batch.py ./media --workers 8 --format jsonl

# Skip already processed files (detects .iscc.json sidecars)
uvx iscc_batch.py ./archive --recursive

# Force reprocessing
uvx iscc_batch.py ./archive --recursive --force

# CSV output for spreadsheet import
uvx iscc_batch.py ./images --format csv --output catalog.csv
```

### Thumbnail Generation

```bash
# Generate thumbnail as data URL
uvx iscc_thumbnail.py video.mp4

# Save as file with specific format
uvx iscc_thumbnail.py document.pdf --output thumb.webp --format webp

# Custom size and quality
uvx iscc_thumbnail.py image.jpg --size 256x256 --quality 90 --format jpeg
```

## Analysis Workflows

### Comparing Content

```bash
# Direct comparison
uvx iscc_compare.py "ISCC:KACYPXW445FTYNJ3..." "ISCC:KACYPXW445FTYNJ4..."

# Compare files by generating ISCCs first
ISCC1=$(uvx iscc_generate.py file1.pdf | jq -r .iscc)
ISCC2=$(uvx iscc_generate.py file2.pdf | jq -r .iscc)
uvx iscc_compare.py "$ISCC1" "$ISCC2" --pretty
```

### Batch Similarity Search

```bash
# Create reference database
uvx iscc_batch.py ./reference --format jsonl > reference.jsonl

# Compare new file against reference
NEW_ISCC=$(uvx iscc_generate.py new_file.pdf | jq -r .iscc)
uvx iscc_distance.py "$NEW_ISCC" --batch reference.jsonl --threshold 80
```

### Inspecting ISCC Structure

```bash
# Full decomposition
uvx iscc_inspect.py "ISCC:KACYPXW445FTYNJ3CYSXHAFJMA2HUWULUNRFE3BLHRSCXYH2M5AEGQY" --pretty

# Output shows:
# - Individual units (Meta, Content, Data, Instance)
# - Unit types (maintype, subtype)
# - Binary representation
# - Hex representation
```

### Validation

```bash
# Basic validation
uvx iscc_validate.py "ISCC:KACYPXW445FTYNJ3"

# Strict mode (checks all constraints)
uvx iscc_validate.py "ISCC:KACYPXW445FTYNJ3" --strict

# Validate full IsccMeta JSON against schema
uvx iscc_generate.py image.jpg > meta.json
uvx iscc_validate.py --schema meta.json
```

### Text Normalization

```bash
# Normalize text from stdin
echo "Hello, World! 123" | uvx iscc_normalize.py

# With statistics
cat article.txt | uvx iscc_normalize.py --stats

# Show n-grams (useful for debugging similarity)
cat article.txt | uvx iscc_normalize.py --ngrams

# Process file to file
uvx iscc_normalize.py --input raw.txt --output normalized.txt
```

## Metadata Workflows

### Extracting Metadata

```bash
# Single file
uvx iscc_metadata_extract.py document.pdf --pretty

# Multiple files
uvx iscc_metadata_extract.py *.jpg --pretty

# Combine with jq for specific fields
uvx iscc_metadata_extract.py image.jpg | jq '{title: .name, created: .created}'
```

### Embedding Metadata

```bash
# Embed from JSON file
uvx iscc_metadata_embed.py --file document.pdf --metadata iscc.json --output tagged.pdf

# Embed from pipeline
uvx iscc_generate.py document.pdf | uvx iscc_metadata_embed.py --file document.pdf --metadata - --output tagged.pdf
```

### Media Type Detection

```bash
# Basic detection
uvx iscc_detect.py unknown_file

# Verbose output with all details
uvx iscc_detect.py unknown_file --verbose --pretty

# Check if supported
uvx iscc_detect.py myfile | jq '.supported'
```

## Cryptographic Workflows

### Key Management

```bash
# Generate new keypair (stored in platform keychain)
uvx iscc_keypair.py --generate

# Generate with DID controller
uvx iscc_keypair.py --generate --controller "did:web:example.com"

# Generate with custom key ID
uvx iscc_keypair.py --generate --key-id "my-signing-key"

# Show existing keypair info
uvx iscc_keypair.py --show --pretty
```

### Signing Declarations

```bash
# Sign from stdin
uvx iscc_generate.py image.jpg | uvx iscc_sign.py > signed.json

# Sign from file
uvx iscc_sign.py --input iscc.json > signed.json
```

### Verifying Signatures

```bash
# Verify from stdin
cat signed.json | uvx iscc_verify.py

# Verify from file
uvx iscc_verify.py --input signed.json --pretty

# Check verification result
if uvx iscc_verify.py --input signed.json | jq -e '.valid' > /dev/null; then
    echo "Signature valid"
else
    echo "Signature invalid"
fi
```

## API Integration Workflows

### Declaring ISCCs

```bash
# Basic declaration
uvx iscc_declare.py "ISCC:KACYPXW445FTYNJ3..."

# With data hash
uvx iscc_declare.py "ISCC:KACYPXW445FTYNJ3..." --datahash "1220..."

# Force declare (override duplicate check)
uvx iscc_declare.py "ISCC:KACYPXW445FTYNJ3..." --force

# Use custom API endpoint
uvx iscc_declare.py "ISCC:KACYPXW445FTYNJ3..." --api-url "https://custom.iscc.id"
```

### Searching the Registry

```bash
# Search by ISCC code
uvx iscc_search.py "ISCC:KACYPXW445FTYNJ3..."

# Search by ISCC-ID
uvx iscc_search.py "ISCC:MEAJU4A..."

# Semantic text search
uvx iscc_search.py "machine learning tutorial" --type text

# With options
uvx iscc_search.py "ISCC:..." --limit 20 --threshold 80 --pretty
```

## Complete Pipeline Examples

### Content Registration Pipeline

```bash
#!/bin/bash
# register_content.sh - Register content on ISCC registry

FILE="$1"

# 1. Check if file type is supported
if ! uvx iscc_detect.py "$FILE" | jq -e '.supported' > /dev/null; then
    echo "Error: Unsupported file type"
    exit 1
fi

# 2. Generate ISCC code with metadata
ISCC_JSON=$(uvx iscc_generate.py "$FILE" --granular)
ISCC_CODE=$(echo "$ISCC_JSON" | jq -r '.iscc')

echo "Generated ISCC: $ISCC_CODE"

# 3. Sign the declaration
SIGNED_JSON=$(echo "$ISCC_JSON" | uvx iscc_sign.py)

# 4. Declare on registry
RESULT=$(uvx iscc_declare.py "$ISCC_CODE")

echo "Declaration result:"
echo "$RESULT" | jq .
```

### Deduplication Check

```bash
#!/bin/bash
# check_duplicate.sh - Check if content already exists

FILE="$1"
THRESHOLD="${2:-80}"

# Generate ISCC
ISCC=$(uvx iscc_generate.py "$FILE" | jq -r '.iscc')

# Search registry
MATCHES=$(uvx iscc_search.py "$ISCC" --threshold "$THRESHOLD")

if echo "$MATCHES" | jq -e '.results | length > 0' > /dev/null; then
    echo "Potential duplicates found:"
    echo "$MATCHES" | jq '.results[] | {iscc, similarity}'
else
    echo "No duplicates found"
fi
```

### Batch Catalog Generation

```bash
#!/bin/bash
# catalog.sh - Generate content catalog

DIR="$1"
OUTPUT="${2:-catalog.json}"

echo "Processing directory: $DIR"

# Generate ISCCs with progress
uvx iscc_batch.py "$DIR" \
    --recursive \
    --workers 4 \
    --format json \
    --output "$OUTPUT"

# Summary
COUNT=$(jq '. | length' "$OUTPUT")
echo "Processed $COUNT files"
echo "Results saved to $OUTPUT"
```

## Environment Variables

Some tools support configuration via environment variables:

```bash
# Set default API endpoint
export ISCC_API_URL="https://sb0.iscc.id"

# Set keypair from environment (for CI/CD)
export ISCC_PRIVATE_KEY="base64-encoded-key"
```

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
# Ensure uv is installed
pip install uv

# Or use pipx
pipx install uv
```

**"Unsupported file type" errors:**
```bash
# Check what's detected
uvx iscc_detect.py myfile --verbose

# ISCC supports: text, image, audio, video
# Specific formats depend on iscc-sdk installation
```

**"Key not found" errors:**
```bash
# Generate keypair first
uvx iscc_keypair.py --generate

# Or check existing
uvx iscc_keypair.py --show
```

**Slow processing:**
```bash
# Use batch tool with parallel workers
uvx iscc_batch.py ./media --workers 8

# Or generate only specific units
uvx iscc_units.py large_video.mp4 --unit-type data
```
