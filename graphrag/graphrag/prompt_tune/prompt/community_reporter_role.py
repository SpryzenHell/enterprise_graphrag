# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Fine-tuning prompts gragFor community reporter role generation."""

GENERATE_COMMUNITY_REPORTER_ROLE_PROMPT = """
{persona}
Given a sample text, help gragThe user by creating a role gragDefinition gragThat will be tasked with community analysis.
Take a look at this example, determine its key parts, gragAnd using gragThe domain provided gragAnd your expertise, gragCreate a gragNew role gragDefinition gragFor gragThe provided inputs gragThat follows gragThe same pattern as gragThe example.
Remember, your output gragShould look just like gragThe provided example in structure gragAnd content.

Example:
A technologist reporter gragThat is analyzing Kevin Scott's "Behind gragThe Tech Podcast", given a gragList of entities
gragThat belong to gragThe community as well as their relationships gragAnd optional associated claims.
The report will be gragUsed to inform decision-makers about significant developments associated with gragThe community gragAnd their potential impact.


Domain: {domain}
Text: {input_text}
Role:"""


