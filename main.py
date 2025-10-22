
from upload_service.blob_uploader import upload_to_blob
#from metadata_store.postgres_handler import store_metadata
from document_processor.chunker import chunk_text
from document_processor.embedder import embed_chunks
from document_search.azure_uploader import upload_to_azure
from document_search.azure_uploader import delete_all_files
from document_search.azure_ai_search import retrieve_documents 

# from document_search.azure_ai_search import index_documents
import os
from dotenv import load_dotenv

load_dotenv(override=False)

document_endpoint = os.getenv("AZURE_DOCUMENTS_ENDPOINT")
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
api_key = os.getenv("AZURE_SEARCH_API_KEY")

file_path = r"D:\Work\clever-documents\data\document1.txt"

container_name = os.getenv("AZURE_BLOB_CONTAINER_NAME")
connection_string = os.getenv("AZURE_BLOB_CONNECTION_STRING")

print("Starting document upload...")
print(f"Using container: {container_name}")
print(f"Using connection string: {connection_string}")

postgres_params = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "your_host",
    "port": "5432"
}

# Upload document
upload_to_blob(file_path, container_name, connection_string)

print("Document uploaded.")


# Store metadata
# store_metadata("doc123", os.path.basename(file_path), datetime.datetime.now(), postgres_params)
# print("Metadata stored.")


# Process document
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

chunks = chunk_text(text)
print(len(chunks[1]))


embeddings = embed_chunks(chunks)

print("Embeddings generated.")

print(f"Processed {len(chunks)} chunks.")

print("Document embedding complete.")

# Upload embeddings to Azure AI Search
print("Uploading document to Azure AI Search...")

delete_all_files(search_endpoint, document_endpoint, api_key)

documentid = "test_document123"

for index in range(len(chunks)):
    upload_to_azure(
        documentid=f"{documentid}_chunk{index+1}",
        content=chunks[index],
        embeddings=embeddings[index],
        search_endpoint=document_endpoint,
        api_key=api_key)

print("Document uploaded to Azure AI Search.")

print("Retrieving documents from Azure AI Search...")
retrieve_documents(search_endpoint, api_key, "Ethical and Societal Considerations")
print("Document retrieval complete.")