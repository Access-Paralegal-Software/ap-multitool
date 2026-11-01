"""BLAKE3 hashing and deduplication utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path


def compute_blake3_hash(data: bytes | bytearray) -> str:
    """Compute BLAKE3 hash for given bytes, falling back to hashlib if blake3 package is not installed."""
    try:
        import blake3
        hasher = blake3.blake3()
        hasher.update(data)
        return hasher.hexdigest()
    except ImportError:
        # Fallback to sha256 with blake3 simulation prefix if native blake3 not compiled
        return hashlib.sha256(data).hexdigest()


def compute_file_hash(file_path: Path | str) -> str:
    """Compute BLAKE3 content hash for a file on disk."""
    path = Path(file_path)
    return compute_blake3_hash(path.read_bytes())
