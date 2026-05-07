from dataclasses import dataclass


@dataclass
class DocumentChunk:
    doc_id: str
    chunk_id: str
    text: str
    source: str | None = None
