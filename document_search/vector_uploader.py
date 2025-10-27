
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from models.embedding_document import EmbeddingDocumentChunk

# Authenticate using RBAC
credential = DefaultAzureCredential()
index_name = "vector_documents"


class AzureSearchError(Exception):
    """Custom exception for Azure Search operations."""
    pass


def delete_all_files(
    search_endpoint: str
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
    
    # Create search client
    search_client = SearchClient(endpoint=search_endpoint,
                                 index_name=index_name,
                                 credential=credential)

    # Perform a search
    results = search_client.search(search_text="*")
    # Collect document IDs to delete
    document_ids = [doc["id"] for doc in results]
    # Delete documents
    if document_ids:
        delete_actions = [
            {"@search.action": "delete", "id": doc_id}
            for doc_id in document_ids
        ]
        search_client.upload_documents(documents=delete_actions)
        print(
            f"Deleted {len(document_ids)} documents "
            f"from index '{index_name}'."
        )
    else:
        print("No documents found to delete.")

    deleted_count = len(document_ids)
    print(f"Successfully deleted {deleted_count} documents.")
    return deleted_count


def upload_to_azure(
    document: EmbeddingDocumentChunk,
    search_endpoint: str,
) -> None:
    """
    Upload a document chunk to Azure Search using the DocumentChunk model.
    
    Args:
        document (DocumentChunk): The document chunk to upload
        search_endpoint (str): Azure Search service endpoint
    
    Raises:
        AzureSearchError: If the upload fails
    """
    try:
        # Create search client
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=credential
        )
        
        # Convert DocumentChunk to search document format
        search_doc = {
            "id": document.id,
            "documentid": document.document_id,
            "content": document.content,
            "large_embedding": document.embeddings,
            "tags": document.tags
        }
        
        # Upload documents directly
        search_client.upload_documents(documents=search_doc)

        print("Document uploaded to Azure AI Search index.")
    except Exception as e:
        raise AzureSearchError(f"Upload failed: {str(e)}")

