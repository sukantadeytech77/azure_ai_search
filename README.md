<<<<<<< HEAD
# azure_ai_search
=======
# Document uploads and Q & A System with Azure

## Features
- Upload large documents via UI
- Store files in Azure Blob Storage
- Store metadata in Azure PostgreSQL
- Chunk and embed document text
- Index embeddings in Azure AI Search
- Perform semantic search

## Setup Instructions
1. Create pythonn env: 
```
python3 -m venv venv
```
2. Install Requirements:
```
venv\Scripts\activate
python3 -m pip install -r requirements.txt
```
3. Configure your Azure credentials in main.py:
   - Blob Storage connection string
   - PostgreSQL connection parameters
   - Azure AI Search endpoint and API key

4. Create PostgreSQL table:
   CREATE TABLE documents (
       doc_id VARCHAR PRIMARY KEY,
       filename TEXT,
       upload_time TIMESTAMP
   );

4. Run the main script:
   python main.py


>>>>>>> 7496204 (Initial commit)
