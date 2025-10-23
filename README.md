# Clever Documents

A robust document processing and semantic search system built with Azure services. The system handles document uploads, processing, embedding generation, and semantic search capabilities.

## Features

### Document Processing
- Smart document chunking with configurable overlap
- Token-aware text segmentation using tiktoken
- Efficient embedding generation with Azure OpenAI
- Batch processing support for large documents

### Storage & Search
- Azure Blob Storage for document storage
- Azure PostgreSQL for metadata management
- Azure AI Search for semantic search capabilities
- Tag-based document filtering
- Configurable search parameters

### CLI Interface
- Interactive search mode
- Command-line arguments support
- Rich text output formatting
- Tag-based filtering options

## Architecture

The system follows a modular pipeline architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Upload Service │ -> │ Document Processor│ -> │ Document Search │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│ Azure Blob  │        │ Text Chunks & │        │  Azure AI   │
│  Storage    │        │  Embeddings   │        │   Search    │
└─────────────┘        └──────────────┘        └─────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   PostgreSQL    │
                     │    Metadata     │
                     └─────────────────┘
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Azure subscription with:
  - Azure Blob Storage
  - Azure PostgreSQL
  - Azure OpenAI Service
  - Azure AI Search

### Environment Setup

1. Clone the repository and create virtual environment:
   ```powershell
   git clone https://github.com/your-repo/clever-documents.git
   cd clever-documents
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Create .env file with required credentials:
   ```env
   AZURE_DOCUMENTS_ENDPOINT=your-search-docs-endpoint
   AZURE_SEARCH_ENDPOINT=your-search-endpoint
   AZURE_SEARCH_API_KEY=your-search-api-key
   AZURE_BLOB_CONTAINER_NAME=your-container-name
   AZURE_BLOB_CONNECTION_STRING=your-connection-string
   AZURE_OPENAI_ENDPOINT=your-openai-endpoint
   AZURE_OPENAI_API_KEY=your-openai-key
   AZURE_OPENAI_MODEL=your-model-deployment
   AZURE_OPENAI_API_VERSION=2023-05-15
   AZURE_OPENAI_DIMENSIONS=your-embeddings-model
   ```

## Usage

### Document Processing
Process and index a document:
```powershell
python main.py --file path/to/document.txt --tags technical,research
```

### Document Search
Search indexed documents:
```powershell
# Basic search
python search.py -q "machine learning"

# Search with tags
python search.py -q "neural networks" -t "technical,research"

# Interactive mode
python search.py -i

# Limit results
python search.py -q "data science" -n 3
```

## Development

### Project Structure
- `document_processor/`: Document chunking and embedding generation
- `document_search/`: Azure AI Search integration
- `metadata_store/`: PostgreSQL database operations
- `upload_service/`: Azure Blob Storage operations
- `models/`: Data models and schemas

### Running Tests
```powershell
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_chunker.py
```

### Code Quality
```powershell
# Format code
black .

# Sort imports
isort .

# Type checking
mypy .

# Linting
flake8
```

## Configuration

### Chunking Parameters
- Default chunk size: 1024 tokens
- Default overlap: 50 tokens
- Model: gpt-3.5-turbo tokenizer

### Search Parameters
- Default results per page: 5
- Supports tag-based filtering
- Configurable scoring and sorting

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details