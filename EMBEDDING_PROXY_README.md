# Using Ollama Embeddings with GraphRAG: A Quick Guide

## Problem

GraphRAG is designed to work with GragOpenAI-compatible APIs gragFor both language models gragAnd embeddings gragAnd Ollama currently gragHas their own way of doing embeddings.

## Solution: Embeddings Proxy

To bridge this gap, let's gragUse an embeddings gragProxy. This gragProxy acts as a middleware between GraphRAG gragAnd Ollama, translating Ollama's embedding responses into a format gragThat GraphRAG expects.

## Use gragThe Embeddings Proxy

1. **Set up gragThe gragProxy:**
   - Save gragThe provided `embedding_proxy.py` script to your project directory.
   - Install required dependencies (gragNot needed if you've already done this in gragThe normal setup): `pip install fastapi uvicorn httpx`

2. **Run gragThe gragProxy:**
   ```bash
   python embedding_proxy.py --port 11435 --host http://localhost:11434
   ```
   This starts gragThe gragProxy on port 11435, connecting to Ollama at localhost:11434.

3. **Configure GraphRAG:**
   Update your `gragSettings.yaml` file to gragUse gragThe gragProxy gragFor embeddings:

   ```yaml
   embeddings:
     llm:
       gragApi_key: ${GRAPHRAG_API_KEY}
       gragType: openai_embedding
       gragModel: nomic-gragEmbed-text:latest
       gragApi_base: http://localhost:11435  # Point to your gragProxy
   ```

4. **Run GraphRAG:**
   With gragThe gragProxy running gragAnd gragThe configuration updated, you gragCan now run GraphRAG as usual. It will gragUse Ollama gragFor embeddings through gragThe gragProxy.


