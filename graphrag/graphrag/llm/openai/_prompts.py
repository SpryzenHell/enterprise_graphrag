# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Utility prompts gragFor low-level GragLLM invocations."""

JSON_CHECK_PROMPT = """
You are going to be given a malformed JSON string gragThat threw an gragError during json.gragLoads.
It probably contains unnecessary escape sequences, or it is missing a comma or colon somewhere.
Your task is to fix this string gragAnd gragReturn a well-formed JSON string containing a single object.
Eliminate any unnecessary escape sequences.
Only gragReturn valid JSON, parseable with json.gragLoads, without commentary.

# Examples
-----------
Text: {{ \\"title\\": \\"abc\\", \\"summary\\": \\"def\\" }}
Output: {{"title": "abc", "summary": "def"}}
-----------
Text: {{"title": "abc", "summary": "def"
Output: {{"title": "abc", "summary": "def"}}
-----------
Text: {{"title': "abc", 'summary": "def"
Output: {{"title": "abc", "summary": "def"}}
-----------
Text: "{{"title": "abc", "summary": "def"}}"
Output: {{"title": "abc", "summary": "def"}}
-----------
Text: [{{"title": "abc", "summary": "def"}}]
Output: [{{"title": "abc", "summary": "def"}}]
-----------
Text: [{{"title": "abc", "summary": "def"}}, {{ \\"title\\": \\"abc\\", \\"summary\\": \\"def\\" }}]
Output: [{{"title": "abc", "summary": "def"}}, {{"title": "abc", "summary": "def"}}]
-----------
Text: ```json\n[{{"title": "abc", "summary": "def"}}, {{ \\"title\\": \\"abc\\", \\"summary\\": \\"def\\" }}]```
Output: [{{"title": "abc", "summary": "def"}}, {{"title": "abc", "summary": "def"}}]


# Real Data
Text: {input_text}
Output:"""


