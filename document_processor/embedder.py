
"""
Embeddings generation module using Azure OpenAI services.
Handles the creation of vector embeddings for text chunks.
"""

from typing import List, Optional
import os
from dataclasses import dataclass
from openai import AzureOpenAI
from openai.types.create_embedding_response import CreateEmbeddingResponse
from dotenv import load_dotenv


@dataclass
class EmbeddingConfig:
    """Configuration for Azure OpenAI embeddings service."""
    endpoint: str
    deployment: str
    api_version: str
    api_key: str
    dimensions: str

    @classmethod
    def from_env(cls) -> 'EmbeddingConfig':
        """Create configuration from environment variables."""
        load_dotenv()
        
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_MODEL",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_DIMENSIONS"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            vars_str = ', '.join(missing_vars)
            raise ValueError(
                f"Missing required environment variables: {vars_str}"
            )
        
        return cls(
            endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            deployment=os.environ["AZURE_OPENAI_MODEL"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            dimensions=os.environ["AZURE_OPENAI_DIMENSIONS"]
        )


class EmbeddingError(Exception):
    """Custom exception for embedding operations."""
    pass


class Embedder:
    """Handles text embedding operations using Azure OpenAI."""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize the embedder with configuration.
        
        Args:
            config: Optional embedding configuration. If None, loads from env.
            
        Raises:
            ValueError: If configuration is invalid
            EmbeddingError: If client initialization fails
        """
        try:
            self.config = config or EmbeddingConfig.from_env()
            self._client = AzureOpenAI(
                azure_endpoint=self.config.endpoint,
                azure_deployment=self.config.deployment,
                api_version=self.config.api_version,
                api_key=self.config.api_key
            )
        except Exception as e:
            raise EmbeddingError(f"Failed to initialize embedder: {str(e)}")

    def embed_chunks(
        self,
        chunks: List[str],
        batch_size: int = 10
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of text chunks.
        
        Args:
            chunks: List of text chunks to embed
            batch_size: Number of chunks to process in parallel
            
        Returns:
            List of embedding vectors
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        if not chunks:
            return []

        try:
            embeddings = []
            
            # Process chunks in batches
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                responses: List[CreateEmbeddingResponse] = [
                    self._client.embeddings.create(
                        model=self.config.dimensions,
                        input=chunk
                    )
                    for chunk in batch
                ]
                
                batch_embeddings = [
                    response.data[0].embedding for response in responses
                ]
                embeddings.extend(batch_embeddings)
                
                # Log progress for long operations
                if len(chunks) > batch_size:
                    processed = min(i + batch_size, len(chunks))
                    print(f"Processed {processed}/{len(chunks)} chunks")
            
            return embeddings

        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate embeddings: {str(e)}"
            )

    def embed_single(self, text: str) -> List[float]:
        """
        Generate embedding for a single text chunk.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            EmbeddingError: If embedding generation fails
        """
        try:
            response = self._client.embeddings.create(
                model=self.config.dimensions,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise EmbeddingError(
                f"Failed to generate single embedding: {str(e)}"
            )
