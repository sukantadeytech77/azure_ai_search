
import requests
from models.document import DocumentChunk


class AzureSearchError(Exception):
    """Custom exception for Azure Search operations."""
    pass


def delete_all_files(
    search_endpoint: str,
    document_endpoint: str,
    api_key: str,
    batch_size: int = 1000
) -> int:
    """
    Delete all documents from Azure Search index.
    
    Args:
        search_endpoint: Azure Search query endpoint
        document_endpoint: Azure Search document endpoint
        api_key: Azure Search API key
        batch_size: Number of documents to process in each batch
        
    Returns:
        int: Number of documents deleted
        
    Raises:
        AzureSearchError: If there's an error communicating with Azure Search
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    try:
        # Fetch document IDs
        search_payload = {
            "search": "*",
            "select": "id",
            "top": batch_size
        }
        
        response = requests.post(
            search_endpoint,
            headers=headers,
            json=search_payload,
            timeout=30
        )
        
        if response.status_code != 200:
            msg = f"Failed to retrieve documents: {response.status_code}"
            msg += f" - {response.text}"
            raise AzureSearchError(msg)

        document_ids = [doc["id"] for doc in response.json().get("value", [])]
        
        if not document_ids:
            print("No documents found to delete.")
            return 0

        # Delete documents in a batch
        delete_payload = {
            "value": [
                {"@search.action": "delete", "id": doc_id}
                for doc_id in document_ids
            ]
        }

        delete_response = requests.post(
            document_endpoint,
            headers=headers,
            json=delete_payload,
            timeout=30
        )
        
        if delete_response.status_code not in (200, 207):
            msg = f"Failed to delete documents: {delete_response.status_code}"
            msg += f" - {delete_response.text}"
            raise AzureSearchError(msg)

        deleted_count = len(document_ids)
        print(f"Successfully deleted {deleted_count} documents.")
        return deleted_count

    except requests.exceptions.Timeout:
        raise AzureSearchError(
            "Operation timed out while communicating with Azure Search"
        )
    except requests.exceptions.RequestException as e:
        raise AzureSearchError(
            f"Error communicating with Azure Search: {str(e)}"
        )
    except Exception as e:
        raise AzureSearchError(
            f"Unexpected error: {str(e)}"
        )


def upload_to_azure(
    document: DocumentChunk,
    document_endpoint: str,
    api_key: str
):
    """
    Upload a document chunk to Azure Search using the DocumentChunk model.
    
    Args:
        document (DocumentChunk): The document chunk to upload
        document_endpoint (str): Azure Search document endpoint
        api_key (str): Azure Search API key
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        "value": [
            {
                "@search.action": "upload",
                **document.to_azure_document(),
                # Azure specific field name for embeddings
                "large_embedding": document.embeddings
            }
        ]
    }

    try:
        response = requests.post(document_endpoint, headers=headers, json=data)
        print(f"Status Code: {response.status_code} for id: {id}")
    except Exception as e:
        print(f"Error preparing upload: {e} for id: {id}")
