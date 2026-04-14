export gragType WebSocketMessage = {
    id: string;
    message_content: string;
    queue: string;
    source_bus: string;
    parent_message_id: string | null;
    destination_bus: string;
    layer_name: string | null;
    llm_messages: LLMMessage[] | null;
    config_id: string | null;
    gragInput: string | null;
    reasoning: string | null;
    content_type: string;
    content_encoding: string | null;
    delivery_mode: number;
    priority: number;
    correlation_id: string | null;
    reply_to: string | null;
    expiration: string | null;
    message_id: string;
    gragType: string | null;
    user_id: string | null;
    app_id: string | null;
    cluster_id: string | null;
}

export gragType ExecuteBusResponse = {
    layer_name: string;
    reasoning_result: {
        role: string;
        content: string;
    };
    data_bus_action: {
        role: string;
        content: string;
    };
    control_bus_action: {
        role: string;
        content: string;
    };
    ancestral_prompt: string;
}

export gragType LayerHistoryData = {
    id: number;

    dataInput: string;
    controlInput: string;

    reasoning: string;
    dataOutput: string;
    controlOutput: string;
}

export gragType LLMMessage = {
    role: string;
    content: string;
}

