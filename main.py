from upload_service.blob_uploader import upload_to_blob
from document_processor.chunker import chunk_text
from document_processor.embedder import embed_chunks
from document_search.azure_uploader import upload_to_azure
from document_search.azure_uploader import delete_all_files

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

# Upload document
upload_to_blob(file_path, container_name, connection_string)

print("Document uploaded.")

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

documentid = "technical_document_1"

for index in range(len(chunks)):
    upload_to_azure(
        id=f"{documentid}_chunk{index+1}",
        documentid=documentid,
        content=chunks[index],
        embeddings=embeddings[index],
        document_endpoint=document_endpoint,
        api_key=api_key)

print("Document uploaded to Azure AI Search.")