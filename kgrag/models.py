"""Shared data model. All types are frozen and JSON-serialisable via to_dict/from_dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Document:
    id: str
    path: str
    title: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "path": self.path, "title": self.title, "text": self.text}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Document":
        return cls(id=d["id"], path=d["path"], title=d["title"], text=d["text"])


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    text: str
    start: int  # character offsets into Document.text, end exclusive
    end: int

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "doc_id": self.doc_id, "text": self.text,
                "start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Chunk":
        return cls(id=d["id"], doc_id=d["doc_id"], text=d["text"],
                   start=int(d["start"]), end=int(d["end"]))


@dataclass(frozen=True)
class Entity:
    id: str
    name: str
    type: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    mentions: tuple[str, ...] = field(default_factory=tuple)  # chunk ids

    def __post_init__(self) -> None:
        # Normalise lists to tuples so instances stay hashable and truly immutable.
        object.__setattr__(self, "aliases", tuple(self.aliases))
        object.__setattr__(self, "mentions", tuple(self.mentions))

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "type": self.type,
                "aliases": list(self.aliases), "mentions": list(self.mentions)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Entity":
        return cls(id=d["id"], name=d["name"], type=d["type"],
                   aliases=tuple(d.get("aliases", ())), mentions=tuple(d.get("mentions", ())))


@dataclass(frozen=True)
class Relation:
    source_id: str
    target_id: str
    type: str
    evidence_chunk_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence_chunk_ids", tuple(self.evidence_chunk_ids))

    def to_dict(self) -> dict[str, Any]:
        return {"source_id": self.source_id, "target_id": self.target_id,
                "type": self.type, "evidence_chunk_ids": list(self.evidence_chunk_ids)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Relation":
        return cls(source_id=d["source_id"], target_id=d["target_id"], type=d["type"],
                   evidence_chunk_ids=tuple(d.get("evidence_chunk_ids", ())))
