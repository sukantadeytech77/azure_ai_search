
"""
Semantic search interface for Azure AI Search.
"""

import os
import argparse
from document_search.azure_ai_search import AzureSearchClient
from dotenv import load_dotenv


def semantic_search_documents(search_text: str, max_results: int = 5) -> None:
    """
    Search documents and display results.
    """
    load_dotenv(override=False)
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    
    if not search_endpoint:
        print("Error: Missing Azure Search configuration")
        return
    
    tags = ["technical section"]

    client = AzureSearchClient(search_endpoint)
    try:

        results = client.semantic_search(
            search_text=search_text,
            filter_tags=tags,
            top=max_results
        )
        
        if not results:
            print("No matching documents found.")
            return
            
        print(f"\nFound {len(results)} matching documents:")
        print("-" * 60)
        
        display_information(results)
            
    except Exception as e:
        print(f"Error performing search: {str(e)}")


def display_information(results):
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

    print("Semantic Search Results:")
    semantic_search_documents(args.query, args.num_results)


if __name__ == "__main__":
    main()
