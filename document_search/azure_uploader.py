
import requests


def delete_all_files(search_endpoint, document_endpoint, api_key):
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    search_payload = {
        "search": "*",
        "select": "id",
        "top": 1000
    }

    response = requests.post(search_endpoint, headers=headers, 
                             json=search_payload)

    if response.status_code != 200:
        print("Failed to retrieve documents:", response.status_code, response.text)
        exit()

    document_ids = [doc["id"] for doc in response.json().get("value", [])]

    if document_ids:
        delete_payload = {
                "value": [
                    {"@search.action": "delete", "id": doc_id} for doc_id in document_ids
                ]
            }

        requests.post(document_endpoint, headers=headers, json=delete_payload)
    else:
        print("No documents to delete.")
    

def upload_to_azure(documentid, content, embeddings, document_endpoint, api_key):
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    data = {
        "value": [
            {
                "@search.action": "upload",
                "id": documentid,
                "content": content,
                "large_embedding": embeddings
            }
        ]
    }

    try:
        response = requests.post(document_endpoint, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error preparing upload: {e}")
