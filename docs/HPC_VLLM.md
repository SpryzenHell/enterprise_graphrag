# Private vLLM / HPC setup

This guide shows how to run the GraphRAG service next to a private OpenAI-compatible vLLM server on an HPC machine. The services can stay private; a laptop can reach the GraphRAG API through an SSH tunnel.

## 1. Network setup

On the HPC machine, enable the site's network configuration before any network command:

    source "$HOME/Conda/bin/activate"
    cd "$HOME"
    python -c "import core_config"

Keep that shell active for commands such as `curl`, `pip`, model downloads and `git` operations.

## 2. Start vLLM

Bind vLLM to loopback:

    export VLLM_API_KEY="<generation-key-or-empty>"
    vllm serve <CHAT_MODEL> --host 127.0.0.1 --port 8001

Check the model name:

    curl -H "Authorization: Bearer ${VLLM_API_KEY}" \
      http://127.0.0.1:8001/v1/models

Use the `data[].id` value as `VLLM_MODEL`.

## 3. Start an embedding service

GraphRAG needs an OpenAI-compatible embeddings endpoint. It may be a second vLLM process or another private provider.

Example:

    export EMBEDDING_API_KEY="<embedding-key-or-empty>"
    curl -H "Authorization: Bearer ${EMBEDDING_API_KEY}" \
      -H "Content-Type: application/json" \
      -d '{"model":"<EMBEDDING_MODEL>","input":["Enterprise GraphRAG probe."]}' \
      http://127.0.0.1:8002/v1/embeddings

Count the returned vector values. That count must match `EMBEDDING_DIMENSION`.

## 4. Configure GraphRAG

For a host-process deployment:

    GRAGRAPH_ENV=development
    VLLM_BASE_URL=http://127.0.0.1:8001
    VLLM_API_KEY=<generation-key-or-empty>
    VLLM_MODEL=<CHAT_MODEL>

    EMBEDDING_BASE_URL=http://127.0.0.1:8002
    EMBEDDING_API_KEY=<embedding-key-or-empty>
    EMBEDDING_MODEL=<EMBEDDING_MODEL>
    EMBEDDING_DIMENSION=<measured-dimension>

Then:

    python -m enterprise_graphrag.run --host 127.0.0.1 --port 8000

## 5. Run the provider checks

From the repository root:

    export VLLM_API_KEY="<generation-key-or-empty>"
    export EMBEDDING_API_KEY="<embedding-key-or-empty>"

    python scripts/provider_probe.py \
      --base-url "$VLLM_BASE_URL" \
      --chat-model "$VLLM_MODEL" \
      --embedding-model "$EMBEDDING_MODEL" \
      --embedding-dimension "$EMBEDDING_DIMENSION"

The probe checks:

- chat completions;
- prompt-token logprobs;
- embeddings;
- embedding dimension;
- basic operation latency.

The keys are read from the environment. They are not written to source files.

## 6. Use the private GraphRAG UI from your laptop

With the VPN connected, create a local SSH tunnel:

    ssh -N \
      -L 18000:127.0.0.1:8000 \
      <HPC_USER>@<HPC_HOST>

Then open:

    http://127.0.0.1:18000/

The GraphRAG service remains on the HPC machine's loopback interface.

For a login/bastion path:

    ssh -N \
      -J <HPC_USER>@<LOGIN_HOST> \
      -L 18000:127.0.0.1:8000 \
      <HPC_USER>@<COMPUTE_HOST>

## 7. Run the application probes

From your laptop:

    TOKEN="<tenant-jwt>"

    python scripts/runtime_probe.py \
      --base-url http://127.0.0.1:18000 \
      --token "$TOKEN" \
      --tenant "<TENANT_ID>" \
      --query "representative question"

    python scripts/mcp_probe.py \
      --url http://127.0.0.1:18000/mcp/ \
      --token "$TOKEN" \
      --tenant "<TENANT_ID>" \
      --query "representative question"

The SSH tunnel only moves the HTTP connection. JWT authentication is still handled by GraphRAG.

## 8. Private deployment notes

Keep both services private whenever possible.

Do not put these in the repository:

- API keys;
- JWTs;
- SSH private keys;
- private datasets;
- service credentials.

For production GraphRAG, use the enterprise identity provider and JWKS mode rather than the development token command.

## 9. Evidence to keep

For a real provider run, save:

- the `/v1/models` response with private identifiers removed if needed;
- provider probe JSON;
- runtime probe JSON;
- MCP probe JSON;
- the model and embedding identifiers;
- the measured embedding dimension;
- the configuration used for the run.

Do not use small checked-in fixture metrics as production latency or accuracy claims.
