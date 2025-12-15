# ISCC Repository Guide

Detailed guide for selecting the appropriate ISCC repository.

## Core Libraries

### iscc-core
**Purpose**: Official Python reference implementation of ISO 24138:2024

**Use for**:
- Low-level codec operations (encoding/decoding ISCC digests)
- Generating individual ISCC-UNITs
- Binary manipulation and header parsing
- Understanding the standard's algorithms

**Key functions**: `gen_meta_code()`, `gen_data_code()`, `gen_instance_code()`, `gen_text_code()`, `gen_image_code()`, `gen_audio_code()`, `gen_video_code()`

### iscc-sdk
**Purpose**: High-level SDK for practical ISCC integration

**Use for**:
- Generating complete ISCC-CODEs from media files
- Automatic content type detection
- Metadata extraction and embedding
- Content extraction and transformation (OCR, transcription)

**Key functions**: `code_iscc()`, `code_meta()`, `code_content()`, `code_data()`, `code_instance()`

## Semantic Libraries (Experimental)

### iscc-sct
**Purpose**: Semantic Code Text - AI-based text similarity

**Use for**:
- Semantic text similarity (meaning-based, not lexical)
- Granular text features (SIMPRINTS)
- Cross-language similarity detection

**Key functions**: `gen_text_code_semantic()`, `create_features()`, `similarity()`

### iscc-sci
**Purpose**: Semantic Code Image - AI-based image similarity

**Use for**:
- Semantic image similarity
- Visual concept matching
- Image feature extraction

## Infrastructure Libraries

### iscc-vdb
**Purpose**: Multi-index vector database for ISCC similarity search

**Use for**:
- Indexing ISCC codes for similarity search
- Near-duplicate detection at scale
- Building content registries

### iscc-schema
**Purpose**: JSON Schema and JSON-LD contexts

**Use for**:
- Validating ISCC metadata
- Linked data integration
- Metadata interoperability

### iscc-crypto
**Purpose**: Cryptographic primitives

**Use for**:
- Signing ISCC codes
- Timestamping for notarization
- Generating ISCC-IDs

### iscc-web
**Purpose**: REST API service

**Use for**:
- Deploying ISCC generation as a service
- HTTP API integration
- Microservice architecture

### iscc-ieps
**Purpose**: ISCC Enhancement Proposals

**Use for**:
- Understanding ecosystem specifications
- Contributing to ISCC development
- Community-driven features
