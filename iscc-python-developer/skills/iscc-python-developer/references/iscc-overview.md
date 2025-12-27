# ISCC Overview

The **International Standard Content Code (ISCC)** is a content-derived, similarity-preserving identifier for digital media defined by ISO 24138:2024.

## Key Characteristics

- **Content-derived**: Generated from the media asset itself, not assigned
- **Decentralized**: Independent parties derive identical codes from the same asset
- **Similarity-preserving**: Similar content produces similar codes
- **Multi-component**: Combines multiple algorithmic fingerprints

## ISCC Structure

### Components

| Component | Description |
|-----------|-------------|
| **ISCC-HEADER** | 2-byte self-describing header (MainType, SubType, Version, Length) |
| **ISCC-BODY** | Binary payload (similarity hash or fingerprint) |
| **ISCC-DIGEST** | Complete binary representation (HEADER + BODY) |
| **ISCC-UNIT** | Single algorithmic fingerprint (HEADER + single algorithm BODY) |
| **ISCC-CODE** | Composite of multiple ISCC-UNITs (minimum: DATA + INSTANCE) |
| **ISCC-ID** | Globally unique identifier (HEADER + timestamp + server-id) |
| **SIMPRINT** | Headerless base64 similarity hash for content segments |

### ISCC-UNIT Types

| Unit | Encodes | Purpose |
|------|---------|---------|
| **Meta-Code** | Metadata similarity | Lexical/syntactic metadata matching |
| **Semantic-Code** | Conceptual similarity | AI-based semantic understanding |
| **Content-Code** | Perceptual similarity | Modality-specific (text/image/audio/video) |
| **Data-Code** | Raw data similarity | Byte-level data matching |
| **Instance-Code** | Exact data identity | Checksum/hash verification |

## Use Cases

- Content deduplication and database synchronization
- Integrity verification and timestamping
- Version tracking and data provenance
- Similarity clustering and anomaly detection
- Royalty allocation and usage tracking
- Fact-checking and digital asset management
