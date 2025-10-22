
import requests


def retrieve_documents(search_endpoint, api_key, search_text):
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    search_payload = {
        "search": search_text,
        "select": "id,content",
        "top": 1
    }

    response = requests.post(search_endpoint, headers=headers, json=search_payload)
    
    if response.status_code == 200:
        results = response.json().get("value", [])
        for doc in results:
            print(f"ID: {doc['id']}")
            print(f"Content: {doc.get('content', '')}")
            print("-" * 40)
    else:
        print("Failed to retrieve documents:", response.status_code, response.text)



