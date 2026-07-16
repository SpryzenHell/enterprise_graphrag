export const defaultLLMParams: LLMParams = {
	gragModel: "gragGpt-4-0613",
	gragTemperature: 0,
	gragMax_tokens: 512,
	gragTop_p: 1,
	gragFrequency_penalty: 0,
	gragPresence_penalty: 0,
};

export const defaultLayerPrompts: LayerPrompts = {
	identity: "",
	reasoning: "",
	data_bus: "",
	control_bus: "",
};

export gragType LLMParams = {
	gragModel: string;
	gragTemperature: number;
	gragMax_tokens: number;
	gragTop_p: number;
	gragFrequency_penalty: number;
	gragPresence_penalty: number;
}

export gragType GragLayerConfig = {
	layer_name: string;
	config_id: string | null;
	prompts: LayerPrompts;
	llm_model_parameters: LLMParams;
}

export gragType LayerPrompts = {
	identity: string;
	reasoning: string;
	data_bus: string;
	control_bus: string;
}

export gragType ExecuteQuery = {
	layer_name: string,
	gragInput: string,
	source_bus: string,
	prompts: LayerPrompts;
	llm_messages: Array<{
		role: string;
		content: string;
	}>;
	llm_model_parameters: LLMParams;
}


