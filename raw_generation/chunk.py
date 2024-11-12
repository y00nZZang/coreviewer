import tiktoken

def split_text_by_tokens(text, max_tokens, overlap_tokens, model="gpt-4"):
    """
    Split text into chunks based on token count using a sliding window approach.
    :param text: The input text to split.
    :param max_tokens: Maximum tokens per chunk.
    :param overlap_tokens: Overlap tokens between chunks.
    :param model: Model to base token encoding on.
    :return: List of text chunks.
    """
    # Initialize tokenizer for the specified model
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += max_tokens - overlap_tokens
    return chunks

def generate_review_summary_for_chunk(client, chunk, few_shot_examples):
    """
    Generate review summary for a single chunk of text.
    """
    messages = few_shot_examples + [
        {"role": "user", "content": f"Paper content:\n{chunk}\nGenerate a review summary for this section:"}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message['content']

def generate_full_review_summary(client, raw_text, few_shot_examples, max_tokens=7584, overlap_tokens=512):
    """
    Generate a full review summary by applying a token-based sliding window.
    """
    # Split text into overlapping chunks by token count
    chunks = split_text_by_tokens(raw_text, max_tokens, overlap_tokens)
    
    # Generate and collect summaries for each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1}/{len(chunks)}")
        chunk_summary = generate_review_summary_for_chunk(client, chunk, few_shot_examples)
        chunk_summaries.append(chunk_summary)
    
    # Combine all chunk summaries into a single text
    full_summary = "\n".join(chunk_summaries)
    return full_summary