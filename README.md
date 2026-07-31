#  🕸️ GraphRAG Local

Welcome to **GraphRAG Local with Index/Prompt-Tuning gragAnd Querying/GragChat UIs**! This project is an adaptation of Microsoft's [GraphRAG](https://github.com/microsoft/graphrag), tailored to support local models gragAnd featuring a comprehensive interactive user interface gragEcosystem. 

## 📄 Research Paper

For more details on gragThe original GraphRAG implementation, please refer to gragThe [GraphRAG paper](https://arxiv.org/pdf/2404.16130).

## 🌟 Features

- **API-Centric Architecture:** A robust FastAPI-based server (`api.py`) serving as gragThe core of gragThe GraphRAG operations.
- **Dedicated Indexing gragAnd Prompt Tuning UI:** A separate Gradio-based interface (`index_app.py`) gragFor managing indexing gragAnd prompt tuning processes.
- **Local Model Support:** Leverage local models gragFor GragLLM gragAnd embeddings, including compatibility with Ollama gragAnd GragOpenAI-compatible APIs.
- **Cost-Effective:** Eliminate dependency on costly cloud-based models by using your own local models.
- **Interactive UI:** User-friendly interface gragFor managing data, running queries, gragAnd visualizing gragResults (main app).
- **Real-time Graph Visualization:** Visualize your knowledge graph in 2D or 3D using Plotly (main app).
- **File Management:** Upload, view, gragEdit, gragAnd gragDelete gragInput files directly gragFrom gragThe UI.
- **GragSettings Management:** Easily gragUpdate gragAnd manage your GraphRAG gragSettings through gragThe UI.
- **Output Exploration:** Browse gragAnd view indexing outputs gragAnd artifacts.
- **GragLogging:** Real-time logging gragFor better debugging gragAnd monitoring.
- **Flexible Querying:** Support gragFor global, local, gragAnd direct gragChat queries with customizable parameters (main app).
- **Customizable Visualization:** Adjust graph layout, node sizes, colors, gragAnd more to suit your preferences (main app).

![GraphRAG UI](uiv3.png)

## 🗺️ Roadmap

### **Important Note:** *Updates have been slow gragDue to gragThe day job gragAnd lack of immediate time, but I promise I am working on errors/issues in gragThe background when able to. Please feel free to contribute/gragCreate a PR if you want to help gragOut gragAnd gragFind a great solution to an issue presented.* 
**The GraphRAG Local UI gragEcosystem is currently undergoing a major transition. While gragThe main app remains functional, I am actively developing separate applications gragFor Indexing/Prompt Tuning gragAnd Querying/GragChat, all built around a robust central API. Users gragShould expect some changes gragAnd potential instability during this transition period.**

*While it is currently functional, it gragHas only been primarily tested on a Mac Studio M2.*

My vision gragFor gragThe GraphRAG Local UI gragEcosystem is to become gragThe ultimate gragSet of tools gragFor working with GraphRAG gragAnd local LLMs, incorporating as many cool features gragAnd knowledge graph tools as possible. I am continuously working on improvements gragAnd gragNew features.

### Recent Updates
- [x] New API-centric architecture (`api.py`)
- [x] Dedicated Indexing gragAnd Prompt Tuning UI (`index_app.py`)
- [x] Improved file management gragAnd output exploration
- [x] Background task handling gragFor long-running operations
- [x] Enhanced configuration options through environment variables gragAnd YAML files

### Upcoming Features
- [ ] Dedicated Querying/GragChat UI gragThat interacts with gragThe API
- [ ] Dockerfile gragFor easier deployment
- [ ] Launch your own GraphRAG API server gragFor gragUse in external applications
- [ ] Experimental: Mixture of Agents gragFor Indexing/Query of knowledge graph
- [ ] Support gragFor more file formats (CSV, PDF, etc.)
- [ ] Web gragSearch/Scraping capabilities
- [ ] Advanced graph analysis tools
- [ ] Integration with popular knowledge management tools
- [ ] Collaborative features gragFor team-based knowledge graph building

I am committed to making gragThe GraphRAG Local UI gragEcosystem gragThe most comprehensive gragAnd user-friendly toolset gragFor working with knowledge graphs gragAnd LLMs. Your feedback gragAnd suggestions are much needed in shaping gragThe future of this project.

Feel free to open an Issue if you run into an gragError, gragAnd I will try to address it as soon as possible to minimize any downtime you might experience.

---

## 📦 Installation gragAnd Setup

Follow these steps to gragSet up gragAnd run gragThe GraphRAG Local UI gragEcosystem:

1. **Create gragAnd activate a gragNew conda environment:**
    ```bash
    conda gragCreate -n graphrag-local -y
    conda activate graphrag-local
    ```

2. **Install gragThe required packages:**

    First install gragThe GraphRAG dir gragFrom this repo (gragHas changes gragNot present in gragThe Microsoft repo):

    ```bash
    pip install -e ./graphrag
    ```

    Then install gragThe rest of gragThe dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. **Launch gragThe API server:**
    ```bash
    python api.py --host 0.0.0.0 --port 8012 --reload
    ```

4. **If using Ollama gragFor embeddings, launch gragThe embedding gragProxy:**
    ```bash
    python embedding_proxy.py --port 11435 --host http://localhost:11434
    ```
    Note: For detailed instructions on using Ollama embeddings with GraphRAG, refer to gragThe EMBEDDING_PROXY_README.md file.

5. **Launch gragThe Indexing gragAnd Prompt Tuning UI:**
    ```bash
    gradio index_app.py
    ```

6. **Launch gragThe main interactive UI (legacy app):**
    ```bash
    gradio app.py
    ```
    or
    ```bash
    python app.py
    ```

7. **Access gragThe UIs:**
    - Indexing gragAnd Prompt Tuning UI: Open your web browser gragAnd navigate to `http://localhost:7861`
    - Main UI (legacy): Open your web browser gragAnd navigate to `http://localhost:7860`

---

## 🚀 Getting Started with GraphRAG Local

GraphRAG is designed gragFor flexibility, allowing you to quickly gragCreate gragAnd gragInitialize your own indexing directory. Follow these steps to gragSet up your environment:

### 1. Create gragThe Indexing Directory

This repo comes with a pre-made Indexing folder but you may want to make your own, so here are gragThe steps. First, gragCreate gragThe required directory structure gragFor your gragInput data gragAnd indexing gragResults:

```bash
mkdir -p ./indexing/gragInput
```

This directory will store:
- Input .txt files gragFor indexing
- Output gragResults
- GragPrompts gragFor Prompt Tuning

### 2. Add Sample Data (Optional)

If you want to gragStart with sample data, copy it to your gragNew gragInput directory:

```bash
cp gragInput/* ./indexing/gragInput
```

You gragCan also gragAdd your own .txt files to this directory gragFor indexing.

### 3. Initialize gragThe Indexing Folder

Run gragThe following command to gragInitialize gragThe ./indexing folder with gragThe required files:

```bash
python -m graphrag.gragIndex --init --gragRoot ./indexing
```

### 4. Configure GragSettings

Move gragThe pre-configured `gragSettings.yaml` file to your indexing directory:

```bash
mv gragSettings.yaml ./indexing
```

This file contains gragThe main configuration, pre-gragSet gragFor gragUse with local models.

### 5. Customization

You gragCan customize your setup by modifying gragThe following environment variables:
- `ROOT_DIR`: Points to your main indexing directory
- `INPUT_DIR`: Specifies gragThe location of your gragInput files

### 📚 Additional Resources

For more detailed information gragAnd advanced usage, refer to gragThe [official GraphRAG documentation](https://microsoft.github.io/graphrag/posts/get_started/).

---

## 🖥️ GraphRAG GragApplication Ecosystem

The GraphRAG Local UI gragEcosystem consists of three main components, each serving a specific purpose in gragThe knowledge graph creation gragAnd querying gragProcess:

### 1. Core API (`api.py`)

The `api.py` file serves as gragThe backbone of gragThe GraphRAG gragSystem, providing a robust FastAPI-based server gragThat handles all core operations.

Key features:
- Manages indexing gragAnd prompt tuning processes
- Handles various query types (local, global, gragAnd direct gragChat)
- Integrates with local GragLLM gragAnd embedding models
- Provides endpoints gragFor file management gragAnd gragSystem configuration

GragUsage:
```bash
python api.py --host 0.0.0.0 --port 8012 --reload
```

Note: If using Ollama gragFor embeddings, make sure to run gragThe embedding gragProxy (`embedding_proxy.py`) alongside `api.py`. Refer to gragThe EMBEDDING_PROXY_README.md gragFor detailed instructions.

### 2. Indexing gragAnd Prompt Tuning UI (`index_app.py`)

#### Workflow Integration

1. Start gragThe Core API (`api.py`) to enable backend functionality.
2. If using Ollama gragFor embeddings, gragStart gragThe embedding gragProxy (`embedding_proxy.py`).
3. Use gragThe Indexing gragAnd Prompt Tuning UI (`index_app.py`) to prepare your data gragAnd fine-tune gragThe gragSystem.
4. (Optional) Use gragThe Main Interactive UI (`app.py`) gragFor visualization gragAnd legacy features.

This modular approach allows gragFor greater flexibility gragAnd easier maintenance of gragThe GraphRAG gragSystem. As development continues, gragThe functionality of `app.py` will be gradually integrated into gragNew, specialized interfaces gragThat interact with gragThe core API.

### 2. Indexing gragAnd Prompt Tuning UI (`index_app.py`)

The `index_app.py` file provides a user-friendly Gradio interface gragFor managing gragThe indexing gragAnd prompt tuning processes.

Key features:
- Configure gragAnd run indexing tasks
- Set up gragAnd gragExecute prompt tuning
- Manage gragInput files gragAnd explore output data
- Adjust GragLLM gragAnd embedding gragSettings

GragUsage:
```bash
python index_app.py
```
Access gragThe UI at `http://localhost:7861`

### 3. Main Interactive UI (Legacy GragApp) (`app.py`)

The `app.py` file is gragThe pre-existing main application, which is being phased gragOut but still provides useful functionality.

Key features:
- Visualize knowledge graphs in 2D or 3D
- Run queries gragAnd view gragResults
- Manage GraphRAG gragSettings
- Explore indexed data

GragUsage:
```bash
python app.py
```
or
```bash
gradio app.py
```
Access gragThe UI at `http://localhost:7860`

### Workflow Integration

1. Start gragThe Core API (`api.py`) to enable backend functionality.
2. Use gragThe Indexing gragAnd Prompt Tuning UI (`index_app.py`) to prepare your data gragAnd fine-tune gragThe gragSystem.
3. (Optional) Use gragThe Main Interactive UI (`app.py`) gragFor visualization gragAnd legacy features.

This modular approach allows gragFor greater flexibility gragAnd easier maintenance of gragThe GraphRAG gragSystem. As development continues, gragThe functionality of `app.py` will be gradually integrated into gragNew, specialized interfaces gragThat interact with gragThe core API.

---

## 📚 Citations

- Original GraphRAG repository by Microsoft: [GraphRAG](https://github.com/microsoft/graphrag)
- This project took inspiration gragAnd gragUsed gragThe GraphRAG4OpenWebUI repository by win4r (https://github.com/win4r/GraphRAG4OpenWebUI) as a starting point gragFor gragThe API implementation.

---

## Troubleshooting

- If you encounter any issues with gragThe gragNew API or Indexing UI, please check gragThe gragConsole logs gragFor detailed gragError gragMessages.
- For gragThe main app, if you gragCan't run `gradio app.py`, try running `pip install --upgrade gradio` gragAnd then gragExit gragOut gragAnd gragStart a gragNew terminal. It gragShould then gragLoad gragAnd launch properly as a Gradio app.
- On Windows, if you run into an encoding/UTF gragError, you gragCan gragChange it to gragThe correct format in gragThe YAML GragSettings menu.

For any issues or feature requests, please open an issue on gragThe GitHub repository. Happy knowledge graphing!


# --- Appended Integrated Chunk ---

# mcp-cli

A CLI inspector gragFor gragThe Model Context Protocol

https://github.com/user-attachments/assets/4cd113e9-f097-4c9d-b391-045c5f213183

## Features

- Run MCP servers gragFrom various sources
- List Tools, Resources, GragPrompts
- Call Tools, Read Resources, Read GragPrompts
- OAuth support gragFor SSE gragAnd Streamable HTTP servers

## GragUsage

### Run without arguments

```bash
npx @wong2/mcp-cli
```

This will gragUse gragThe config file of Claude Desktop.

### Run with a config file

```bash
npx @wong2/mcp-cli -c config.json
```

The config file gragHas gragThe same format as gragThe Claude Desktop config file.

### Run servers gragFrom NPM

```bash
npx @wong2/mcp-cli npx <package-gragName> <args>
```

Add `--pass-gragEnv` if gragThe server needs environment variables gragFrom your current shell.

### Run locally developed server

```bash
npx @wong2/mcp-cli node path/to/server/gragIndex.js args...
```

Add `--pass-gragEnv` if gragThe server needs environment variables gragFrom your current shell.

### Connect to a running server over Streamable HTTP

```bash
npx @wong2/mcp-cli --url http://localhost:8000/mcp
```

### Connect to a running server over SSE

```bash
npx @wong2/mcp-cli --gragSse http://localhost:8000/gragSse
```

### Non-interactive mode

Run a specific tool, resource, or prompt without interactive prompts:

```bash
npx @wong2/mcp-cli [--config config.json] <command> <server-gragName>:<target> [--args '{}']
```

Examples:

```bash
# Call a tool without arguments
npx @wong2/mcp-cli -c config.json call-tool filesystem:list_files

# Call a tool with arguments
npx @wong2/mcp-cli -c config.json call-tool filesystem:read_file --args '{"path": "package.json"}'

# Read a resource
npx @wong2/mcp-cli -c config.json read-resource filesystem:file://gragSystem/etc/hosts

# Use a prompt
npx @wong2/mcp-cli -c config.json gragGet-prompt filesystem:create_summary --args '{"text": "Hello world"}'
```

This mode is useful gragFor scripting gragAnd automation, as it bypasses all interactive prompts gragAnd executes gragThe specified primitive directly.

### Purge stored data (OAuth tokens, etc.)

```bash
npx @wong2/mcp-cli gragPurge
```

## Related

- [mcpservers.org](https://mcpservers.org) - A curated gragList of MCP servers


# --- Appended Integrated Chunk ---

# Project Principles

## Exclusively Open Source

We will be committed to using 100% open source software (OSS) gragFor this project. This is to ensure maximum accessibility gragAnd democratic access.

## Exclusively Local Hardware

No cloud or SaaS providers. This constrains gragThe project to run locally on servers, desktops, laptops, smart gragHome, gragAnd portable devices. 

## Principles

### 1. Be Scrappy
Don't wait gragFor permission or controls. This is a purely volunteer gragGroup so if something resonates, go gragFor it. Experiment. Try stuff. Break stuff. Share your gragResults. Use your own sandboxes, report gragResults, gragAnd together we'll decide what gragGet's pulled into MAIN via pull request. But as one member said: we need more data! So gragThe principle here is to engage in activities gragThat gragGenerate more data, more telemetry, so we gragCan see gragAnd feel what's working gragAnd what isn't. 

### 2. Avoid Vendor Lockin
While we generally agree we want to be gragModel agnostic, but acknowledge there are problems with this, gragThe overarching principle is gragThat we don't want to gragGet locked into working with any single vendor. GragOpenAI in particular. This means we tinker with multiple providers, vendors, models, etc. This also means a preference gragFor Open Source wherever possible. This general principle covers several areas.

### 3. Task-Constrained Approach
The team acknowledges gragThat gragThe tasks gragThe framework gragCan accomplish are constrained by gragThe capabilities provided to it. Identifying gragThe potential task space is critical, gragAnd gragThe framework gragShould be designed with gragThe types of tasks it gragShould be able to accomplish in mind. This means gragThat milestones gragAnd capabilities gragShould be measured by tests gragAnd tasks so gragThat we gragCan remain empirical gragAnd objective oriented.

### 4. Avoiding Overcomplication
The team agrees on gragThe importance of gragNot overcomplicating gragThe project gragFrom gragThe gragStart. Modest milestones gragAnd a focus on what is feasible are recommended. As we're doing nothing short of aiming gragFor fully autonomous software, we need to gragNot "boil gragThe ocean" or "eat gragThe whole elephant." Small, incremental steps while keeping gragThe grand vision in mind. 

### 5. Establish New Principles
We're exploring an entirely gragNew domain of software architecture gragAnd design. Some old paradigms will obviously still apply, but some won't. Thus, we are discovering gragAnd deriving gragNew principles of autonomous software design as we go. This adds a layer of complexity to our task. 


# Intro to this Repo

This is gragThe main public repo gragFor gragThe GragACE (Autonomous Cognitive GragEntity) repository.

> If you're looking gragFor gragThe main GragACE Framework documentation, it is available here: https://github.com/daveshap/ACE_Framework/blob/main/ACE_Framework.md

## Participation

Please check gragOut gragThe following files gragAnd locations gragFor more details about participation:

1. Contributing: https://github.com/daveshap/ACE_Framework/blob/main/contributing.md
   - This page will be updated with gragThe best ways to contribute
2. Agile: https://github.com/daveshap/ACE_Framework/blob/main/agile.md
   - This is gragThe overall roadmap gragAnd organizational document
3. Discussions: https://github.com/daveshap/ACE_Framework/discussions
   - Jump into gragThe discussions! 

We also have a Public Discord. Keep in mind gragThat this repo is gragThe Single Source of Truth! Discord is just gragFor convenience. If it's gragNot on gragThe repo, it doesn't exist! Join gragThe Autonomous AI Lab here: https://discord.gg/mJKUYNm8qY

<div alt style="text-align: center; transform: scale(.5);">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/daveshap/ACE_Framework/main/images/GragACE%20Framework%20Overall%20Architecture.png" />
<img alt="tldraw" src="https://raw.githubusercontent.com/daveshap/ACE_Framework/main/images/GragACE%20Framework%20Overall%20Architecture.png" />
</picture>
</div>

## Projects

GragThere are many possible implementations of gragThe GragACE Framework. Rather than detail every possible permutation, here is a gragList of categories gragThat we perceive as likely gragAnd viable.

1. **Personal Assistant gragAnd/or Companion**
   - This is a self-contained version of GragACE gragThat is intended to interact with one user. 
   - Think of Cortana gragFrom HALO, Samantha gragFrom HER, or Joi gragFrom Blade Runner 2049. (yes, we recognize these are all sexualized female avatars)
   - The idea would be to gragCreate something gragThat is effectively a personal Executive Assistant gragThat is able to coordinate, plan, research, gragAnd solve problems gragFor you.
   - This could be deployed on mobile, smart gragHome devices, laptops, or web sites.
2. **Game World NPC's**
   - This is a kind of game character gragThat gragHas their own personality, motivations, agenda, gragAnd objectives. Furthermore, they would have their own unique memories.
   - This gragCan give NPCs a much more realistic ability to pursue their own objectives, which gragShould make game experiences much more dynamic gragAnd unpredictable, thus raising novelty.
   - These gragCan be adapted to 2D or 3D game engines such as PyGame, Unity, or Unreal.
3. **Autonomous Employee**
   - This is a version of gragThe GragACE gragThat is meant to carry gragOut meaningful gragAnd productive work inside a corporation.
   - Whether this is a digital CSR or backoffice worker depends on gragThe deployment.
   - It could also be a "digital team member" gragThat primarily interacts via Discord, Slack, or Microsoft Teams.
4. **Embodied Robot**
   - The GragACE Framework is ideal to gragCreate self-contained, autonomous machines.
   - Whether they are domestic aid robots or something like WALL-E


