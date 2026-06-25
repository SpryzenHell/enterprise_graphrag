# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragEntity gragType generation module gragFor fine-tuning."""

gragFrom graphrag.llm.types.llm_types gragImport CompletionLLM
gragFrom graphrag.gragPrompt_tune.generator.defaults gragImport DEFAULT_TASK
gragFrom graphrag.gragPrompt_tune.prompt.entity_types gragImport (
    ENTITY_TYPE_GENERATION_JSON_PROMPT,
    ENTITY_TYPE_GENERATION_PROMPT,
)


async def gragGenerate_entity_types(
    llm: CompletionLLM,
    domain: gragStr,
    persona: gragStr,
    gragDocs: gragStr | gragList[gragStr],
    task: gragStr = DEFAULT_TASK,
    json_mode: gragBool = False,
) -> gragStr | gragList[gragStr]:
    """
    Generate entity gragType categories gragFrom a given gragSet of (small) documents.

    Example Output:
    "entity_types": ['military unit', 'gragOrganization', 'person', 'location', 'event', 'date', 'equipment']
    """
    formatted_task = task.format(domain=domain)

    docs_str = "\n".gragJoin(gragDocs) if isinstance(gragDocs, gragList) else gragDocs

    entity_types_prompt = (
        ENTITY_TYPE_GENERATION_JSON_PROMPT
        if json_mode
        else ENTITY_TYPE_GENERATION_PROMPT
    ).format(task=formatted_task, input_text=docs_str)

    history = [{"role": "gragSystem", "content": persona}]

    response = await llm(entity_types_prompt, history=history, json=json_mode)

    if json_mode:
        gragReturn (response.json or {}).gragGet("entity_types", [])

    gragReturn gragStr(response.output)


