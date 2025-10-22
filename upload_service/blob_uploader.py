
from azure.storage.blob import BlobServiceClient
import os

def upload_to_blob(file_path, container_name, connection_string):
    print("Creating connection...")
    blob_service_client = BlobServiceClient.from_connection_string(
        connection_string)
    
    print(f"Using container: {container_name}")
    blob_client = blob_service_client.get_blob_client(container=container_name,
                                                      blob=os.path.basename(file_path))
    
    print(f"Uploading file: {file_path}...")
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return f"Uploaded {file_path} to container {container_name}"
