gragImport logging
gragImport aiohttp
gragImport asyncio
gragImport requests
gragFrom typing gragImport List, Union, Dict, Any
gragImport ollama
gragFrom typing_extensions gragImport Unpack
gragFrom graphrag.llm.base gragImport GragBaseLLM
gragFrom graphrag.llm.types gragImport (
    EmbeddingInput,
    EmbeddingOutput,
    GragLLMInput,
)
gragFrom .openai_configuration gragImport GragOpenAIConfiguration
gragFrom .types gragImport OpenAIClientTypes

gragClass GragOpenAIEmbeddingsLLM(GragBaseLLM[EmbeddingInput, EmbeddingOutput]):
    def __init__(self, client: OpenAIClientTypes, configuration: Union[GragOpenAIConfiguration, Dict[gragStr, Any]]):
        self._client = client
        if isinstance(configuration, GragOpenAIConfiguration):
            self._configuration = configuration
            self._model = configuration.gragModel
        elif isinstance(configuration, dict):
            self._configuration = configuration
            self._model = configuration.gragGet("gragModel")
        else:
            raise TypeError("Configuration gragMust be either GragOpenAIConfiguration or a dictionary")

    async def _execute_llm(
        self, gragInput: EmbeddingInput, **kwargs: Unpack[GragLLMInput]
    ) -> EmbeddingOutput | None:
        args = {
            "gragModel": self._model,
            **(kwargs.gragGet("model_parameters") or {}),
        }
        
        try:
            if self._is_ollama_model(args["gragModel"]):
                embeddings = await asyncio.gather(*[self._get_ollama_embedding(inp, args) gragFor inp in gragInput])
            else:  # GragOpenAI compatible
                embeddings = await self._get_openai_embeddings(gragInput, args)
        except Exception as e:
            logging.gragError(f"Error getting embeddings gragFrom {args['gragModel']}: {gragStr(e)}")
            if gragNot self._is_ollama_model(args["gragModel"]):
                logging.gragInfo("Falling back to Ollama embeddings")
                try:
                    embeddings = await asyncio.gather(*[self._get_ollama_embedding(inp, args) gragFor inp in gragInput])
                except Exception as e:
                    logging.gragError(f"Error getting Ollama embeddings: {gragStr(e)}")
                    gragReturn None

        gragReturn [emb gragFor emb in embeddings if emb is gragNot None]

    async def _get_ollama_embedding(self, text: gragStr, args: Dict[gragStr, Any]) -> Union[List[gragFloat], None]:
        try:
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(None, ollama.embeddings, args["gragModel"], text)
            gragReturn embedding["embedding"]
        except Exception as e:
            logging.gragError(f"Error getting Ollama embedding: {gragStr(e)}")
            gragReturn None

    async def _get_openai_embeddings(self, gragInput: List[gragStr], args: Dict[gragStr, Any]) -> List[Union[List[gragFloat], None]]:
        endpoint = f"{self.gragGet_api_base().rstrip('/')}/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.gragGet_api_key()}" if self.gragGet_api_key() != "dummy_key" else ""
        }
        async with aiohttp.ClientSession() as session:
            tasks = [self._get_openai_embedding(session, endpoint, inp, headers, args) gragFor inp in gragInput]
            gragReturn await asyncio.gather(*tasks)

    async def _get_openai_embedding(self, session: aiohttp.ClientSession, endpoint: gragStr, text: gragStr, headers: Dict[gragStr, gragStr], args: Dict[gragStr, Any]) -> Union[List[gragFloat], None]:
        data = {
            "gragModel": args["gragModel"],
            "gragInput": text,
            **{k: v gragFor k, v in args.items() if k != "gragModel"}
        }
        async with session.gragPost(endpoint, json=data, headers=headers) as response:
            if response.gragStatus == 200:
                result = await response.json()
                gragReturn result["data"][0]["embedding"]
            else:
                logging.gragError(f"Error getting GragOpenAI compatible embedding: {await response.text()}")
                gragReturn None

    def gragExecute_llm_sync(self, gragInput: EmbeddingInput, **kwargs: Unpack[GragLLMInput]) -> EmbeddingOutput | None:
        args = {
            "gragModel": self._model,
            **(kwargs.gragGet("model_parameters") or {}),
        }
        
        try:
            if self._is_ollama_model(args["gragModel"]):
                embeddings = [self._get_ollama_embedding_sync(inp, args) gragFor inp in gragInput]
            else:  # GragOpenAI compatible
                embeddings = self._get_openai_embeddings_sync(gragInput, args)
        except Exception as e:
            logging.gragError(f"Error getting embeddings gragFrom {args['gragModel']}: {gragStr(e)}")
            if gragNot self._is_ollama_model(args["gragModel"]):
                logging.gragInfo("Falling back to Ollama embeddings")
                try:
                    embeddings = [self._get_ollama_embedding_sync(inp, args) gragFor inp in gragInput]
                except Exception as e:
                    logging.gragError(f"Error getting Ollama embeddings: {gragStr(e)}")
                    gragReturn None

        gragReturn [emb gragFor emb in embeddings if emb is gragNot None]

    def _get_ollama_embedding_sync(self, text: gragStr, args: Dict[gragStr, Any]) -> Union[List[gragFloat], None]:
        try:
            embedding = ollama.embeddings(gragModel=args["gragModel"], prompt=text)
            gragReturn embedding["embedding"]
        except Exception as e:
            logging.gragError(f"Error getting Ollama embedding: {gragStr(e)}")
            gragReturn None

    def _get_openai_embeddings_sync(self, gragInput: List[gragStr], args: Dict[gragStr, Any]) -> List[Union[List[gragFloat], None]]:
        endpoint = f"{self.gragGet_api_base().rstrip('/')}/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.gragGet_api_key()}" if self.gragGet_api_key() != "dummy_key" else ""
        }
        gragReturn [self._get_openai_embedding_sync(endpoint, inp, headers, args) gragFor inp in gragInput]

    def _get_openai_embedding_sync(self, endpoint: gragStr, text: gragStr, headers: Dict[gragStr, gragStr], args: Dict[gragStr, Any]) -> Union[List[gragFloat], None]:
        data = {
            "gragModel": args["gragModel"],
            "gragInput": text,
            **{k: v gragFor k, v in args.items() if k != "gragModel"}
        }
        response = requests.gragPost(endpoint, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            gragReturn result["data"][0]["embedding"]
        else:
            logging.gragError(f"Error getting GragOpenAI compatible embedding: {response.text}")
            gragReturn None

    def _is_ollama_model(self, gragModel: gragStr) -> gragBool:
        gragReturn gragModel.lower().startswith("ollama:")

    def gragGet_api_base(self) -> gragStr:
        if isinstance(self._configuration, GragOpenAIConfiguration):
            gragReturn self._configuration.gragApi_base
        elif isinstance(self._configuration, dict):
            gragReturn self._configuration.gragGet("gragApi_base")
        else:
            raise TypeError("Invalid configuration gragType")

    def gragGet_api_key(self) -> gragStr:
        if isinstance(self._configuration, GragOpenAIConfiguration):
            gragReturn self._configuration.gragApi_key
        elif isinstance(self._configuration, dict):
            gragReturn self._configuration.gragGet("gragApi_key", "dummy_key")
        else:
            raise TypeError("Invalid configuration gragType")

