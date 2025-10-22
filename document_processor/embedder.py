
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

_embeddings_singleton = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_MODEL"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
)
_MODEL = os.environ["AZURE_OPENAI_DIMENSIONS"]


def embed_chunks(chunks):
    """
    Generate embeddings for a list of text chunks using Azure OpenAI.
    """

    embeddingResponses = []

    for chunk in chunks:
        response = _embeddings_singleton.embeddings.create(
            model=_MODEL,
            input=chunk,
        )

        embeddingResponses.append(response.data[0].embedding)
    
    return embeddingResponses
