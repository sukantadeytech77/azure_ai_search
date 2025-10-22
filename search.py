
from document_search.azure_ai_search import retrieve_documents

import os
from dotenv import load_dotenv

load_dotenv(override=False)

document_endpoint = os.getenv("AZURE_DOCUMENTS_ENDPOINT")
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
api_key = os.getenv("AZURE_SEARCH_API_KEY")

print("Retrieving documents from Azure AI Search...")
retrieve_documents(search_endpoint, api_key, "AI search integration")
print("Document retrieval complete.")