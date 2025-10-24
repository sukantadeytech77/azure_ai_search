
"""
Simple search interface for Azure AI Search.
"""

import os
import argparse
from document_search.azure_ai_search import AzureSearchClient
from dotenv import load_dotenv


def search_documents(query: str, max_results: int = 5) -> None:
    """
    Search documents and display results.
    """
    load_dotenv(override=False)
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    
    if not search_endpoint or not api_key:
        print("Error: Missing Azure Search configuration")
        return
        
    client = AzureSearchClient(search_endpoint, api_key)
    try:
        results = client.search_documents(
            query=query,
            top=max_results
        )
        
        if not results:
            print("No matching documents found.")
            return
            
        print(f"\nFound {len(results)} matching documents:")
        print("-" * 60)
        
        for i, result in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"ID: {result.id}")
            print(f"Document ID: {result.document_id}")
            print(f"Score: {result.score:.2f}")
            content = (
                result.content[:200] + "..."
                if len(result.content) > 100
                else result.content
            )
            print(f"Content: {content}")
            print("-" * 60)
            
    except Exception as e:
        print(f"Error performing search: {str(e)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Search documents in Azure AI Search index."
    )
    parser.add_argument(
        "-q", "--query",
        help="Search query text",
        type=str,
        required=True
    )
    parser.add_argument(
        "-n", "--num-results",
        help="Maximum number of results to return",
        type=int,
        default=5
    )

    args = parser.parse_args()
    search_documents(args.query, args.num_results)


if __name__ == "__main__":
    main()
