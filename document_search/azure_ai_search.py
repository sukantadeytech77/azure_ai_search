
"""
Azure AI Search integration module for document search and retrieval.
Provides functionality to search and retrieve documents using Azure
Cognitive Search.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from requests.exceptions import RequestException


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
        endpoint: str,
        api_key: str
    ):
        """
        Initialize the Azure Search client.

        Args:
            endpoint: Azure Search service endpoint
            api_key: API key for authentication
        """
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        if not all([endpoint, api_key]):
            raise ValueError("Both endpoint and api_key are required")

    def _get_headers(self) -> Dict[str, str]:
        """Get the required headers for API requests."""
        return {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

    def search_documents(
        self,
        query: str,
        *,
        filter_tags: Optional[List[str]] = None,
        select_fields: Optional[List[str]] = None,
        top: int = 10,
        skip: int = 0,
        order_by: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for documents in the Azure Search index.

        Args:
            query: Search query text
            filter_tags: Optional list of tags to filter by
            select_fields: Optional list of fields to return
            top: Maximum number of results to return
            skip: Number of results to skip
            order_by: Optional field to sort by

        Returns:
            List of SearchResult objects

        Raises:
            AzureSearchError: If the search operation fails
            ValueError: If parameters are invalid
        """
        if not query:
            raise ValueError("Search query cannot be empty")
        
        if top < 1:
            raise ValueError("top must be greater than 0")
        
        if skip < 0:
            raise ValueError("skip must be non-negative")

        try:
            # Build search payload
            payload = {
                "search": query,
                "select": ",".join(
                    select_fields or ["id", "documentid", "content", "tags"]
                ),
                "top": min(top, 1000),  # Azure's max limit
                "skip": skip,
                "count": True
            }

            # Add optional parameters
            if filter_tags:
                tag_filters = [
                    f"tags/any(t: t eq '{tag}')"
                    for tag in filter_tags
                ]
                payload["filter"] = " or ".join(tag_filters)

            if order_by:
                payload["orderby"] = order_by

            # Make request
            self.logger.debug(f"Searching with payload: {payload}")
            response = requests.post(
                self.endpoint,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )

            # Handle response
            if response.status_code != 200:
                raise AzureSearchError(
                    f"Search failed: {response.status_code} - {response.text}"
                )

            # Parse results
            data = response.json()
            total_count = data.get("@odata.count", 0)
            results = [
                SearchResult.from_json(doc) for doc in data.get("value", [])
            ]

            self.logger.info(
                f"Found {total_count} results, returning {len(results)} items"
            )
            return results

        except RequestException as e:
            raise AzureSearchError(f"Search request failed: {str(e)}")
        except Exception as e:
            raise AzureSearchError(f"Unexpected error during search: {str(e)}")

    def get_document_by_id(self, document_id: str) -> Optional[SearchResult]:
        """
        Retrieve a specific document by ID.

        Args:
            document_id: The ID of the document to retrieve

        Returns:
            SearchResult object if found, None otherwise

        Raises:
            AzureSearchError: If the retrieval operation fails
        """
        try:
            results = self.search_documents(
                f"documentid eq '{document_id}'",
                top=1
            )
            return results[0] if results else None
            
        except Exception as e:
            raise AzureSearchError(
                f"Failed to retrieve document {document_id}: {str(e)}"
            )