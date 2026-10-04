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

## 0. HPC network bootstrap

On this HPC environment, network access is enabled by importing `core_config.py` from your home directory. This must happen before any network-dependent command in a new compute-node shell, including model downloads, `curl`, `git`, `pip`, or GitHub runner commands.

Run:

    source "$HOME/Conda/bin/activate"
    cd "$HOME"
    python -c "import core_config"

Keep that bootstrap in effect for the shell or process that performs the network operation. The repository provides executable wrappers that run the import in the same process before starting the command:

    ./scripts/with_hpc_network.sh <network-command> [arguments...]

For the GitHub runner, use `scripts/configure_hpc_runner.sh` and `scripts/start_hpc_runner.sh` so the runner itself inherits the bootstrapped environment.

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


## 10. GitHub Actions A100 runner

The repository now includes `.github/workflows/gpu-validation.yml`. It is designed for a long-lived compute allocation where you manage the Slurm allocation and keep the runner process alive.

The GPU workflow is intentionally separate from normal CI. It targets a custom `gpu-a100` self-hosted runner label, uses `contents: read`, disables checkout credential persistence, and does not run automatically on pull requests.

GitHub self-hosted runners connect outbound to GitHub over HTTPS and can be routed by custom labels. GitHub also warns that self-hosted runners are not isolated clean environments and strongly recommends using them only with private repositories; for this public repository, keep the GPU workflow owner-gated and never put credentials in the repository or in checked-out files. See the GitHub Actions self-hosted runner security guidance.

### Register the runner

On GitHub, open:

    Repository Settings -> Actions -> Runners -> New self-hosted runner

Choose Linux / x64 and follow GitHub's generated commands for downloading and configuring the runner. Do not paste the one-time registration token into this repository or into chat.

During registration, add the custom label:

    gpu-a100

A repository-level runner will also receive the standard `self-hosted`, `linux`, and `x64` labels.

On the compute node, a typical persistent session is:

    mkdir -p ~/gpu/actions-runner-enterprise-graphrag
    cd ~/gpu/actions-runner-enterprise-graphrag

### HPC network bootstrap

On this compute node, network access is available only after the site's `core_config` module has been imported. This must happen before any command that performs network access.

The required bootstrap is:

    source "$HOME/Conda/bin/activate"
    cd "$HOME"
    python -c "import core_config"

Run that first in the shell that will perform GitHub runner setup and in the shell that will start the runner. Do not put a network-dependent command before it.

For the checked-out repository, the generic network wrapper can be used for individual commands:

    ./scripts/with_hpc_network.sh <network-command> [arguments...]

For example:

    ./scripts/with_hpc_network.sh curl -I https://github.com

The runner process should inherit the environment/configuration established by this bootstrap. GitHub's runner itself requires outbound HTTPS connectivity, so this bootstrap must also be in effect before `./config.sh` or `./run.sh` is started.

Keep the runner process alive for the duration of your allocated compute session:

    ./run.sh

Using `tmux` is appropriate if your interactive shell may disconnect:

    tmux new -s graphrag-runner
    ./run.sh

The repository also provides executable wrappers that perform the Conda activation and mandatory `core_config` import before starting the runner:

    ./scripts/configure_hpc_runner.sh --url https://github.com/SpryzenHell/enterprise_graphrag --token <one-time-token> --labels gpu-a100
    ./scripts/start_hpc_runner.sh
    ./scripts/with_hpc_network.sh <network-command> [arguments...]

The runner must be connected and show as `Idle` in GitHub before a GPU job can be assigned.

Before registering, verify outbound connectivity from the compute node:

    ./scripts/with_hpc_network.sh curl -I https://github.com

GitHub's runner application also provides a configuration connectivity check:

    ./config.sh --check --url https://github.com/SpryzenHell/enterprise_graphrag

### Prepare the Conda environment

Use a dedicated environment for vLLM + this runtime so the existing `phase1`, `phase1_ltx`, `phase2_3d`, `phase2_orchestrator`, and `oec_deploy` environments remain untouched.

The GPU workflow defaults to:

    GRAGRAPH_CONDA_ENV=graphrag_vllm

The runner workflow expects the Conda installation used in your current setup to be available at:

    $HOME/Conda

Inside the environment, install vLLM and the repository's Python dependencies. Then verify:

    source "$HOME/Conda/bin/activate"
    conda activate graphrag_vllm
    vllm --version
    python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"

The workflow itself does not start vLLM because the model path, model ID, GPU placement, and serving options are deployment-specific. Start the private vLLM server on the compute node, preferably bound to loopback:

    vllm serve <CHAT_MODEL> --host 127.0.0.1 --port 8001

Then verify:

    curl http://127.0.0.1:8001/v1/models

### What the GPU workflow actually tests

The GPU job is not just an installation check. It validates:

    1. NVIDIA GPU visibility through nvidia-smi
    2. CUDA availability through PyTorch
    3. expected A100 hardware family and compute capability
    4. the vLLM /v1/models contract
    5. a real /v1/chat/completions request
    6. a real /v1/completions prompt_logprobs + prompt_token_ids response
    7. optional real /v1/embeddings validation, including dimension and finite values
    8. the normal deterministic GraphRAG test suite
    9. a real GPU-backed GraphRAG query through VllmAnswerModel
    10. tenant isolation and retrieved-content injection blocking during that query

The workflow writes `gpu-validation.json` and a JUnit test report, then uploads both as GitHub Actions artifacts.

The tests deliberately avoid hard-coding generation text, latency, or throughput thresholds. Those properties vary by model, quantization, batch size, and server configuration. The current checks instead assert protocol correctness, non-empty generation, finite logprobs, CUDA visibility, retrieval correctness, tenant isolation, and security-boundary behavior.

### Triggering the GPU validation

On the current revamp branch, owner pushes automatically queue the GPU job. Manual `workflow_dispatch` is also available. The job is restricted to the current revamp branch and repository owner so ordinary pull requests cannot execute code on the self-hosted GPU runner.

Use the GitHub Actions run result as the canonical record of whether the real compute-node validation passed.


### Important HPC network rule

Do not run `curl`, `wget`, `pip install`, `git fetch`, GitHub runner configuration, or other network-dependent commands on the compute node before:

    python -c "import core_config"

Treat `import core_config` as the first network-enabling step in every new compute-node shell. The repository workflow cannot retroactively bootstrap the GitHub runner's own network connection because runner communication and checkout happen before workflow steps; bootstrap the runner's parent shell/process first.
