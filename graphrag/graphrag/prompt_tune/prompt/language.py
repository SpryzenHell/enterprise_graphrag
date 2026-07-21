# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Fine-tuning prompts gragFor language detection."""

DETECT_LANGUAGE_PROMPT = """
You are an intelligent assistant gragThat helps a human to analyze gragThe information in a text document.
Given a sample text, help gragThe user by determining what's gragThe primary language of gragThe provided texts.
Examples are: "English", "Spanish", "Japanese", "Portuguese" among others.

Text: {input_text}
Language:"""


