
"""
Azure AI Search integration module for document search and retrieval.
Provides functionality to search and retrieve documents using Azure
Cognitive Search.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient

@dataclass
class SearchResult:
    """Represents a single document search result."""
    id: str
    document_id: str
    content: str
    score: float
    tags: List[str]

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'SearchResult':
        """Create a SearchResult instance from JSON data."""
        return cls(
            id=json_data['id'],
            document_id=json_data['documentid'],
            content=json_data.get('content', ''),
            score=float(json_data.get('@search.score', 0.0)),
            tags=json_data.get('tags', [])
        )


class AzureSearchError(Exception):
    """Custom exception for Azure Search operations."""
    pass


class AzureSearchClient:
    """Client for interacting with Azure Cognitive Search."""

    def __init__(
        self,
        endpoint: str
    ):
        """
        Initialize the Azure Search client.

        Args:
            endpoint: Azure Search service endpoint
        """
        self.endpoint = endpoint.rstrip('/')
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
    def vector_search(
        self,
        embeddings: list,
        filter_tags: Optional[List[str]] = None,
        top: int = 5
    ) -> List[SearchResult]:
        """
        Perform semantic search using Azure Cognitive Search.
        
        Args:
            search_text: The text to search for
            top: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
            
        Raises:
            AzureSearchError: If the search operation fails
        """
        try:
            # Azure Cognitive Search configuration
            index_name = "cleverdocuments"
            credential = DefaultAzureCredential()
            
            # Create search client
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=credential
            )
            # Perform vector search
            
            results = search_client.search(
                search_text=None,
                vector_queries=[{
                    "kind": "vector",
                    "fields": "large_embedding",
                    "vector": embeddings,
                    "k": top,
                    "vectorSearchProfile": "vector-profile-1761148909736"
                }],
                select=["id", "content", "tags"]
            )

            for result in results:
                self.logger.debug("Found document ID: %s with score: %s",
                                  result['id'], result['@search.score'])
            # Convert to SearchResult objects
            return [SearchResult.from_json(result) for result in results]
            
        except Exception as e:
            self.logger.error("Semantic search failed: %s", str(e))
            raise AzureSearchError(f"Search failed: {str(e)}")
    
    def semantic_search(
        self,
        search_text: str,
        filter_tags=Optional[List[str]],
        top: int = 5
    ) -> List[SearchResult]:
        """
        Perform semantic search using Azure Cognitive Search.
        
        Args:
            search_text: The text to search for
            top: Maximum number of results to return
            
        Returns:
            List of SearchResult objects sorted by relevance
            
        Raises:
            AzureSearchError: If the search operation fails
        """
        try:
            # Azure Cognitive Search configuration
            index_name = "cleverdocuments"
            credential = DefaultAzureCredential()
            
            # Create search client
            search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=index_name,
                credential=credential
            )

            # Construct filter expression if tags are provided
            filter_expression = None
            if filter_tags:
                filter_expression = " or ".join([f"tags/any(t: t eq '{tag}')"
                                                 for tag in filter_tags])

            # Perform semantic search with size limit
            results = list(search_client.search(
                search_text=search_text,
                top=top,
                select=["id", "documentid", "content", "tags"],
                filter=filter_expression
            ))
            
            # Convert to SearchResult objects
            return [SearchResult.from_json(result) for result in results]
            
        except Exception as e:
            self.logger.error("Semantic search failed: %s", str(e))
            raise AzureSearchError(f"Search failed: {str(e)}")