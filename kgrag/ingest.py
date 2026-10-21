"""Document ingestion: corpus loading and chunking."""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path

from .models import Chunk, Document

log = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt"}
INDEX_FILENAMES = {"readme.md"}  # root-level corpus index, not content
_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")


def _stable_id(*parts: object) -> str:
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        m = _HEADING_RE.match(line)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return fallback


def load_corpus(path: str | Path) -> list[Document]:
    """Recursively load .md/.markdown/.txt files under `path`, sorted by relative path."""
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError(f"Corpus folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Corpus path is not a folder: {root}")

    docs: list[Document] = []
    for file in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = file.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if len(rel.parts) == 1 and file.name.lower() in INDEX_FILENAMES:
            # A corpus index/README restates facts (even answers) from the real documents,
            # so indexing it pollutes retrieval and citations.
            continue
        if file.suffix.lower() not in SUPPORTED_SUFFIXES:
            log.warning("Skipping unsupported file type: %s", rel.as_posix())
            continue
        # Decode from bytes so newlines are not translated and offsets match the source.
        text = file.read_bytes().decode("utf-8", errors="replace")
        rel_posix = rel.as_posix()
        docs.append(Document(id=_stable_id(rel_posix), path=rel_posix,
                             title=_extract_title(text, file.stem), text=text))
    if not docs:
        raise ValueError(
            f"No supported documents found in {root}. "
            f"Add files with extensions: {', '.join(sorted(SUPPORTED_SUFFIXES))}."
        )
    return docs


def _segments(text: str) -> list[tuple[int, int]]:
    """Paragraph spans (start, end) split on blank lines and heading lines."""
    spans: list[tuple[int, int]] = []
    seg_start: int | None = None
    seg_end = 0
    pos = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        line_start = pos
        pos += len(line)
        if not content.strip():
            if seg_start is not None:
                spans.append((seg_start, seg_end))
                seg_start = None
            continue
        if seg_start is not None and _HEADING_RE.match(content):
            spans.append((seg_start, seg_end))
            seg_start = None
        if seg_start is None:
            seg_start = line_start
        seg_end = line_start + len(content)
    if seg_start is not None:
        spans.append((seg_start, seg_end))
    return spans


def _windows(start: int, end: int, size: int, overlap: int) -> list[tuple[int, int]]:
    step = size - overlap
    out = []
    s = start
    while True:
        e = min(s + size, end)
        out.append((s, e))
        if e >= end:
            return out
        s += step


def chunk_document(doc: Document, size: int = 800, overlap: int = 100) -> list[Chunk]:
    """Split a document into chunks whose text is exactly doc.text[start:end].

    Paragraphs/headings are packed greedily up to `size` characters; a single
    paragraph longer than `size` falls back to overlapping character windows.
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must satisfy 0 <= overlap < size")

    spans: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = None
    for s, e in _segments(doc.text):
        if e - s > size:
            if cur:
                spans.append(cur)
                cur = None
            spans.extend(_windows(s, e, size, overlap))
        elif cur is None:
            cur = (s, e)
        elif e - cur[0] <= size and not _HEADING_RE.match(doc.text[s:e].split("\n", 1)[0]):
            cur = (cur[0], e)
        else:
            spans.append(cur)
            cur = (s, e)
    if cur:
        spans.append(cur)

    return [Chunk(id=_stable_id(doc.id, s, e), doc_id=doc.id, text=doc.text[s:e], start=s, end=e)
            for s, e in spans]
