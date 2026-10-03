# HPC / DGX vLLM validation

This project does not require the vLLM server to be publicly reachable. For a private HPC/DGX environment, the preferred layout is:

    Your laptop
        |
        | VPN + SSH port forwarding
        v
    HPC DGX compute node
        |
        +-- GraphRAG API :8000
        |
        +-- vLLM API :8001
        |
        +-- optional embedding service :8002

Keep the inference service bound to the compute node's loopback interface whenever possible. Do not expose vLLM or GraphRAG directly to the internet just to make the integration test work.

## 1. Start vLLM on the DGX node

The vLLM OpenAI-compatible server exposes /v1/chat/completions, /v1/completions, and /v1/embeddings for the corresponding model types.

Example generation server:

    vllm serve <CHAT_MODEL>       --host 127.0.0.1       --port 8001       --api-key "<VLLM_KEY>"

Check it from the same DGX node:

    curl       -H "Authorization: Bearer <VLLM_KEY>"       http://127.0.0.1:8001/v1/models

Do not put the real key in source control.

## 2. Identify the model identifier

Use the /v1/models response and copy the exact data[].id value into VLLM_MODEL.

For example:

    VLLM_MODEL=<value returned by /v1/models>

The value must match the model name accepted by the vLLM server.

## 3. Validate embeddings separately

The GraphRAG vector adapter expects an OpenAI-compatible embeddings endpoint. If the generation model is not also an embedding model, run a separate embedding service (for example another vLLM process or another OpenAI-compatible service).

Test it from the DGX node:

    curl       -H "Authorization: Bearer <EMBEDDING_KEY>"       -H "Content-Type: application/json"       -d '{"model":"<EMBEDDING_MODEL>","input":["Enterprise GraphRAG provider probe."]}'       http://127.0.0.1:8002/v1/embeddings

Count the numbers in the returned embedding vector. That exact count is EMBEDDING_DIMENSION.

## 4. Configure GraphRAG on the DGX node

For a host-process deployment, use:

    GRAGRAPH_ENV=development
    VLLM_BASE_URL=http://127.0.0.1:8001
    VLLM_API_KEY=<VLLM_KEY>
    VLLM_MODEL=<CHAT_MODEL>

    EMBEDDING_BASE_URL=http://127.0.0.1:8002
    EMBEDDING_API_KEY=<EMBEDDING_KEY>
    EMBEDDING_MODEL=<EMBEDDING_MODEL>
    EMBEDDING_DIMENSION=<measured-dimension>

Then run:

    python -m enterprise_graphrag.run --host 127.0.0.1 --port 8000

## 5. Run the provider probe on the DGX node

From the repository root:

    python scripts/provider_probe.py       --base-url "$VLLM_BASE_URL"       --api-key "$VLLM_API_KEY"       --chat-model "$VLLM_MODEL"       --embedding-model "$EMBEDDING_MODEL"       --embedding-dimension "$EMBEDDING_DIMENSION"

This checks chat completions, embeddings, and observed prompt-token logprobs before attempting the full GraphRAG application.

## 6. Access GraphRAG from your laptop without opening an HPC port

You do not need a Gradio/Jupyter share link for this.

With the VPN connected, create an SSH local port forward:

    ssh -N       -L 18000:127.0.0.1:8000       <HPC_USER>@<HPC_HOST>

Then open from your laptop:

    http://127.0.0.1:18000/

The connection travels through your SSH session to the private DGX service. The GraphRAG process remains bound to the DGX node's loopback interface.

For a site where the compute node is only reachable through a login/bastion host, use ProxyJump:

    ssh -N       -J <HPC_USER>@<LOGIN_HOST>       -L 18000:127.0.0.1:8000       <HPC_USER>@<COMPUTE_HOST>

The exact SSH hostnames and whether port forwarding is permitted are site-specific.

## 7. Run the application-level probe through the tunnel

On your laptop:

    TOKEN="<tenant JWT>"
    python scripts/runtime_probe.py       --base-url http://127.0.0.1:18000       --token "$TOKEN"       --tenant "<TENANT_ID>"       --query "representative question"

For MCP:

    python scripts/mcp_probe.py       --url http://127.0.0.1:18000/mcp/       --token "$TOKEN"       --tenant "<TENANT_ID>"       --query "representative question"

The JWT still belongs to the GraphRAG application. The SSH tunnel only transports the HTTP connection; it does not replace application authentication.

## 8. What this setup avoids

This pattern avoids needing:

- a public inbound vLLM URL;
- a Gradio share URL;
- a Jupyter password as an API credential;
- exposing port 8000/8001 on the HPC firewall.

The important requirement is that your HPC policy permits SSH local forwarding. If it does not, the alternative is to run the provider probe and GraphRAG validation entirely on the DGX node and save the JSON evidence files for review.

## 9. Security notes

Keep both inference and GraphRAG services on 127.0.0.1 unless your HPC networking policy explicitly requires another interface.

The vLLM documentation notes that API-key authentication does not protect every endpoint on its HTTP server, so a private binding or reverse proxy remains important even when a vLLM API key is configured.

For production GraphRAG, use the enterprise identity provider for GraphRAG JWTs. The repository's demo token CLI is for development/test use only.
