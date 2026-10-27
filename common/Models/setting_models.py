from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LoggingSettings:
    dir: Path
    file: str
    audit_file: str
    level: str
    console: bool
    max_bytes: int
    backup_count: int


@dataclass(frozen=True)
class EmbeddingSettings:
    model: str
    dimensions: int
    tokenizer_encoding: str
    chunk_size: int
    batch_size: int


@dataclass(frozen=True)
class PineconeSettings:
    index_name: str
    namespace: str


@dataclass(frozen=True)
class RagSettings:
    resources_dir: Path
    embedding: EmbeddingSettings
    pinecone: PineconeSettings


@dataclass(frozen=True)
class LlmSettings:
    model: str
    top_k: int


@dataclass(frozen=True)
class WebSettings:
    host: str
    port: int