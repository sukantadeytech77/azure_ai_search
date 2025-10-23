"""Tests for Azure AI Search integration."""

import pytest
from unittest.mock import patch
from .azure_ai_search import (
    AzureSearchClient,
    SearchResult,
    AzureSearchError
)


@pytest.fixture
def mock_response():
    """Create a mock successful search response."""
    return {
        "@odata.count": 2,
        "value": [
            {
                "id": "doc1",
                "documentid": "test1",
                "content": "Test content 1",
                "@search.score": 0.8,
                "tags": ["technical"]
            },
            {
                "id": "doc2",
                "documentid": "test2",
                "content": "Test content 2",
                "@search.score": 0.6,
                "tags": ["research"]
            }
        ]
    }


def test_search_result_from_json():
    """Test SearchResult creation from JSON."""
    json_data = {
        "id": "test1",
        "documentid": "doc1",
        "content": "Test content",
        "@search.score": 0.9,
        "tags": ["technical", "research"]
    }
    
    result = SearchResult.from_json(json_data)
    
    assert result.id == "test1"
    assert result.document_id == "doc1"
    assert result.content == "Test content"
    assert result.score == 0.9
    assert result.tags == ["technical", "research"]


def test_azure_search_client_initialization():
    """Test client initialization."""
    endpoint = "https://test.search.windows.net"
    client = AzureSearchClient(endpoint, "test-key")
    assert client.endpoint == endpoint
    assert client.api_key == "test-key"
    
    with pytest.raises(ValueError):
        AzureSearchClient("", "test-key")
    
    with pytest.raises(ValueError):
        AzureSearchClient("https://test.search.windows.net", "")


def test_search_documents(mock_response):
    """Test document search functionality."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        endpoint = "https://test.search.windows.net"
        client = AzureSearchClient(endpoint, "test-key")
        results = client.search_documents("test query")
        
        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].score > results[1].score


def test_search_validation():
    """Test search parameter validation."""
    client = AzureSearchClient("https://test.search.windows.net", "test-key")
    
    with pytest.raises(ValueError):
        client.search_documents("")
    
    with pytest.raises(ValueError):
        client.search_documents("test", top=0)
    
    with pytest.raises(ValueError):
        client.search_documents("test", skip=-1)


def test_search_error_handling():
    """Test error handling in search operations."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"
        
        endpoint = "https://test.search.windows.net"
        client = AzureSearchClient(endpoint, "test-key")
        
        with pytest.raises(AzureSearchError):
            client.search_documents("test query")


def test_get_document_by_id(mock_response):
    """Test retrieving a specific document."""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response
        
        endpoint = "https://test.search.windows.net"
        client = AzureSearchClient(endpoint, "test-key")
        doc = client.get_document_by_id("test1")
        
        assert doc is not None
        assert isinstance(doc, SearchResult)
        assert doc.document_id == "test1"