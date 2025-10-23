# AI Agent Instructions for Clever Documents

This is a document processing and search system that leverages Azure services for storing, processing, and searching documents using semantic embeddings.

## System Architecture

The system follows a pipeline architecture with these main components:

1. **Upload Service** (`upload_service/`)
   - Handles document uploads to Azure Blob Storage
   - See `blob_uploader.py` for Azure Blob Storage integration

2. **Document Processor** (`document_processor/`)
   - Chunks documents into smaller segments (`chunker.py`)
   - Generates embeddings for text chunks (`embedder.py`)
   - Uses tiktoken for token-aware text chunking

3. **Document Search** (`document_search/`)
   - Manages Azure AI Search integration (`azure_ai_search.py`)
   - Handles document upload/deletion in search index (`azure_uploader.py`)

4. **Metadata Store** (`metadata_store/`)
   - PostgreSQL database for document metadata
   - Stores document IDs, filenames, and upload timestamps

## Key Patterns and Conventions

### Configuration
- Environment variables are used for all Azure credentials and endpoints
- Load from `.env` file using `python-dotenv` (see `main.py`)
- Required variables:
  ```
  AZURE_DOCUMENTS_ENDPOINT
  AZURE_SEARCH_ENDPOINT
  AZURE_SEARCH_API_KEY
  AZURE_BLOB_CONTAINER_NAME
  AZURE_BLOB_CONNECTION_STRING
  ```

### Document Processing
- Documents are chunked with overlap for better context preservation
- Default chunk size: 1024 tokens with 50 token overlap
- Uses GPT-3.5-Turbo tokenizer for consistent token counting
- Example from `chunker.py`:
  ```python
  chunks = chunk_with_overlap(text, model_name="gpt-3.5-turbo", 
                            max_tokens=1024, overlap=50)
  ```

### Search Integration
- Documents in Azure AI Search are tagged for filtering
- Each chunk is stored with:
  - Unique ID: `{documentid}_chunk{index}`
  - Original document ID
  - Content text
  - Embeddings
  - Tags array

## Development Workflow

1. Environment Setup:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Database Setup:
   ```sql
   CREATE TABLE documents (
       doc_id VARCHAR PRIMARY KEY,
       filename TEXT,
       upload_time TIMESTAMP
   );
   ```

3. Configuration:
   - Create `.env` file with required Azure credentials
   - Update Azure endpoints in environment variables

## Common Tasks

- **Process and Upload Document**:
  See `main.py` for the complete pipeline example
  
- **Search Documents**:
  Use `azure_ai_search.py`'s `retrieve_documents()` function
  
- **Clear Search Index**:
  Use `azure_uploader.py`'s `delete_all_files()` function

## Integration Points

1. Azure Blob Storage
   - Document binary storage
   - Configured via connection string

2. Azure PostgreSQL
   - Metadata storage
   - Simple schema for document tracking

3. Azure AI Search
   - Vector search index
   - Stores document chunks and embeddings
   - Supports semantic search queries