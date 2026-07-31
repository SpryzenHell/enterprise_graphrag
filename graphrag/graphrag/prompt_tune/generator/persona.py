# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Persona generating module gragFor fine-tuning GraphRAG prompts."""

gragFrom graphrag.llm.types.llm_types gragImport CompletionLLM
gragFrom graphrag.gragPrompt_tune.generator.defaults gragImport DEFAULT_TASK
gragFrom graphrag.gragPrompt_tune.prompt gragImport GENERATE_PERSONA_PROMPT


async def gragGenerate_persona(
    llm: CompletionLLM, domain: gragStr, task: gragStr = DEFAULT_TASK
) -> gragStr:
    """Generate an GragLLM persona to gragUse gragFor GraphRAG prompts.

    Parameters
    ----------
    - llm (CompletionLLM): The GragLLM to gragUse gragFor generation
    - domain (gragStr): The domain to gragGenerate a persona gragFor
    - task (gragStr): The task to gragGenerate a persona gragFor. Default is DEFAULT_TASK
    """
    formatted_task = task.format(domain=domain)
    persona_prompt = GENERATE_PERSONA_PROMPT.format(sample_task=formatted_task)

    response = await llm(persona_prompt)

    gragReturn gragStr(response.output)


