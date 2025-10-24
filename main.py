"""
Main script for document processing and indexing pipeline.
Handles document upload, processing, and search index updates.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from upload_service.blob_uploader import upload_to_blob
from document_processor.chunker import TextChunker
from document_processor.embedder import Embedder
from document_search.azure_uploader import upload_to_azure, delete_all_files
from models.document import DocumentChunk


@dataclass
class PipelineConfig:
    """Configuration for the document processing pipeline."""
    search_endpoint: str
    container_name: str
    connection_string: str
    chunk_size: int = 1024
    chunk_overlap: int = 50

    @classmethod
    def from_env(cls) -> 'PipelineConfig':
        """Load configuration from environment variables."""
        load_dotenv(override=False)
        
        required_vars = [
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_BLOB_CONTAINER_NAME",
            "AZURE_BLOB_CONNECTION_STRING"
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            missing_vars = ', '.join(missing)
            raise ValueError(f"Missing environment variables: {missing_vars}")
            
        return cls(
            search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            container_name=os.getenv("AZURE_BLOB_CONTAINER_NAME"),
            connection_string=os.getenv("AZURE_BLOB_CONNECTION_STRING")
        )


class DocumentProcessor:
    """Handles the document processing pipeline."""
    
    def __init__(self, config: PipelineConfig):
        """Initialize with configuration."""
        self.config = config
        self.chunker = TextChunker()
        self.embedder = Embedder()
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def process_document(
        self,
        file_path: str | Path,
        document_id: str,
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Process a document through the entire pipeline.
        
        Args:
            file_path: Path to the document
            document_id: Unique identifier for the document
            tags: Optional list of tags for the document
        
        Raises:
            FileNotFoundError: If document doesn't exist
            ValueError: If parameters are invalid
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if not document_id:
            raise ValueError("document_id is required")
            
        tags = tags or ["technical section"]
        
        try:
            # Step 1: Upload to blob storage
            self.logger.info("Uploading document to blob storage...")
            blob_url = upload_to_blob(
                file_path=file_path,
                container_name=self.config.container_name,
                connection_string=self.config.connection_string
            )
            self.logger.info(f"Document uploaded to blob: {blob_url}")

            # Step 2: Read and chunk document
            self.logger.info("Processing document...")
            text = file_path.read_text(encoding='utf-8')
            chunks = self.chunker.chunk_with_overlap(
                text=text,
                max_tokens=self.config.chunk_size,
                overlap=self.config.chunk_overlap
            )
            self.logger.info(f"Generated {len(chunks)} chunks")

            # Step 3: Generate embeddings
            self.logger.info("Generating embeddings...")
            embeddings = self.embedder.embed_chunks(chunks)
            self.logger.info("Embeddings generated")

            # Step 4: Clear existing documents
            self.logger.info("Clearing existing search index...")
            delete_all_files(
                self.config.search_endpoint
            )

            # Step 5: Upload to search index
            self.logger.info("Uploading to search index...")
            chunk_pairs = enumerate(zip(chunks, embeddings), 1)
            for index, (chunk, embedding) in chunk_pairs:
                doc_chunk = DocumentChunk.create_chunk(
                    document_id=document_id,
                    chunk_index=index,
                    content=chunk,
                    tags=tags,
                    embeddings=embedding
                )
                upload_to_azure(
                    document=doc_chunk,
                    search_endpoint=self.config.search_endpoint
                )
            
            self.logger.info("Document processing complete")

        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            raise


def main():
    """Main entry point."""
    try:
        # Initialize configuration
        config = PipelineConfig.from_env()
        processor = DocumentProcessor(config)
        
        # Process document
        processor.process_document(
            file_path=Path("data/document1.txt"),
            document_id="document1"
        )
        
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()