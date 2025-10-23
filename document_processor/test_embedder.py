"""Tests for the embeddings generation functionality."""

import pytest
from unittest.mock import Mock, patch
from .embedder import Embedder, EmbeddingConfig, EmbeddingError


@pytest.fixture
def mock_config():
    """Provide a mock embedding configuration."""
    return EmbeddingConfig(
        endpoint="https://test.openai.azure.com",
        deployment="test-deployment",
        api_version="2023-05-15",
        api_key="test-key",
        dimensions="text-embedding-ada-002"
    )


@pytest.fixture
def mock_response():
    """Provide a mock embedding response."""
    response = Mock()
    response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
    return response


def test_embedder_initialization(mock_config):
    """Test embedder initialization with config."""
    with patch('openai.AzureOpenAI'):
        embedder = Embedder(config=mock_config)
        assert embedder.config == mock_config


def test_embedder_env_initialization():
    """Test embedder initialization from environment."""
    env_vars = {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_MODEL": "test-deployment",
        "AZURE_OPENAI_API_VERSION": "2023-05-15",
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_DIMENSIONS": "text-embedding-ada-002"
    }
    
    with patch.dict('os.environ', env_vars), patch('openai.AzureOpenAI'):
        embedder = Embedder()
        assert embedder.config.endpoint == env_vars["AZURE_OPENAI_ENDPOINT"]


def test_embed_chunks(mock_config, mock_response):
    """Test batch embedding generation."""
    with patch('openai.AzureOpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.embeddings.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        embedder = Embedder(config=mock_config)
        chunks = ["test1", "test2"]
        embeddings = embedder.embed_chunks(chunks, batch_size=1)
        
        assert len(embeddings) == 2
        assert all(isinstance(emb, list) for emb in embeddings)
        assert mock_instance.embeddings.create.call_count == 2


def test_embed_single(mock_config, mock_response):
    """Test single text embedding."""
    with patch('openai.AzureOpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.embeddings.create.return_value = mock_response
        mock_client.return_value = mock_instance
        
        embedder = Embedder(config=mock_config)
        embedding = embedder.embed_single("test")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 3  # Mock response has 3 dimensions
        mock_instance.embeddings.create.assert_called_once()


def test_error_handling(mock_config):
    """Test error handling in embedding operations."""
    with patch('openai.AzureOpenAI') as mock_client:
        mock_instance = Mock()
        mock_instance.embeddings.create.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance
        
        embedder = Embedder(config=mock_config)
        
        with pytest.raises(EmbeddingError):
            embedder.embed_single("test")
        
        with pytest.raises(EmbeddingError):
            embedder.embed_chunks(["test1", "test2"])


def test_empty_input(mock_config):
    """Test handling of empty input."""
    with patch('openai.AzureOpenAI'):
        embedder = Embedder(config=mock_config)
        assert embedder.embed_chunks([]) == []