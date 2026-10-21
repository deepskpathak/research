"""Default configuration. Paths are relative to the working directory."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_CORPUS_DIR = Path("research")
DEFAULT_STORE_DIR = Path(".kgrag")
DEFAULT_CHUNK_SIZE = 800  # characters
DEFAULT_CHUNK_OVERLAP = 100  # characters


@dataclass(frozen=True)
class Config:
    corpus_dir: Path = DEFAULT_CORPUS_DIR
    store_dir: Path = DEFAULT_STORE_DIR
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP

    def __post_init__(self) -> None:
        object.__setattr__(self, "corpus_dir", Path(self.corpus_dir))
        object.__setattr__(self, "store_dir", Path(self.store_dir))
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("chunk_overlap must be in [0, chunk_size)")
