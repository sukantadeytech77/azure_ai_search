from dataclasses import dataclass
from typing import List


@dataclass
class SemanticDocumentChunk:
    id: str
    document_id: str
    content: str
    tags: List[str]

    def to_azure_document(self) -> dict:
        """Convert the document chunk to Azure Search format."""
        return {
            "id": self.id,
            "documentid": self.document_id,
            "content": self.content,
            "tags": self.tags,
            "embeddings": self.embeddings
        }

    @classmethod
    def create_chunk(
        cls,
        document_id: str,
        chunk_index: int,
        content: str,
        tags: List[str]
    ) -> 'SemanticDocumentChunk':
        """Create a semantic document chunk with the standard ID format."""
        chunk_id = f"{document_id}_chunk{chunk_index}"
        return cls(
            id=chunk_id,
            document_id=document_id,
            content=content,
            tags=tags
        )
