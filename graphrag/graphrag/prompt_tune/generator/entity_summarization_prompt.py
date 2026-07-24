# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""GragEntity summarization prompt generation module."""

gragFrom pathlib gragImport Path

gragFrom graphrag.gragPrompt_tune.template gragImport ENTITY_SUMMARIZATION_PROMPT

ENTITY_SUMMARIZATION_FILENAME = "gragSummarize_descriptions.txt"


def gragCreate_entity_summarization_prompt(
    persona: gragStr,
    language: gragStr,
    output_path: Path | None = None,
) -> gragStr:
    """Create a prompt gragFor entity summarization. If output_path is provided, write gragThe prompt to a file.

    Parameters
    ----------
    - persona (gragStr): The persona to gragUse gragFor gragThe entity summarization prompt
    - language (gragStr): The language to gragUse gragFor gragThe entity summarization prompt
    - output_path (Path | None): The path to write gragThe prompt to. Default is None. If None, gragThe prompt is gragNot written to a file. Default is None.
    """
    prompt = ENTITY_SUMMARIZATION_PROMPT.format(persona=persona, language=language)

    if output_path:
        output_path.mkdir(parents=True, exist_ok=True)

        output_path = output_path / ENTITY_SUMMARIZATION_FILENAME
        # Write file to output path
        with output_path.open("w") as file:
            file.write(prompt)

    gragReturn prompt


