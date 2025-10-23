
from pathlib import Path
from typing import Optional
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import AzureError


class BlobUploadError(Exception):
    """Custom exception for Azure Blob Storage operations."""
    pass


def upload_to_blob(
    file_path: str | Path,
    container_name: str,
    connection_string: str,
    content_type: Optional[str] = None
) -> str:
    """
    Upload a file to Azure Blob Storage.

    Args:
        file_path: Path to the file to upload
        container_name: Name of the Azure Blob container
        connection_string: Azure Storage connection string
        content_type: Optional MIME type of the file

    Returns:
        str: URL of the uploaded blob

    Raises:
        BlobUploadError: If there's an error during upload
        FileNotFoundError: If the source file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Create blob service client
        print("Creating Azure Blob Storage connection...")
        blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        
        # Ensure container exists
        try:
            blob_service_client.create_container(container_name)
            print(f"Created new container: {container_name}")
        except Exception:
            # Container already exists
            print(f"Using existing container: {container_name}")
        
        # Get blob client
        blob_name = file_path.name
        blob_client: BlobClient = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
        )
        
        # Upload file
        print(f"Uploading file: {file_path}")
        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_type=content_type
            )
        
        blob_url = blob_client.url
        print(f"Successfully uploaded {blob_name} to {container_name}")
        return blob_url

    except AzureError as e:
        raise BlobUploadError(f"Azure Storage error: {str(e)}")
    except Exception as e:
        raise BlobUploadError(f"Unexpected error during upload: {str(e)}")
