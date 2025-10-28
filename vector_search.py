
"""
Simple search interface for Azure AI Search.
"""

import os
import argparse
from document_search.azure_ai_search import AzureSearchClient
from dotenv import load_dotenv
from document_processor.embedder import Embedder


def vector_search_documents(
    embeddings: list,
    max_results: int = 5,
    document_tags: list | None = None
) -> None:
    """
    Search documents and display results.

    Args:
        embeddings: Vector embeddings to search with
        max_results: Maximum number of results to return
        document_tags: Optional list of tags to filter by
    """
    load_dotenv(override=False)
    
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    
    if not search_endpoint:
        print("Error: Missing Azure Search configuration")
        return

    client = AzureSearchClient(search_endpoint)
    try:
        results = client.vector_search(
            embeddings=embeddings,
            filter_tags=document_tags,
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
    """Display search results with formatted output."""
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
    parser.add_argument(
        "--documentTags",
        help="Comma-separated tags to filter search results",
        type=str,
        default=""
    )

    args = parser.parse_args()
    
    # Parse document tags if provided
    document_tags = (
        [t.strip() for t in args.documentTags.split(",") if t.strip()]
        if args.documentTags else None
    )

    # Generate embeddings
    embedder = Embedder()
    embeddings = embedder.embed_chunks([args.query])[0]
    # Search documents by sending embeddings
    print("Vector Search Results:")
    vector_search_documents(
        embeddings=embeddings,
        max_results=args.num_results,
        document_tags=document_tags
    )


if __name__ == "__main__":
    main()
