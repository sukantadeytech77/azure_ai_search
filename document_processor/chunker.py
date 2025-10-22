
def chunk_text(text, max_tokens=8000):
    """
    Chunk text into segments of approximately max_tokens characters.
    Azure OpenAI embedding model supports up to ~8192 tokens per input.
    """
    chunks = []
    current_chunk = ""
    for paragraph in text.split("\n"):
        if len(current_chunk) + len(paragraph) < max_tokens:
            current_chunk += paragraph + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
