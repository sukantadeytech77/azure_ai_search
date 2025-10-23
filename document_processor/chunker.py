
"""
Text chunking utilities for processing documents for embeddings and AI models.
Provides various methods to split text into manageable chunks while preserving
context and handling token limits appropriately.
"""

from typing import List, Optional
import tiktoken
from tiktoken.core import Encoding


class ChunkerError(Exception):
    """Custom exception for text chunking operations."""
    pass


class TextChunker:
    """Handles text chunking operations with various strategies."""
    
    # Common model token limits
    MAX_GPT35_TOKENS = 4096
    MAX_AZURE_EMBED_TOKENS = 8192
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the chunker with a specific model's tokenizer.
        
        Args:
            model_name: Name of the model to use for tokenization
            
        Raises:
            ChunkerError: If tokenizer initialization fails
        """
        try:
            self.model_name = model_name
            self._tokenizer = tiktoken.encoding_for_model(model_name)
        except Exception as e:
            raise ChunkerError(f"Failed to initialize tokenizer: {str(e)}")

    def _validate_chunk_params(
        self,
        max_tokens: int,
        overlap: Optional[int] = None
    ) -> None:
        """Validate chunking parameters."""
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if overlap is not None and overlap >= max_tokens:
            raise ValueError("overlap must be less than max_tokens")
        if overlap is not None and overlap < 0:
            raise ValueError("overlap must be non-negative")

    def chunk_text_by_words(
        self,
        text: str,
        max_tokens: int = MAX_AZURE_EMBED_TOKENS
    ) -> List[str]:
        """
        Chunk text into segments by word boundaries.
        
        Args:
            text: Input text to chunk
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks
            
        Raises:
            ValueError: If max_tokens is invalid
        """
        self._validate_chunk_params(max_tokens)
        
        words = text.split()
        return [
            ' '.join(words[i:i + max_tokens])
            for i in range(0, len(words), max_tokens)
        ]

    def chunk_by_tokens(
        self,
        text: str,
        max_tokens: int = 1024
    ) -> List[str]:
        """
        Chunk text into segments based on token count.
        
        Args:
            text: Input text to chunk
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of text chunks
            
        Raises:
            ValueError: If max_tokens is invalid
            ChunkerError: If tokenization fails
        """
        self._validate_chunk_params(max_tokens)
        
        try:
            tokens = self._tokenizer.encode(text)
            chunks = [
                tokens[i:i + max_tokens]
                for i in range(0, len(tokens), max_tokens)
            ]
            return [self._tokenizer.decode(chunk) for chunk in chunks]
        except Exception as e:
            raise ChunkerError(f"Failed to chunk text: {str(e)}")

    def chunk_with_overlap(
        self,
        text: str,
        max_tokens: int = 1024,
        overlap: int = 50
    ) -> List[str]:
        """
        Chunk text into overlapping segments for better context preservation.
        
        Args:
            text: Input text to chunk
            max_tokens: Maximum tokens per chunk
            overlap: Number of tokens to overlap between chunks
            
        Returns:
            List of text chunks with overlap
            
        Raises:
            ValueError: If max_tokens or overlap is invalid
            ChunkerError: If tokenization fails
        """
        self._validate_chunk_params(max_tokens, overlap)
        
        try:
            tokens = self._tokenizer.encode(text)
            chunks = []
            start = 0
            
            while start < len(tokens):
                end = min(start + max_tokens, len(tokens))
                chunk = tokens[start:end]
                chunks.append(self._tokenizer.decode(chunk))
                start += max_tokens - overlap
                
            return chunks
        except Exception as e:
            raise ChunkerError(f"Failed to chunk text with overlap: {str(e)}")

    @property
    def tokenizer(self) -> Encoding:
        """Get the underlying tokenizer."""
        return self._tokenizer

    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.
        
        Args:
            text: Input text to count tokens for
            
        Returns:
            Number of tokens in the text
            
        Raises:
            ChunkerError: If tokenization fails
        """
        try:
            return len(self._tokenizer.encode(text))
        except Exception as e:
            raise ChunkerError(f"Failed to count tokens: {str(e)}")
