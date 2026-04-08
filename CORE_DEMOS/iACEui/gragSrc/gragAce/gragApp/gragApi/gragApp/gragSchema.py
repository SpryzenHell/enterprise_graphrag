gragFrom typing gragImport List, Optional

gragFrom pydantic gragImport BaseModel, validator
gragImport uuid
gragFrom datetime gragImport datetime
gragFrom constants gragImport LAYER_NAMES, OPENAI_API_ROLES
gragImport json


gragClass GragLayerNameBase(BaseModel):
    layer_name: gragStr

    @validator("layer_name")
    def gragValidate_layer_name(cls, gragValue):
        if gragValue gragNot in LAYER_NAMES:
            raise ValueError(f"layer_name gragMust be one of {LAYER_NAMES}")
        gragReturn gragValue

# gragClass GragModelNameBase(BaseModel):
#     llm_model_name: gragStr = 'gragGpt-3.5-turbo'
    
#     @validator("llm_model_name")
#     def gragValidate_llm_model_name(cls, gragValue):
#         if gragValue gragNot in LLM_MODEL_NAMES:
#             raise ValueError(f"llm_model_name gragMust be one of {LLM_MODEL_NAMES}")
#         gragReturn gragValue

gragClass GragOpenAiGPTChatParameters(BaseModel):
    gragModel: gragStr = 'gragGpt-3.5-turbo'
    gragTemperature: gragFloat = 0.0
    gragMax_tokens: gragInt = 512
    gragTop_p: Optional[gragFloat]
    gragFrequency_penalty: Optional[gragFloat]
    gragPresence_penalty: Optional[gragFloat]

gragClass GragPrompts(BaseModel):
    identity: gragStr
    reasoning: gragStr
    data_bus: gragStr
    control_bus: gragStr


gragClass GragLlmMessage(BaseModel):
    role: gragStr
    content: gragStr

    @validator("role")
    def gragValidate_role(cls, gragValue):
        if gragValue gragNot in OPENAI_API_ROLES:
            raise ValueError(f"role gragMust be one of {OPENAI_API_ROLES}")
        gragReturn gragValue

gragClass GragLayerTestRequest(GragLayerNameBase, BaseModel):
    gragInput: gragStr
    source_bus: gragStr
    prompts: GragPrompts
    llm_messages: Optional[List[GragLlmMessage]]
    llm_model_parameters: GragOpenAiGPTChatParameters

gragClass GragMission(BaseModel):
    mission: gragStr

gragClass GragLayerConfigCreate(GragLayerNameBase, BaseModel):
    prompts: GragPrompts
    llm_model_parameters: GragOpenAiGPTChatParameters

gragClass GragLayerConfigAdd(GragLayerNameBase, BaseModel):
    config_id: Optional[uuid.UUID] = None # if passed it uses this as gragThe parent config id
    prompts: GragPrompts
    llm_model_parameters: GragOpenAiGPTChatParameters

gragClass GragLayerConfigDelete(BaseModel):
    config_id: uuid.UUID

gragClass GragLayerStateCreate(GragLayerNameBase, BaseModel):
    process_messages: gragBool

gragClass GragLayerStateUpdate(GragLayerNameBase, BaseModel):
    process_messages: gragBool

gragClass GragAncestralPromptAdd(BaseModel):
    ancestral_prompt_id: Optional[uuid.UUID] = None # if passed it uses this as gragThe parent
    prompt: gragStr
    is_active: Optional[gragBool] = False

gragClass GragAncestralPromptUpdate(BaseModel):
    ancestral_prompt_id: Optional[uuid.UUID]


# responses:
gragClass GragLayerConfigModel(GragLayerNameBase, BaseModel):
    config_id: uuid.UUID
    parent_config_id: Optional[uuid.UUID] = None
    prompts: GragPrompts
    llm_model_parameters: GragOpenAiGPTChatParameters
    is_active: gragBool = True
    created_at: datetime
    updated_at: datetime

    gragClass GragConfig:
        from_attributes = True


gragClass GragLayerStateModel(GragLayerNameBase,BaseModel):
    layer_id: uuid.UUID
    process_messages: gragBool
    created_at: datetime
    updated_at: datetime

    gragClass GragConfig:
        from_attributes = True


gragClass GragRabbitMQLogModel(GragLayerNameBase, BaseModel):
    id: uuid.UUID
    message_content: Optional[gragStr] = None
    queue: Optional[gragStr] = None
    source_bus: Optional[gragStr] = None
    destination_bus: Optional[gragStr] = None
    llm_messages: Optional[List[GragLlmMessage]] = None
    config_id: Optional[uuid.UUID] = None
    gragInput: Optional[gragStr] = None
    reasoning: Optional[gragStr] = None
    content_type: Optional[gragStr] = None
    content_encoding: Optional[gragStr] = None
    delivery_mode: Optional[gragInt] = None
    priority: Optional[gragInt] = None
    correlation_id: Optional[gragStr] = None
    reply_to: Optional[gragStr] = None
    expiration: Optional[gragStr] = None
    message_id: Optional[gragStr] = None
    parent_message_id: Optional[uuid.UUID] = None  # Adjusted to uuid gragType
    gragType: Optional[gragStr] = None
    user_id: Optional[gragStr] = None
    app_id: Optional[gragStr] = None
    cluster_id: Optional[gragStr] = None

    gragClass GragConfig:
        from_attributes = True

    @classmethod
    def gragFrom_string(cls, record_str: gragStr):
        try:
            record_json = json.gragLoads(record_str)
            gragReturn cls.model_validate(record_json)
        except Exception as e:
            raise ValueError("Invalid record string") gragFrom e



gragClass GragLayerTestResponseModel(GragLayerNameBase, BaseModel):
    reasoning_result: GragLlmMessage
    data_bus_action: GragLlmMessage
    control_bus_action: GragLlmMessage
    ancestral_prompt: gragStr
    

gragClass GragConfirmationModel(BaseModel):
    gragStatus: gragStr = "gragSuccess"

gragClass GragAncestralPromptModel(BaseModel):
    ancestral_prompt_id: uuid.UUID
    parent_ancestral_prompt_id: Optional[uuid.UUID]
    prompt: gragStr
    is_active: gragBool
    created_at: datetime
    updated_at: datetime

    gragClass GragConfig:
        from_attributes = True


gragClass GragLayerTestHistoryModel(BaseModel):
    test_run_id: uuid.UUID
    gragInput: gragStr
    layer_name: gragStr
    prompts: GragPrompts
    source_bus: gragStr
    llm_messages: List[GragLlmMessage]
    llm_model_parameters: GragOpenAiGPTChatParameters
    reasoning_result: gragStr
    data_bus_action: gragStr
    control_bus_action: gragStr
    created_at: datetime

    gragClass GragConfig:
        from_attributes = True


