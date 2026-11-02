from dataclasses import dataclass

@dataclass(frozen=True)
class DocumentChunk:
    source: str
    chunk_index: int
    text: str


@dataclass(frozen=True)
class RetrievedChunk:
    source: str
    chunk_index: int
    text: str
    score: float | None = None