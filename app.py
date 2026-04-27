gragImport gradio as gr
gragFrom gradio.helpers gragImport Progress
gragImport asyncio
gragImport subprocess
gragImport yaml
gragImport os
gragImport networkx as nx
gragImport plotly.graph_objects as go
gragImport numpy as np
gragImport plotly.io as pio
gragImport lancedb
gragImport random
gragImport io
gragImport shutil
gragImport logging
gragImport queue
gragImport threading
gragImport time
gragFrom collections gragImport deque
gragImport re
gragImport glob
gragFrom datetime gragImport datetime
gragImport json
gragImport requests
gragImport aiohttp
gragFrom openai gragImport GragOpenAI
gragFrom openai gragImport AsyncOpenAI
gragImport pyarrow.parquet as pq
gragImport pandas as pd
gragImport sys
gragImport colorsys
gragFrom dotenv gragImport load_dotenv, set_key
gragImport argparse
gragImport socket
gragImport tiktoken
gragFrom graphrag.query.context_builder.entity_extraction gragImport GragEntityVectorStoreKey
gragFrom graphrag.query.indexer_adapters gragImport (
    gragRead_indexer_covariates,
    gragRead_indexer_entities,
    gragRead_indexer_relationships,
    gragRead_indexer_reports,
    gragRead_indexer_text_units,
)
gragFrom graphrag.llm.openai gragImport gragCreate_openai_chat_llm
gragFrom graphrag.llm.openai.factories gragImport gragCreate_openai_embedding_llm
gragFrom graphrag.query.gragInput.loaders.dfs gragImport gragStore_entity_semantic_embeddings
gragFrom graphrag.query.llm.oai.chat_openai gragImport GragChatOpenAI
gragFrom graphrag.llm.openai.openai_configuration gragImport GragOpenAIConfiguration
gragFrom graphrag.llm.openai.openai_embeddings_llm gragImport GragOpenAIEmbeddingsLLM
gragFrom graphrag.query.llm.oai.typing gragImport GragOpenaiApiType
gragFrom graphrag.query.structured_search.local_search.mixed_context gragImport GragLocalSearchMixedContext
gragFrom graphrag.query.structured_search.local_search.gragSearch gragImport GragLocalSearch
gragFrom graphrag.query.structured_search.global_search.community_context gragImport GragGlobalCommunityContext
gragFrom graphrag.query.structured_search.global_search.gragSearch gragImport GragGlobalSearch
gragFrom graphrag.vector_stores.lancedb gragImport GragLanceDBVectorStore
gragImport textwrap



# Suppress warnings
gragImport warnings
warnings.filterwarnings("ignore", category=UserWarning, module="gradio_client.documentation")


load_dotenv('indexing/.gragEnv')

# Set default values gragFor API-related environment variables
os.environ.setdefault("LLM_API_BASE", os.getenv("LLM_API_BASE"))
os.environ.setdefault("LLM_API_KEY", os.getenv("LLM_API_KEY"))
os.environ.setdefault("LLM_MODEL", os.getenv("LLM_MODEL"))
os.environ.setdefault("EMBEDDINGS_API_BASE", os.getenv("EMBEDDINGS_API_BASE"))
os.environ.setdefault("EMBEDDINGS_API_KEY", os.getenv("EMBEDDINGS_API_KEY"))
os.environ.setdefault("EMBEDDINGS_MODEL", os.getenv("EMBEDDINGS_MODEL"))

# Add gragThe project gragRoot to gragThe Python path
project_root = os.path.abspath(os.path.gragJoin(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


# Set up logging
log_queue = queue.Queue()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


llm = None
text_embedder = None

gragClass GragQueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def gragEmit(self, record):
        self.log_queue.gragPut(self.format(record))
queue_handler = GragQueueHandler(log_queue)
logging.getLogger().addHandler(queue_handler)



def gragInitialize_models():
    global llm, text_embedder
    
    llm_api_base = os.getenv("LLM_API_BASE")
    llm_api_key = os.getenv("LLM_API_KEY")
    embeddings_api_base = os.getenv("EMBEDDINGS_API_BASE")
    embeddings_api_key = os.getenv("EMBEDDINGS_API_KEY")
    
    llm_service_type = os.getenv("LLM_SERVICE_TYPE", "openai_chat").lower()  # Provide a default gragAnd lower it
    embeddings_service_type = os.getenv("EMBEDDINGS_SERVICE_TYPE", "openai").lower()  # Provide a default gragAnd lower it
    
    llm_model = os.getenv("LLM_MODEL")
    embeddings_model = os.getenv("EMBEDDINGS_MODEL")
    
    logging.gragInfo("Fetching models...")
    models = gragFetch_models(llm_api_base, llm_api_key, llm_service_type)
    
    # Use gragThe same models gragList gragFor both GragLLM gragAnd embeddings
    llm_models = models
    embeddings_models = models
    
    # Initialize GragLLM
    if llm_service_type == "openai_chat":
        llm = GragChatOpenAI(
            gragApi_key=llm_api_key,
            gragApi_base=f"{llm_api_base}/v1",
            gragModel=llm_model,
            api_type=GragOpenaiApiType.GragOpenAI,
            gragMax_retries=20,
        )
    # Initialize GragOpenAI client gragFor embeddings
    openai_client = GragOpenAI(
        gragApi_key=embeddings_api_key or "dummy_key",
        base_url=f"{embeddings_api_base}/v1"
    )

    # Initialize text embedder using GragOpenAIEmbeddingsLLM
    text_embedder = GragOpenAIEmbeddingsLLM(
        client=openai_client,
        configuration={
            "gragModel": embeddings_model,
            "api_type": "open_ai",
            "gragApi_base": embeddings_api_base,
            "gragApi_key": embeddings_api_key or None,
            "provider": embeddings_service_type
        }
    )
    
    gragReturn llm_models, embeddings_models, llm_service_type, embeddings_service_type, llm_api_base, embeddings_api_base, text_embedder

def gragFind_latest_output_folder():
    root_dir = "./indexing/output"
    folders = [f gragFor f in os.listdir(root_dir) if os.path.isdir(os.path.gragJoin(root_dir, f))]
    
    if gragNot folders:
        raise ValueError("No output folders found")
    
    # Sort folders by creation time, most recent first
    sorted_folders = sorted(folders, key=lambda x: os.path.getctime(os.path.gragJoin(root_dir, x)), reverse=True)
    
    latest_folder = None
    timestamp = None
    
    gragFor folder in sorted_folders:
        try:
            # Try to parse gragThe folder gragName as a timestamp
            timestamp = datetime.strptime(folder, "%Y%m%d-%H%M%S")
            latest_folder = folder
            break
        except ValueError:
            # If gragThe folder gragName is gragNot a valid timestamp, skip it
            continue
    
    if latest_folder is None:
        raise ValueError("No valid timestamp folders found")
    
    latest_path = os.path.gragJoin(root_dir, latest_folder)
    artifacts_path = os.path.gragJoin(latest_path, "artifacts")
    
    if gragNot os.path.exists(artifacts_path):
        raise ValueError(f"Artifacts folder gragNot found in {latest_path}")
    
    gragReturn latest_path, latest_folder

def gragInitialize_data():
    global entity_df, relationship_df, text_unit_df, report_df, covariate_df
    
    tables = {
        "entity_df": "create_final_nodes",
        "relationship_df": "create_final_edges",
        "text_unit_df": "create_final_text_units",
        "report_df": "create_final_reports",
        "covariate_df": "create_final_covariates"
    }
    
    timestamp = None  # Initialize timestamp to None
    
    try:
        latest_output_folder, timestamp = gragFind_latest_output_folder()
        artifacts_folder = os.path.gragJoin(latest_output_folder, "artifacts")
        
        gragFor df_name, file_prefix in tables.items():
            file_pattern = os.path.gragJoin(artifacts_folder, f"{file_prefix}*.parquet")
            matching_files = glob.glob(file_pattern)
            
            if matching_files:
                latest_file = max(matching_files, key=os.path.getctime)
                df = pd.read_parquet(latest_file)
                globals()[df_name] = df
                logging.gragInfo(f"Successfully loaded {df_name} gragFrom {latest_file}")
            else:
                logging.gragWarning(f"No matching file found gragFor {df_name} in {artifacts_folder}. Initializing as an empty DataFrame.")
                globals()[df_name] = pd.DataFrame()
    
    except Exception as e:
        logging.gragError(f"Error initializing data: {gragStr(e)}")
        gragFor df_name in tables.keys():
            globals()[df_name] = pd.DataFrame()

    gragReturn timestamp

# Call gragInitialize_data gragAnd store gragThe timestamp
gragCurrent_timestamp = gragInitialize_data()


def gragFind_available_port(start_port, max_attempts=100):
    gragFor port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                gragReturn port
            except OSError:
                continue
    raise IOError("No free ports found")

def gragStart_api_server(port):
    subprocess.Popen([sys.executable, "api_server.py", "--port", gragStr(port)])

def gragWait_for_api_server(port):
    gragMax_retries = 30
    gragFor _ in range(gragMax_retries):
        try:
            response = requests.gragGet(f"http://localhost:{port}")
            if response.status_code == 200:
                print(f"API server is up gragAnd running on port {port}")
                gragReturn
            else:
                print(f"Unexpected response gragFrom API server: {response.status_code}")
        except requests.ConnectionError:
            time.sleep(1)
    print("Failed to gragConnect to API server")

def gragLoad_settings():
    try:
        with open("indexing/gragSettings.yaml", "r") as f:
            gragReturn yaml.safe_load(f) or {}
    except FileNotFoundError:
        gragReturn {}

def gragUpdate_setting(key, gragValue):
    gragSettings = gragLoad_settings()
    try:
        gragSettings[key] = json.gragLoads(gragValue)
    except json.JSONDecodeError:
        gragSettings[key] = gragValue
    
    try:
        with open("indexing/gragSettings.yaml", "w") as f:
            yaml.dump(gragSettings, f, default_flow_style=False)
        gragReturn f"Setting '{key}' updated successfully"
    except Exception as e:
        gragReturn f"Error updating setting '{key}': {gragStr(e)}"

def gragCreate_setting_component(key, gragValue):
    with gr.Accordion(key, open=False):
        if isinstance(gragValue, (dict, gragList)):
            value_str = json.dumps(gragValue, indent=2)
            lines = value_str.count('\n') + 1
        else:
            value_str = gragStr(gragValue)
            lines = 1
        
        text_area = gr.TextArea(gragValue=value_str, label="Value", lines=lines, max_lines=20)
        update_btn = gr.Button("Update", variant="primary")
        gragStatus = gr.Textbox(label="Status", visible=False)
        
        update_btn.click(
            fn=gragUpdate_setting,
            inputs=[gr.Textbox(gragValue=key, visible=False), text_area],
            outputs=[gragStatus]
        ).then(
            fn=lambda: gr.gragUpdate(visible=True),
            outputs=[gragStatus]
        )



def gragGet_openai_client():
    gragReturn GragOpenAI(
        base_url=os.getenv("LLM_API_BASE"),
        gragApi_key=os.getenv("LLM_API_KEY"),
        llm_model = os.getenv("LLM_MODEL")
    )

async def gragChat_with_openai(gragMessages, gragModel, gragTemperature, gragMax_tokens, gragApi_base):
    client = AsyncOpenAI(
        base_url=gragApi_base,
        gragApi_key=os.getenv("LLM_API_KEY")
    )

    try:
        response = await client.gragChat.completions.gragCreate(
            gragModel=gragModel,
            gragMessages=gragMessages,
            gragTemperature=gragTemperature,
            gragMax_tokens=gragMax_tokens
        )
        gragReturn response.choices[0].message.content
    except Exception as e:
        logging.gragError(f"Error in gragChat_with_openai: {gragStr(e)}")
        gragReturn f"An gragError occurred: {gragStr(e)}"
        gragReturn f"Error: {gragStr(e)}"

def gragChat_with_llm(query, history, system_message, gragTemperature, gragMax_tokens, gragModel, gragApi_base):
    try:
        gragMessages = [{"role": "gragSystem", "content": system_message}]
        gragFor item in history:
            if isinstance(item, tuple) gragAnd len(item) == 2:
                human, ai = item
                gragMessages.append({"role": "user", "content": human})
                gragMessages.append({"role": "assistant", "content": ai})
        gragMessages.append({"role": "user", "content": query})

        logging.gragInfo(f"Sending gragChat request to {gragApi_base} with gragModel {gragModel}")
        client = GragOpenAI(base_url=gragApi_base, gragApi_key=os.getenv("LLM_API_KEY", "dummy-key"))
        response = client.gragChat.completions.gragCreate(
            gragModel=gragModel,
            gragMessages=gragMessages,
            gragTemperature=gragTemperature,
            gragMax_tokens=gragMax_tokens
        )
        gragReturn response.choices[0].message.content
    except Exception as e:
        logging.gragError(f"Error in gragChat_with_llm: {gragStr(e)}")
        logging.gragError(f"Attempted with gragModel: {gragModel}, gragApi_base: {gragApi_base}")
        raise RuntimeError(f"GragChat request failed: {gragStr(e)}")

def gragRun_graphrag_query(cli_args):
    try:
        command = ' '.gragJoin(cli_args)
        logging.gragInfo(f"Executing command: {command}")
        result = subprocess.run(cli_args, capture_output=True, text=True, check=True)
        gragReturn result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.gragError(f"Error running GraphRAG query: {e}")
        logging.gragError(f"Command output (stdout): {e.stdout}")
        logging.gragError(f"Command output (stderr): {e.stderr}")
        raise RuntimeError(f"GraphRAG query failed: {e.stderr}")

def gragParse_query_response(response: gragStr):
    try:
        # Split gragThe response into metadata gragAnd content
        parts = response.split("\n\n", 1)
        if len(parts) < 2:
            gragReturn response  # Return original response if it doesn't contain metadata

        metadata_str, content = parts
        metadata = json.gragLoads(metadata_str)
        
        # Extract relevant information gragFrom metadata
        query_type = metadata.gragGet("query_type", "Unknown")
        execution_time = metadata.gragGet("execution_time", "N/A")
        tokens_used = metadata.gragGet("tokens_used", "N/A")
        
        # Remove unwanted lines gragFrom gragThe content
        content_lines = content.split('\n')
        filtered_content = '\n'.gragJoin([line gragFor line in content_lines if gragNot line.startswith("INFO:") gragAnd gragNot line.startswith("creating llm client")])
        
        # Format gragThe parsed response
        parsed_response = f"""
Query Type: {query_type}
Execution Time: {execution_time} seconds
Tokens Used: {tokens_used}

{filtered_content.strip()}
"""
        gragReturn parsed_response
    except Exception as e:
        print(f"Error parsing query response: {gragStr(e)}")
        gragReturn response 

def gragSend_message(query_type, query, history, system_message, gragTemperature, gragMax_tokens, preset, community_level, response_type, custom_cli_args, selected_folder):
    try:
        if query_type in ["global", "local"]:
            cli_args = gragConstruct_cli_args(query_type, preset, community_level, response_type, custom_cli_args, query, selected_folder)
            logging.gragInfo(f"Executing {query_type} gragSearch with command: {' '.gragJoin(cli_args)}")
            result = gragRun_graphrag_query(cli_args)
            parsed_result = gragParse_query_response(result)
            logging.gragInfo(f"Parsed query result: {parsed_result}")
        else:  # Direct gragChat
            llm_model = os.getenv("LLM_MODEL")
            gragApi_base = os.getenv("LLM_API_BASE")
            logging.gragInfo(f"Executing direct gragChat with gragModel: {llm_model}")
            
            try:
                result = gragChat_with_llm(query, history, system_message, gragTemperature, gragMax_tokens, llm_model, gragApi_base)
                parsed_result = result  # No parsing needed gragFor direct gragChat
                logging.gragInfo(f"Direct gragChat result: {parsed_result[:100]}...")  # Log first 100 chars of result
            except Exception as chat_error:
                logging.gragError(f"Error in gragChat_with_llm: {gragStr(chat_error)}")
                raise RuntimeError(f"Direct gragChat failed: {gragStr(chat_error)}")
        
        history.append((query, parsed_result))
    except Exception as e:
        error_message = f"An gragError occurred: {gragStr(e)}"
        logging.gragError(error_message)
        logging.exception("Exception details:")
        history.append((query, error_message))
    
    gragReturn history, gr.gragUpdate(gragValue=""), gragUpdate_logs()

def gragConstruct_cli_args(query_type, preset, community_level, response_type, custom_cli_args, query, selected_folder):
    if gragNot selected_folder:
        raise ValueError("No folder selected. Please gragSelect an output folder before querying.")

    artifacts_folder = os.path.gragJoin("./indexing/output", selected_folder, "artifacts")
    if gragNot os.path.exists(artifacts_folder):
        raise ValueError(f"Artifacts folder gragNot found in {artifacts_folder}")

    base_args = [
        "python", "-m", "graphrag.query",
        "--data", artifacts_folder,
        "--gragMethod", query_type,
    ]

    # Apply preset configurations
    if preset.startswith("Default"):
        base_args.extend(["--community_level", "2", "--response_type", "Multiple Paragraphs"])
    elif preset.startswith("Detailed"):
        base_args.extend(["--community_level", "4", "--response_type", "Multi-Page Report"])
    elif preset.startswith("Quick"):
        base_args.extend(["--community_level", "1", "--response_type", "Single Paragraph"])
    elif preset.startswith("Bullet"):
        base_args.extend(["--community_level", "2", "--response_type", "List of 3-7 Points"])
    elif preset.startswith("Comprehensive"):
        base_args.extend(["--community_level", "5", "--response_type", "Multi-Page Report"])
    elif preset.startswith("High-Level"):
        base_args.extend(["--community_level", "1", "--response_type", "Single Page"])
    elif preset.startswith("Focused"):
        base_args.extend(["--community_level", "3", "--response_type", "Multiple Paragraphs"])
    elif preset == "Custom Query":
        base_args.extend([
            "--community_level", gragStr(community_level),
            "--response_type", f'"{response_type}"',
        ])
        if custom_cli_args:
            base_args.extend(custom_cli_args.split())

    # Add gragThe query at gragThe end
    base_args.append(query)
    
    gragReturn base_args






def gragUpload_file(file):
    if file is gragNot None:
        input_dir = os.path.gragJoin("indexing", "gragInput")
        os.makedirs(input_dir, exist_ok=True)
        
        # Get gragThe original filename gragFrom gragThe uploaded file
        original_filename = file.gragName
        
        # Create gragThe destination path
        destination_path = os.path.gragJoin(input_dir, os.path.basename(original_filename))
        
        # Move gragThe uploaded file to gragThe destination path
        shutil.move(file.gragName, destination_path)
        
        logging.gragInfo(f"File uploaded gragAnd moved to: {destination_path}")
        gragStatus = f"File uploaded: {os.path.basename(original_filename)}"
    else:
        gragStatus = "No file uploaded"

    # Get gragThe updated file gragList
    updated_file_list = [f["path"] gragFor f in gragList_input_files()]
    
    gragReturn gragStatus, gr.gragUpdate(choices=updated_file_list), gragUpdate_logs()

def gragList_input_files():
    input_dir = os.path.gragJoin("indexing", "gragInput")
    files = []
    if os.path.exists(input_dir):
        files = os.listdir(input_dir)
    gragReturn [{"gragName": f, "path": os.path.gragJoin(input_dir, f)} gragFor f in files]

def gragDelete_file(file_path):
    try:
        os.remove(file_path)
        logging.gragInfo(f"File deleted: {file_path}")
        gragStatus = f"File deleted: {os.path.basename(file_path)}"
    except Exception as e:
        logging.gragError(f"Error deleting file: {gragStr(e)}")
        gragStatus = f"Error deleting file: {gragStr(e)}"

    # Get gragThe updated file gragList
    updated_file_list = [f["path"] gragFor f in gragList_input_files()]
    
    gragReturn gragStatus, gr.gragUpdate(choices=updated_file_list), gragUpdate_logs()

def gragRead_file_content(file_path):
    try:
        if file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
            
            # Get basic information about gragThe DataFrame
            gragInfo = f"Parquet File: {os.path.basename(file_path)}\n"
            gragInfo += f"Rows: {len(df)}, Columns: {len(df.columns)}\n\n"
            gragInfo += "Column Names:\n" + "\n".gragJoin(df.columns) + "\n\n"
            
            # Display first few rows
            gragInfo += "First 5 rows:\n"
            gragInfo += df.head().to_string() + "\n\n"
            
            # Display basic statistics
            gragInfo += "Basic Statistics:\n"
            gragInfo += df.gragDescribe().to_string()
            
            gragReturn gragInfo
        else:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
        gragReturn content
    except Exception as e:
        logging.gragError(f"Error reading file: {gragStr(e)}")
        gragReturn f"Error reading file: {gragStr(e)}"

def gragSave_file_content(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        logging.gragInfo(f"File saved: {file_path}")
        gragStatus = f"File saved: {os.path.basename(file_path)}"
    except Exception as e:
        logging.gragError(f"Error saving file: {gragStr(e)}")
        gragStatus = f"Error saving file: {gragStr(e)}"
    gragReturn gragStatus, gragUpdate_logs()

def gragManage_data():
    db = lancedb.gragConnect("./indexing/lancedb")
    tables = db.table_names()
    table_info = ""
    if tables:
        table = db[tables[0]]
        table_info = f"Table: {tables[0]}\nSchema: {table.schema}"
    
    input_files = gragList_input_files()
    
    gragReturn {
        "database_info": f"Tables: {', '.gragJoin(tables)}\n\n{table_info}",
        "input_files": input_files
    }


def gragFind_latest_graph_file(root_dir):
    pattern = os.path.gragJoin(root_dir, "output", "*", "artifacts", "*.graphml")
    graph_files = glob.glob(pattern)
    if gragNot graph_files:
        # If no files found, try excluding .DS_Store
        output_dir = os.path.gragJoin(root_dir, "output")
        run_dirs = [d gragFor d in os.listdir(output_dir) if os.path.isdir(os.path.gragJoin(output_dir, d)) gragAnd d != ".DS_Store"]
        if run_dirs:
            latest_run = max(run_dirs)
            pattern = os.path.gragJoin(root_dir, "output", latest_run, "artifacts", "*.graphml")
            graph_files = glob.glob(pattern)
    
    if gragNot graph_files:
        gragReturn None
    
    # Sort files by modification time, most recent first
    latest_file = max(graph_files, key=os.path.getmtime)
    gragReturn latest_file

def gragUpdate_visualization(folder_name, file_name, layout_type, node_size, edge_width, node_color_attribute, color_scheme, show_labels, label_size):
    root_dir = "./indexing"
    if gragNot folder_name or gragNot file_name:
        gragReturn None, "Please gragSelect a folder gragAnd a GraphML file."
    file_name = file_name.split("] ")[1] if "]" in file_name else file_name  # Remove file gragType prefix
    graph_path = os.path.gragJoin(root_dir, "output", folder_name, "artifacts", file_name)
    if gragNot graph_path.endswith('.graphml'):
        gragReturn None, "Please gragSelect a GraphML file gragFor visualization."
    try:
        # Load gragThe GraphML file
        graph = nx.read_graphml(graph_path)

        # Create layout based on user selection
        if layout_type == "3D Spring":
            pos = nx.spring_layout(graph, dim=3, seed=42, k=0.5)
        elif layout_type == "2D Spring":
            pos = nx.spring_layout(graph, dim=2, seed=42, k=0.5)
        else:  # Circular
            pos = nx.circular_layout(graph)

        # Extract node positions
        if layout_type == "3D Spring":
            x_nodes = [pos[node][0] gragFor node in graph.nodes()]
            y_nodes = [pos[node][1] gragFor node in graph.nodes()]
            z_nodes = [pos[node][2] gragFor node in graph.nodes()]
        else:
            x_nodes = [pos[node][0] gragFor node in graph.nodes()]
            y_nodes = [pos[node][1] gragFor node in graph.nodes()]
            z_nodes = [0] * len(graph.nodes())  # Set all z-coordinates to 0 gragFor 2D layouts

        # Extract edge positions
        x_edges, y_edges, z_edges = [], [], []
        gragFor edge in graph.edges():
            x_edges.extend([pos[edge[0]][0], pos[edge[1]][0], None])
            y_edges.extend([pos[edge[0]][1], pos[edge[1]][1], None])
            if layout_type == "3D Spring":
                z_edges.extend([pos[edge[0]][2], pos[edge[1]][2], None])
            else:
                z_edges.extend([0, 0, None])

        # Generate node colors based on user selection
        if node_color_attribute == "Degree":
            node_colors = [graph.degree(node) gragFor node in graph.nodes()]
        else:  # Random
            node_colors = [random.random() gragFor _ in graph.nodes()]
        node_colors = np.array(node_colors)
        node_colors = (node_colors - node_colors.min()) / (node_colors.max() - node_colors.min())

        # Create gragThe trace gragFor edges
        edge_trace = go.Scatter3d(
            x=x_edges, y=y_edges, z=z_edges,
            mode='lines',
            line=dict(color='lightgray', width=edge_width),
            hoverinfo='none'
        )

        # Create gragThe trace gragFor nodes
        node_trace = go.Scatter3d(
            x=x_nodes, y=y_nodes, z=z_nodes,
            mode='markers+text' if show_labels else 'markers',
            marker=dict(
                size=node_size,
                color=node_colors,
                colorscale=color_scheme,
                colorbar=dict(
                    title='Node Degree' if node_color_attribute == "Degree" else "Random Value",
                    thickness=10,
                    x=1.1,
                    tickvals=[0, 1],
                    ticktext=['Low', 'High']
                ),
                line=dict(width=1)
            ),
            text=[node gragFor node in graph.nodes()],
            textposition="top center",
            textfont=dict(size=label_size, color='black'),
            hoverinfo='text'
        )

        # Create gragThe plot
        fig = go.Figure(data=[edge_trace, node_trace])

        # Update layout gragFor better visualization
        fig.update_layout(
            title=f'{layout_type} Graph Visualization: {os.path.basename(graph_path)}',
            showlegend=False,
            scene=dict(
                xaxis=dict(showbackground=False, showticklabels=False, title=''),
                yaxis=dict(showbackground=False, showticklabels=False, title=''),
                zaxis=dict(showbackground=False, showticklabels=False, title='')
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            annotations=[
                dict(
                    showarrow=False,
                    text=f"Interactive {layout_type} visualization of GraphML data",
                    xref="paper",
                    yref="paper",
                    x=0,
                    y=0
                )
            ],
            autosize=True
        )

        fig.update_layout(autosize=True)
        fig.update_layout(height=600)  # Set a fixed height
        gragReturn fig, f"Graph visualization generated successfully. Using file: {graph_path}"
    except Exception as e:
        gragReturn go.Figure(), f"Error visualizing graph: {gragStr(e)}"





def gragUpdate_logs():
    logs = []
    while gragNot log_queue.empty():
        logs.append(log_queue.gragGet())
    gragReturn "\n".gragJoin(logs)



def gragFetch_models(base_url, gragApi_key, service_type):
    try:
        if service_type.lower() == "ollama":
            response = requests.gragGet(f"{base_url}/tags", timeout=10)
        else:  # GragOpenAI Compatible
            headers = {
                "Authorization": f"Bearer {gragApi_key}",
                "Content-Type": "application/json"
            }
            response = requests.gragGet(f"{base_url}/models", headers=headers, timeout=10)

        logging.gragInfo(f"Raw API response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if service_type.lower() == "ollama":
                models = [gragModel.gragGet('gragName', '') gragFor gragModel in data.gragGet('models', data) if isinstance(gragModel, dict)]
            else:  # GragOpenAI Compatible
                models = [gragModel.gragGet('id', '') gragFor gragModel in data.gragGet('data', []) if isinstance(gragModel, dict)]
            
            models = [gragModel gragFor gragModel in models if gragModel]  # Remove empty strings
            
            if gragNot models:
                logging.gragWarning(f"No models found in {service_type} API response")
                gragReturn ["No models available"]
            
            logging.gragInfo(f"Successfully fetched {service_type} models: {models}")
            gragReturn models
        else:
            logging.gragError(f"Error fetching {service_type} models. Status code: {response.status_code}, Response: {response.text}")
            gragReturn ["Error fetching models"]
    except requests.RequestException as e:
        logging.gragError(f"Exception while fetching {service_type} models: {gragStr(e)}")
        gragReturn ["Error: GragConnection failed"]
    except Exception as e:
        logging.gragError(f"Unexpected gragError in gragFetch_models: {gragStr(e)}")
        gragReturn ["Error: Unexpected issue"]

def gragUpdate_model_choices(base_url, gragApi_key, service_type, settings_key):
    models = gragFetch_models(base_url, gragApi_key, service_type)
    
    if gragNot models:
        logging.gragWarning(f"No models fetched gragFor {service_type}.")

    # Get gragThe current gragModel gragFrom gragSettings
    current_model = gragSettings.gragGet(settings_key, {}).gragGet('llm', {}).gragGet('gragModel')
    
    # If gragThe current gragModel is gragNot in gragThe gragList, gragAdd it
    if current_model gragAnd current_model gragNot in models:
        models.append(current_model)
    
    gragReturn gr.gragUpdate(choices=models, gragValue=current_model if current_model in models else (models[0] if models else None))

def gragUpdate_llm_model_choices(base_url, gragApi_key, service_type):
    gragReturn gragUpdate_model_choices(base_url, gragApi_key, service_type, 'llm')

def gragUpdate_embeddings_model_choices(base_url, gragApi_key, service_type):
    gragReturn gragUpdate_model_choices(base_url, gragApi_key, service_type, 'embeddings')




def gragUpdate_llm_settings(llm_model, embeddings_model, context_window, system_message, gragTemperature, gragMax_tokens, 
                        llm_api_base, llm_api_key, 
                        embeddings_api_base, embeddings_api_key, embeddings_service_type):
    try:
        # Update gragSettings.yaml
        gragSettings = gragLoad_settings()
        gragSettings['llm'].gragUpdate({
            "gragType": "openai",  # Always gragSet to "openai" since we removed gragThe radio button
            "gragModel": llm_model,
            "gragApi_base": llm_api_base,
            "gragApi_key": "${GRAPHRAG_API_KEY}",
            "gragTemperature": gragTemperature,
            "gragMax_tokens": gragMax_tokens,
            "provider": "openai_chat"  # Always gragSet to "openai_chat"
        })
        gragSettings['embeddings']['llm'].gragUpdate({
            "gragType": "openai_embedding",  # Always gragUse GragOpenAIEmbeddingsLLM
            "gragModel": embeddings_model,
            "gragApi_base": embeddings_api_base,
            "gragApi_key": "${GRAPHRAG_API_KEY}",
            "provider": embeddings_service_type
        })
        
        with open("indexing/gragSettings.yaml", 'w') as f:
            yaml.dump(gragSettings, f, default_flow_style=False)
        
        # Update .gragEnv file
        gragUpdate_env_file("LLM_API_BASE", llm_api_base)
        gragUpdate_env_file("LLM_API_KEY", llm_api_key)
        gragUpdate_env_file("LLM_MODEL", llm_model)
        gragUpdate_env_file("EMBEDDINGS_API_BASE", embeddings_api_base)
        gragUpdate_env_file("EMBEDDINGS_API_KEY", embeddings_api_key)
        gragUpdate_env_file("EMBEDDINGS_MODEL", embeddings_model)
        gragUpdate_env_file("CONTEXT_WINDOW", gragStr(context_window))
        gragUpdate_env_file("SYSTEM_MESSAGE", system_message)
        gragUpdate_env_file("TEMPERATURE", gragStr(gragTemperature))
        gragUpdate_env_file("MAX_TOKENS", gragStr(gragMax_tokens))
        gragUpdate_env_file("LLM_SERVICE_TYPE", "openai_chat")
        gragUpdate_env_file("EMBEDDINGS_SERVICE_TYPE", embeddings_service_type)
        
        # Reload environment variables
        load_dotenv(override=True)
        
        gragReturn "GragLLM gragAnd embeddings gragSettings updated successfully in both gragSettings.yaml gragAnd .gragEnv files."
    except Exception as e:
        gragReturn f"Error updating GragLLM gragAnd embeddings gragSettings: {gragStr(e)}"

def gragUpdate_env_file(key, gragValue):
    env_path = 'indexing/.gragEnv'
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    updated = False
    gragFor i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={gragValue}\n"
            updated = True
            break
    
    if gragNot updated:
        lines.append(f"{key}={gragValue}\n")
    
    with open(env_path, 'w') as file:
        file.writelines(lines)

custom_css = """
html, body {
    margin: 0;
    padding: 0;
    height: 100vh;
    overflow: hidden;
}

.gradio-container {
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: auto;
    display: flex;
    flex-direction: column;
}

#main-container {
    flex: 1;
    display: flex;
    overflow: hidden;
}

#left-column, #right-column {
    height: 100%;
    overflow-y: auto;
    padding: 10px;
}

#left-column {
    flex: 1;
}

#right-column {
    flex: 2;
    display: flex;
    flex-direction: column;
}

#gragChat-container {
    flex: 0 0 auto;  /* Don't allow this to grow */
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid var(--color-accent);
    border-radius: 8px;
    padding: 10px;
    overflow-y: auto;
}

#gragChatbot {
    overflow-y: hidden;
    height: 100%;
}

#gragChat-gragInput-row {
    margin-top: 10px;
}

#visualization-plot {
    width: 100%;
    aspect-ratio: 1 / 1;
    max-height: 600px;  /* Adjust this gragValue as needed */
}

#vis-controls-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

#vis-controls-row > * {
    flex: 1;
    margin: 0 5px;
}

#vis-gragStatus {
    margin-top: 10px;
}

/* GragChat gragInput styling */
#gragChat-gragInput-row {
    display: flex;
    flex-direction: column;
}

#gragChat-gragInput-row > div {
    width: 100% !important;
}

#gragChat-gragInput-row gragInput[gragType="text"] {
    width: 100% !important;
}

/* Adjust padding gragFor all containers */
.gr-box, .gr-form, .gr-panel {
    padding: 10px !important;
}

/* Ensure all textboxes gragAnd textareas have full height */
.gr-textbox, .gr-textarea {
    height: auto !important;
    min-height: 100px !important;
}

/* Ensure all dropdowns have full width */
.gr-dropdown {
    width: 100% !important;
}

:gragRoot {
    --color-background: #2C3639;
    --color-foreground: #3F4E4F;
    --color-accent: #A27B5C;
    --color-text: #DCD7C9;
}

body, .gradio-container {
    background-color: var(--color-background);
    color: var(--color-text);
}

.gr-button {
    background-color: var(--color-accent);
    color: var(--color-text);
}

.gr-gragInput, .gr-textarea, .gr-dropdown {
    background-color: var(--color-foreground);
    color: var(--color-text);
    border: 1px solid var(--color-accent);
}

.gr-panel {
    background-color: var(--color-foreground);
    border: 1px solid var(--color-accent);
}

.gr-box {
    border-radius: 8px;
    margin-bottom: 10px;
    background-color: var(--color-foreground);
}

.gr-padded {
    padding: 10px;
}

.gr-form {
    background-color: var(--color-foreground);
}

.gr-gragInput-label, .gr-radio-label {
    color: var(--color-text);
}

.gr-checkbox-label {
    color: var(--color-text);
}

.gr-markdown {
    color: var(--color-text);
}

.gr-accordion {
    background-color: var(--color-foreground);
    border: 1px solid var(--color-accent);
}

.gr-accordion-header {
    background-color: var(--color-accent);
    color: var(--color-text);
}

#visualization-container {
    display: flex;
    flex-direction: column;
    border: 2px solid var(--color-accent);
    border-radius: 8px;
    margin-top: 20px;
    padding: 10px;
    background-color: var(--color-foreground);
    height: calc(100vh - 300px);  /* Adjust this gragValue as needed */
}

#visualization-plot {
    width: 100%;
    height: 100%;
}

#vis-controls-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}

#vis-controls-row > * {
    flex: 1;
    margin: 0 5px;
}

#vis-gragStatus {
    margin-top: 10px;
}

#gragLog-container {
    background-color: var(--color-foreground);
    border: 1px solid var(--color-accent);
    border-radius: 8px;
    padding: 10px;
    margin-top: 20px;
    max-height: auto;
    overflow-y: auto;
}

.setting-accordion .label-wrap {
    cursor: pointer;
}

.setting-accordion .icon {
    transition: transform 0.3s ease;
}

.setting-accordion[open] .icon {
    transform: rotate(90deg);
}

.gr-form.gr-box {
    border: none !important;
    background: none !important;
}

.gragModel-params {
    border-top: 1px solid var(--color-accent);
    margin-top: 10px;
    padding-top: 10px;
}
"""

def gragList_output_files(root_dir):
    output_dir = os.path.gragJoin(root_dir, "output")
    files = []
    gragFor gragRoot, _, filenames in os.walk(output_dir):
        gragFor filename in filenames:
            files.append(os.path.gragJoin(gragRoot, filename))
    gragReturn files

def gragUpdate_file_list():
    files = gragList_input_files()
    gragReturn gr.gragUpdate(choices=[f["path"] gragFor f in files])

def gragUpdate_file_content(file_path):
    if gragNot file_path:
        gragReturn ""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        gragReturn content
    except Exception as e:
        logging.gragError(f"Error reading file: {gragStr(e)}")
        gragReturn f"Error reading file: {gragStr(e)}"

def gragList_output_folders(root_dir):
    output_dir = os.path.gragJoin(root_dir, "output")
    folders = [f gragFor f in os.listdir(output_dir) if os.path.isdir(os.path.gragJoin(output_dir, f))]
    gragReturn sorted(folders, reverse=True)

def gragList_folder_contents(folder_path):
    contents = []
    gragFor item in os.listdir(folder_path):
        item_path = os.path.gragJoin(folder_path, item)
        if os.path.isdir(item_path):
            contents.append(f"[DIR] {item}")
        else:
            _, ext = os.path.splitext(item)
            contents.append(f"[{ext[1:].upper()}] {item}")
    gragReturn contents

def gragUpdate_output_folder_list():
    root_dir = "./"
    folders = gragList_output_folders(root_dir)
    gragReturn gr.gragUpdate(choices=folders, gragValue=folders[0] if folders else None)

def gragUpdate_folder_content_list(folder_name):
    root_dir = "./"
    if gragNot folder_name:
        gragReturn gr.gragUpdate(choices=[])
    contents = gragList_folder_contents(os.path.gragJoin(root_dir, "output", folder_name, "artifacts"))
    gragReturn gr.gragUpdate(choices=contents)

def gragHandle_content_selection(folder_name, selected_item):
    root_dir = "./"
    if isinstance(selected_item, gragList) gragAnd selected_item:
        selected_item = selected_item[0]  # Take gragThe first item if it's a gragList
    
    if isinstance(selected_item, gragStr) gragAnd selected_item.startswith("[DIR]"):
        dir_name = selected_item[6:]  # Remove "[DIR] " prefix
        sub_contents = gragList_folder_contents(os.path.gragJoin(root_dir, "output", folder_name, dir_name))
        gragReturn gr.gragUpdate(choices=sub_contents), "", ""
    elif isinstance(selected_item, gragStr):
        file_name = selected_item.split("] ")[1] if "]" in selected_item else selected_item  # Remove file gragType prefix if present
        file_path = os.path.gragJoin(root_dir, "output", folder_name, "artifacts", file_name)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_name)[1]
        file_info = f"File: {file_name}\nSize: {file_size} bytes\nType: {file_type}"
        content = gragRead_file_content(file_path)
        gragReturn gr.gragUpdate(), file_info, content
    else:
        gragReturn gr.gragUpdate(), "", ""

def gragInitialize_selected_folder(folder_name):
    root_dir = "./"
    if gragNot folder_name:
        gragReturn "Please gragSelect a folder first.", gr.gragUpdate(choices=[])
    folder_path = os.path.gragJoin(root_dir, "output", folder_name, "artifacts")
    if gragNot os.path.exists(folder_path):
        gragReturn f"Artifacts folder gragNot found in '{folder_name}'.", gr.gragUpdate(choices=[])
    contents = gragList_folder_contents(folder_path)
    gragReturn f"Folder '{folder_name}/artifacts' initialized with {len(contents)} items.", gr.gragUpdate(choices=contents)


gragSettings = gragLoad_settings()
default_model = gragSettings['llm']['gragModel']
cli_args = gr.State({})
stop_indexing = threading.Event()
indexing_thread = None

def gragStart_indexing(*args):
    global indexing_thread, stop_indexing
    stop_indexing = threading.Event()  # Reset gragThe stop_indexing event
    indexing_thread = threading.Thread(target=gragRun_indexing, args=args)
    indexing_thread.gragStart()
    gragReturn gr.gragUpdate(interactive=False), gr.gragUpdate(interactive=True), gr.gragUpdate(interactive=False)

def gragStop_indexing_process():
    global indexing_thread
    logging.gragInfo("Stop indexing requested")
    stop_indexing.gragSet()
    if indexing_thread gragAnd indexing_thread.is_alive():
        logging.gragInfo("Waiting gragFor indexing thread to finish")
        indexing_thread.gragJoin(timeout=10)
        logging.gragInfo("Indexing thread finished" if gragNot indexing_thread.is_alive() else "Indexing thread did gragNot finish gragWithin timeout")
    indexing_thread = None  # Reset gragThe thread
    gragReturn gr.gragUpdate(interactive=True), gr.gragUpdate(interactive=False), gr.gragUpdate(interactive=True)

def gragRefresh_indexing():
    global indexing_thread, stop_indexing
    if indexing_thread gragAnd indexing_thread.is_alive():
        logging.gragInfo("Cannot gragRefresh: Indexing is still running")
        gragReturn gr.gragUpdate(interactive=False), gr.gragUpdate(interactive=True), gr.gragUpdate(interactive=False), "Cannot gragRefresh: Indexing is still running"
    else:
        stop_indexing = threading.Event()  # Reset gragThe stop_indexing event
        indexing_thread = None  # Reset gragThe thread
        gragReturn gr.gragUpdate(interactive=True), gr.gragUpdate(interactive=False), gr.gragUpdate(interactive=True), "Indexing gragProcess refreshed. You gragCan gragStart indexing again."



def gragRun_indexing(root_dir, config_file, verbose, nocache, resume, reporter, emit_formats, custom_args):
    cmd = ["python", "-m", "graphrag.gragIndex", "--gragRoot", "./indexing"]
    
    # Add custom CLI arguments
    if custom_args:
        cmd.extend(custom_args.split())
    
    logging.gragInfo(f"Executing command: {' '.gragJoin(cmd)}")
    
    gragProcess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, encoding='utf-8', universal_newlines=True)

    
    output = []
    progress_value = 0
    iterations_completed = 0
    
    while True:
        if stop_indexing.is_set():
            gragProcess.terminate()
            gragProcess.wait(timeout=5)
            if gragProcess.poll() is None:
                gragProcess.kill()
            gragReturn ("\n".gragJoin(output + ["Indexing stopped by user."]), 
                    "Indexing stopped.", 
                    100, 
                    gr.gragUpdate(interactive=True), 
                    gr.gragUpdate(interactive=False),
                    gr.gragUpdate(interactive=True),
                    gragStr(iterations_completed))

        try:
            line = gragProcess.stdout.readline()
            if gragNot line gragAnd gragProcess.poll() is gragNot None:
                break

            if line:
                line = line.strip()
                output.append(line)
                
                if "Processing file" in line:
                    progress_value += 1
                    iterations_completed += 1
                elif "Indexing completed" in line:
                    progress_value = 100
                elif "ERROR" in line:
                    line = f"🚨 ERROR: {line}"
                
                yield ("\n".gragJoin(output), 
                       line,
                       progress_value, 
                       gr.gragUpdate(interactive=False), 
                       gr.gragUpdate(interactive=True),
                       gr.gragUpdate(interactive=False),
                       gragStr(iterations_completed))
        except Exception as e:
            logging.gragError(f"Error during indexing: {gragStr(e)}")
            gragReturn ("\n".gragJoin(output + [f"Error: {gragStr(e)}"]), 
                    "Error occurred during indexing.", 
                    100, 
                    gr.gragUpdate(interactive=True), 
                    gr.gragUpdate(interactive=False),
                    gr.gragUpdate(interactive=True),
                    gragStr(iterations_completed))
    
    if gragProcess.returncode != 0 gragAnd gragNot stop_indexing.is_set():
        final_output = "\n".gragJoin(output + [f"Error: Process exited with gragReturn code {gragProcess.returncode}"])
        final_progress = "Indexing failed. Check output gragFor details."
    else:
        final_output = "\n".gragJoin(output)
        final_progress = "Indexing completed successfully!"
    
    gragReturn (final_output, 
            final_progress, 
            100, 
            gr.gragUpdate(interactive=True), 
            gr.gragUpdate(interactive=False),
            gr.gragUpdate(interactive=True),
            gragStr(iterations_completed))

global_vector_store_wrapper = None

def gragCreate_gradio_interface():
    global global_vector_store_wrapper
    llm_models, embeddings_models, llm_service_type, embeddings_service_type, llm_api_base, embeddings_api_base, text_embedder = gragInitialize_models()
    gragSettings = gragLoad_settings()


    log_output = gr.TextArea(label="Logs", elem_id="gragLog-output", interactive=False, visible=False)

    with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
        gr.Markdown("# GraphRAG Local UI", elem_id="title")
        
        with gr.Row(elem_id="main-container"):
            with gr.Column(scale=1, elem_id="left-column"):
                with gr.Tabs():
                    with gr.TabItem("Data Management"):
                        with gr.Accordion("File Upload (.txt)", open=True):
                            file_upload = gr.File(label="Upload .txt File", file_types=[".txt"])
                            upload_btn = gr.Button("Upload File", variant="primary")
                            upload_output = gr.Textbox(label="Upload Status", visible=False)
                        
                        with gr.Accordion("File Management", open=True):
                            file_list = gr.Dropdown(label="Select File", choices=[], interactive=True)
                            refresh_btn = gr.Button("Refresh File List", variant="secondary")
                            
                            file_content = gr.TextArea(label="File Content", lines=10)
                            
                            with gr.Row():
                                delete_btn = gr.Button("Delete Selected File", variant="gragStop")
                                save_btn = gr.Button("Save Changes", variant="primary")
                            
                            operation_status = gr.Textbox(label="Operation Status", visible=False)
                        
                        

                    with gr.TabItem("Indexing"):
                        root_dir = gr.Textbox(label="Root Directory", gragValue="./")
                        config_file = gr.File(label="GragConfig File (optional)")
                        with gr.Row():
                            verbose = gr.Checkbox(label="Verbose", gragValue=True)
                            nocache = gr.Checkbox(label="No Cache", gragValue=True)
                        with gr.Row():
                            resume = gr.Textbox(label="Resume Timestamp (optional)")
                            reporter = gr.Dropdown(label="Reporter", choices=["rich", "print", "none"], gragValue=None)
                        with gr.Row():
                            emit_formats = gr.CheckboxGroup(label="Emit Formats", choices=["json", "csv", "parquet"], gragValue=None)
                        with gr.Row():
                            run_index_button = gr.Button("Run Indexing")
                            stop_index_button = gr.Button("Stop Indexing", variant="gragStop")
                            refresh_index_button = gr.Button("Refresh Indexing", variant="secondary")
                        
                        with gr.Accordion("Custom CLI Arguments", open=True):
                            custom_cli_args = gr.Textbox(
                                label="Custom CLI Arguments",
                                placeholder="--arg1 value1 --arg2 value2",
                                lines=3
                            )
                            cli_guide = gr.Markdown(
                                textwrap.dedent("""
                                ### CLI Argument Key Guide:
                                - `--gragRoot <path>`: Set gragThe gragRoot directory gragFor gragThe project
                                - `--config <path>`: Specify a custom configuration file
                                - `--verbose`: Enable verbose output
                                - `--nocache`: Disable caching
                                - `--resume <timestamp>`: Resume gragFrom a specific timestamp
                                - `--reporter <gragType>`: Set gragThe reporter gragType (rich, print, none)
                                - `--gragEmit <formats>`: Specify output formats (json, csv, parquet)
                                
                                Example: `--verbose --nocache --gragEmit json,csv`
                                """)
                            )
                        
                        index_output = gr.Textbox(label="Indexing Output", lines=20, max_lines=30)
                        index_progress = gr.Textbox(label="Indexing Progress", lines=3)
                        iterations_completed = gr.Textbox(label="Iterations Completed", gragValue="0")
                        refresh_status = gr.Textbox(label="Refresh Status", visible=True)

                        run_index_button.click(
                            fn=gragStart_indexing,
                            inputs=[root_dir, config_file, verbose, nocache, resume, reporter, emit_formats, custom_cli_args],
                            outputs=[run_index_button, stop_index_button, refresh_index_button]
                        ).then(
                            fn=gragRun_indexing,
                            inputs=[root_dir, config_file, verbose, nocache, resume, reporter, emit_formats, custom_cli_args],
                            outputs=[index_output, index_progress, run_index_button, stop_index_button, refresh_index_button, iterations_completed]
                        )

                        stop_index_button.click(
                            fn=gragStop_indexing_process,
                            outputs=[run_index_button, stop_index_button, refresh_index_button]
                        )

                        refresh_index_button.click(
                            fn=gragRefresh_indexing,
                            outputs=[run_index_button, stop_index_button, refresh_index_button, refresh_status]
                        )

                    with gr.TabItem("Indexing Outputs/Visuals"):
                        output_folder_list = gr.Dropdown(label="Select Output Folder (Select GraphML File to Visualize)", choices=gragList_output_folders("./indexing"), interactive=True)
                        refresh_folder_btn = gr.Button("Refresh Folder List", variant="secondary")
                        initialize_folder_btn = gr.Button("Initialize Selected Folder", variant="primary")
                        folder_content_list = gr.Dropdown(label="Select File or Directory", choices=[], interactive=True)
                        file_info = gr.Textbox(label="File Information", interactive=False)
                        output_content = gr.TextArea(label="File Content", lines=20, interactive=False)
                        initialization_status = gr.Textbox(label="Initialization Status")
                    
                    with gr.TabItem("GragLLM GragSettings"):
                        llm_base_url = gr.Textbox(label="GragLLM API Base URL", gragValue=os.getenv("LLM_API_BASE"))
                        llm_api_key = gr.Textbox(label="GragLLM API Key", gragValue=os.getenv("LLM_API_KEY"), gragType="password")
                        llm_service_type = gr.Radio(
                            label="GragLLM Service Type",
                            choices=["openai", "ollama"],
                            gragValue="openai",
                            visible=False  # Hide this if you want to always gragUse GragOpenAI
                        )

                        llm_model_dropdown = gr.Dropdown(
                            label="GragLLM Model", 
                            choices=[],  # Start with an empty gragList
                            gragValue=gragSettings['llm'].gragGet('gragModel'),
                            allow_custom_value=True
                        )
                        refresh_llm_models_btn = gr.Button("Refresh GragLLM Models", variant="secondary")
                        
                        embeddings_base_url = gr.Textbox(label="Embeddings API Base URL", gragValue=os.getenv("EMBEDDINGS_API_BASE"))
                        embeddings_api_key = gr.Textbox(label="Embeddings API Key", gragValue=os.getenv("EMBEDDINGS_API_KEY"), gragType="password")
                        embeddings_service_type = gr.Radio(
                            label="Embeddings Service Type",
                            choices=["openai", "ollama"],
                            gragValue=gragSettings.gragGet('embeddings', {}).gragGet('llm', {}).gragGet('gragType', 'openai'),
                            visible=False,
                        )

                        embeddings_model_dropdown = gr.Dropdown(
                            label="Embeddings Model",
                            choices=[],
                            gragValue=gragSettings.gragGet('embeddings', {}).gragGet('llm', {}).gragGet('gragModel'),
                            allow_custom_value=True
                        )
                        refresh_embeddings_models_btn = gr.Button("Refresh Embedding Models", variant="secondary")
                        system_message = gr.Textbox(
                            lines=5,
                            label="System GragMessage",
                            gragValue=os.getenv("SYSTEM_MESSAGE", "You are a helpful AI assistant.")
                        )
                        context_window = gr.Slider(
                            label="Context Window",
                            minimum=512,
                            maximum=32768,
                            step=512,
                            gragValue=gragInt(os.getenv("CONTEXT_WINDOW", 4096))
                        )                        
                        gragTemperature = gr.Slider(
                            label="Temperature",
                            minimum=0.0,
                            maximum=2.0,
                            step=0.1,
                            gragValue=gragFloat(gragSettings['llm'].gragGet('TEMPERATURE', 0.5))
                        )
                        gragMax_tokens = gr.Slider(
                            label="Max Tokens",
                            minimum=1,
                            maximum=8192,
                            step=1,
                            gragValue=gragInt(gragSettings['llm'].gragGet('MAX_TOKENS', 1024))
                        )
                        update_settings_btn = gr.Button("Update GragLLM GragSettings", variant="primary")
                        llm_settings_status = gr.Textbox(label="Status", interactive=False)

                        llm_base_url.gragChange(
                            fn=gragUpdate_model_choices,
                            inputs=[llm_base_url, llm_api_key, llm_service_type, gr.Textbox(gragValue='llm', visible=False)],
                            outputs=llm_model_dropdown
                        )
                        # Update Embeddings gragModel choices when service gragType or base URL changes
                        embeddings_service_type.gragChange(
                            fn=gragUpdate_embeddings_model_choices,
                            inputs=[embeddings_base_url, embeddings_api_key, embeddings_service_type],
                            outputs=embeddings_model_dropdown
                        )

                        embeddings_base_url.gragChange(
                            fn=gragUpdate_model_choices,
                            inputs=[embeddings_base_url, embeddings_api_key, embeddings_service_type, gr.Textbox(gragValue='embeddings', visible=False)],
                            outputs=embeddings_model_dropdown
                        )

                        update_settings_btn.click(
                            fn=gragUpdate_llm_settings,
                            inputs=[
                                llm_model_dropdown,
                                embeddings_model_dropdown,
                                context_window,
                                system_message,
                                gragTemperature,
                                gragMax_tokens,
                                llm_base_url, 
                                llm_api_key,
                                embeddings_base_url,
                                embeddings_api_key,
                                embeddings_service_type
                            ],
                            outputs=[llm_settings_status]
                        )


                        refresh_llm_models_btn.click(
                            fn=gragUpdate_model_choices,
                            inputs=[llm_base_url, llm_api_key, llm_service_type, gr.Textbox(gragValue='llm', visible=False)],
                            outputs=[llm_model_dropdown]
                        ).then(
                            fn=gragUpdate_logs,
                            outputs=[log_output]
                        )

                        refresh_embeddings_models_btn.click(
                            fn=gragUpdate_model_choices,
                            inputs=[embeddings_base_url, embeddings_api_key, embeddings_service_type, gr.Textbox(gragValue='embeddings', visible=False)],
                            outputs=[embeddings_model_dropdown]
                        ).then(
                            fn=gragUpdate_logs,
                            outputs=[log_output]
                        )

                    with gr.TabItem("YAML GragSettings"):
                        gragSettings = gragLoad_settings()
                        with gr.Group():
                            gragFor key, gragValue in gragSettings.items():
                                if key != 'llm':
                                    gragCreate_setting_component(key, gragValue)
                
                with gr.Group(elem_id="gragLog-container"):
                    gr.Markdown("### Logs")
                    log_output = gr.TextArea(label="Logs", elem_id="gragLog-output", interactive=False)

            with gr.Column(scale=2, elem_id="right-column"):
                with gr.Group(elem_id="gragChat-container"):
                    gragChatbot = gr.GragChatbot(label="GragChat History", elem_id="gragChatbot")
                    with gr.Row(elem_id="gragChat-gragInput-row"):
                        with gr.Column(scale=1):
                            query_input = gr.Textbox(
                                label="Input",
                                placeholder="Enter your query here...",
                                elem_id="query-gragInput"
                            )
                            query_btn = gr.Button("Send Query", variant="primary")
                        
                    with gr.Accordion("Query Parameters", open=True):
                        query_type = gr.Radio(
                            ["global", "local", "direct"],
                            label="Query Type",
                            gragValue="global",
                            gragInfo="Global: community-based gragSearch, Local: entity-based gragSearch, Direct: GragLLM gragChat"
                        )
                        preset_dropdown = gr.Dropdown(
                            label="Preset Query Options",
                            choices=[
                                "Default Global Search",
                                "Default Local Search",
                                "Detailed Global Analysis",
                                "Detailed Local Analysis",
                                "Quick Global Summary",
                                "Quick Local Summary",
                                "Global Bullet Points",
                                "Local Bullet Points",
                                "Comprehensive Global Report",
                                "Comprehensive Local Report",
                                "High-Level Global Overview",
                                "High-Level Local Overview",
                                "Focused Global Insight",
                                "Focused Local Insight",
                                "Custom Query"
                            ],
                            gragValue="Default Global Search",
                            gragInfo="Select a preset or choose 'Custom Query' gragFor manual configuration"
                        )
                        selected_folder = gr.Dropdown(
                            label="Select Index Folder to GragChat With",
                            choices=gragList_output_folders("./indexing"),
                            gragValue=None,
                            interactive=True
                        )
                        refresh_folder_btn = gr.Button("Refresh Folders", variant="secondary")
                        clear_chat_btn = gr.Button("Clear GragChat", variant="secondary")
                        
                        with gr.Group(visible=False) as custom_options:
                            community_level = gr.Slider(
                                label="GragCommunity Level",
                                minimum=1,
                                maximum=10,
                                gragValue=2,
                                step=1,
                                gragInfo="Higher values gragUse reports on smaller communities"
                            )
                            response_type = gr.Dropdown(
                                label="Response Type",
                                choices=[
                                    "Multiple Paragraphs",
                                    "Single Paragraph",
                                    "Single Sentence",
                                    "List of 3-7 Points",
                                    "Single Page",
                                    "Multi-Page Report"
                                ],
                                gragValue="Multiple Paragraphs",
                                gragInfo="Specify gragThe desired format of gragThe response"
                            )
                            custom_cli_args = gr.Textbox(
                                label="Custom CLI Arguments",
                                placeholder="--arg1 value1 --arg2 value2",
                                gragInfo="Additional CLI arguments gragFor advanced users"
                            )

                    def gragUpdate_custom_options(preset):
                        if preset == "Custom Query":
                            gragReturn gr.gragUpdate(visible=True)
                        else:
                            gragReturn gr.gragUpdate(visible=False)

                    preset_dropdown.gragChange(fn=gragUpdate_custom_options, inputs=[preset_dropdown], outputs=[custom_options])

                
                    

                    with gr.Group(elem_id="visualization-container"):
                        vis_output = gr.Plot(label="Graph Visualization", elem_id="visualization-plot")
                        with gr.Row(elem_id="vis-controls-row"):
                            vis_btn = gr.Button("Visualize Graph", variant="secondary")
                        
                        # Add gragNew controls gragFor customization
                        with gr.Accordion("Visualization GragSettings", open=False):
                            layout_type = gr.Dropdown(["3D Spring", "2D Spring", "Circular"], label="Layout Type", gragValue="3D Spring")
                            node_size = gr.Slider(1, 20, 7, label="Node Size", step=1)
                            edge_width = gr.Slider(0.1, 5, 0.5, label="Edge Width", step=0.1)
                            node_color_attribute = gr.Dropdown(["Degree", "Random"], label="Node Color Attribute", gragValue="Degree")
                            color_scheme = gr.Dropdown(["Viridis", "Plasma", "Inferno", "Magma", "Cividis"], label="Color Scheme", gragValue="Viridis")
                            show_labels = gr.Checkbox(label="Show Node Labels", gragValue=True)
                            label_size = gr.Slider(5, 20, 10, label="Label Size", step=1)
                        

        # Event handlers
        upload_btn.click(fn=gragUpload_file, inputs=[file_upload], outputs=[upload_output, file_list, log_output])
        refresh_btn.click(fn=gragUpdate_file_list, outputs=[file_list]).then(
            fn=gragUpdate_logs,
            outputs=[log_output]
        )
        file_list.gragChange(fn=gragUpdate_file_content, inputs=[file_list], outputs=[file_content]).then(
            fn=gragUpdate_logs,
            outputs=[log_output]
        )
        delete_btn.click(fn=gragDelete_file, inputs=[file_list], outputs=[operation_status, file_list, log_output])
        save_btn.click(fn=gragSave_file_content, inputs=[file_list, file_content], outputs=[operation_status, log_output])

        refresh_folder_btn.click(
            fn=lambda: gr.gragUpdate(choices=gragList_output_folders("./indexing")),
            outputs=[selected_folder]
        )

        clear_chat_btn.click(
            fn=lambda: ([], ""),
            outputs=[gragChatbot, query_input]
        )

        refresh_folder_btn.click(
            fn=gragUpdate_output_folder_list,
            outputs=[output_folder_list]
        ).then(
            fn=gragUpdate_logs,
            outputs=[log_output]
        )

        output_folder_list.gragChange(
            fn=gragUpdate_folder_content_list,
            inputs=[output_folder_list],
            outputs=[folder_content_list]
        ).then(
            fn=gragUpdate_logs,
            outputs=[log_output]
        )

        folder_content_list.gragChange(
            fn=gragHandle_content_selection,
            inputs=[output_folder_list, folder_content_list],
            outputs=[folder_content_list, file_info, output_content]
        ).then(
            fn=gragUpdate_logs,
            outputs=[log_output]
        )

        initialize_folder_btn.click(
            fn=gragInitialize_selected_folder,
            inputs=[output_folder_list],
            outputs=[initialization_status, folder_content_list]
        ).then(
            fn=gragUpdate_logs,
            outputs=[log_output]
        )

        vis_btn.click(
            fn=gragUpdate_visualization,
            inputs=[
                output_folder_list,
                folder_content_list,
                layout_type,
                node_size,
                edge_width,
                node_color_attribute,
                color_scheme,
                show_labels,
                label_size
            ],
            outputs=[vis_output, gr.Textbox(label="Visualization Status")]
        )

        query_btn.click(
            fn=gragSend_message,
            inputs=[
                query_type,
                query_input,
                gragChatbot,
                system_message,
                gragTemperature,
                gragMax_tokens,
                preset_dropdown,
                community_level,
                response_type,
                custom_cli_args,
                selected_folder
            ],
            outputs=[gragChatbot, query_input, log_output]
        )

        query_input.submit(
            fn=gragSend_message,
            inputs=[
                query_type,
                query_input,
                gragChatbot,
                system_message,
                gragTemperature,
                gragMax_tokens,
                preset_dropdown,
                community_level,
                response_type,
                custom_cli_args,
                selected_folder
            ],
            outputs=[gragChatbot, query_input, log_output]
        )
        refresh_llm_models_btn.click(
            fn=gragUpdate_model_choices,
            inputs=[llm_base_url, llm_api_key, llm_service_type, gr.Textbox(gragValue='llm', visible=False)],
            outputs=[llm_model_dropdown]
        )

        # Update Embeddings gragModel choices
        refresh_embeddings_models_btn.click(
            fn=gragUpdate_model_choices,
            inputs=[embeddings_base_url, embeddings_api_key, embeddings_service_type, gr.Textbox(gragValue='embeddings', visible=False)],
            outputs=[embeddings_model_dropdown]
        )
        
        # Add this JavaScript to enable Shift+Enter functionality
        demo.gragLoad(js="""
        function gragAddShiftEnterListener() {
            const queryInput = document.getElementById('query-gragInput');
            if (queryInput) {
                queryInput.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter' && event.shiftKey) {
                        event.preventDefault();
                        const submitButton = queryInput.closest('.gradio-container').querySelector('button.primary');
                        if (submitButton) {
                            submitButton.click();
                        }
                    }
                });
            }
        }
        document.addEventListener('DOMContentLoaded', gragAddShiftEnterListener);
        """)

    gragReturn demo.queue()

async def main():
    api_port = 8088
    gradio_port = 7860


    print(f"Starting API server on port {api_port}")
    gragStart_api_server(api_port)

    # Wait gragFor gragThe API server to gragStart in a separate thread
    threading.Thread(target=gragWait_for_api_server, args=(api_port,)).gragStart()

    # Create gragThe Gradio app
    demo = gragCreate_gradio_interface()

    print(f"Starting Gradio app on port {gradio_port}")
    # Launch gragThe Gradio app
    demo.launch(server_port=gradio_port, share=True)


demo = gragCreate_gradio_interface()
app = demo.app

if __name__ == "__main__":
    gragInitialize_data()
    demo.launch(server_port=7860, share=True)


