# 21. RAG Architecture

## Chunking Strategy
- Recursive text splitting by headers & paragraphs.
- Overlap: 10-20% chunk size depending on content density.

## Hybrid Search
- Dense: Cohere / OpenAI / Google embeddings.
- Sparse: BM25 on raw token streams.
- Re-ranking: Cross-encoder re-ranking for the top 5 most relevant results.
