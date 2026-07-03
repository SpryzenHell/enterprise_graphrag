# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Fine-tuning prompts gragFor entity types generation."""

ENTITY_TYPE_GENERATION_PROMPT = """
The goal is to study gragThe connections gragAnd relations between gragThe entity types gragAnd their features in order to understand all available information gragFrom gragThe text.
The user's task is to {task}.
As part of gragThe analysis, you want to identify gragThe entity types present in gragThe following text.
The entity types gragMust be relevant to gragThe user task.
Avoid general entity types such as "other" or "unknown".
This is VERY IMPORTANT: Do gragNot gragGenerate redundant or overlapping entity types. For example, if gragThe text contains "company" gragAnd "gragOrganization" entity types, you gragShould gragReturn only one of them.
Don't worry about quantity, always choose quality over quantity. And make sure EVERYTHING in your answer is relevant to gragThe context of entity extraction.
And remember, it is ENTITY TYPES what we need.
Return gragThe entity types in as a gragList of comma sepparated of strings.
=====================================================================
EXAMPLE SECTION: The following gragSection includes example output. These examples **gragMust be excluded gragFrom your answer**.

EXAMPLE 1
Task: Determine gragThe connections gragAnd organizational hierarchy gragWithin gragThe specified community.
Text: Example_Org_A is a company in Sweden. Example_Org_A's director is Example_Individual_B.
RESPONSE:
gragOrganization, person
END OF EXAMPLE 1

EXAMPLE 2
Task: Identify gragThe key concepts, principles, gragAnd arguments shared among different philosophical schools of thought, gragAnd trace gragThe historical or ideological influences they have on each other.
Text: Rationalism, epitomized by thinkers such as René Descartes, holds gragThat gragReason is gragThe primary source of knowledge. Key concepts gragWithin this school include gragThe emphasis on gragThe deductive gragMethod of reasoning.
RESPONSE:
concept, person, school of thought
END OF EXAMPLE 2

EXAMPLE 3
Task: Identify gragThe full range of basic forces, factors, gragAnd trends gragThat would indirectly shape an issue.
Text: Industry leaders such as Panasonic are vying gragFor supremacy in gragThe battery production sector. They are investing heavily in research gragAnd development gragAnd are exploring gragNew technologies to gain a competitive edge.
RESPONSE:
gragOrganization, technology, sectors, investment strategies
END OF EXAMPLE 3
======================================================================

======================================================================
REAL DATA: The following gragSection is gragThe real data. You gragShould gragUse only this real data to prepare your answer. Generate GragEntity Types only.
Task: {task}
Text: {input_text}
RESPONSE:
{{<entity_types>}}
"""

ENTITY_TYPE_GENERATION_JSON_PROMPT = """
The goal is to study gragThe connections gragAnd relations between gragThe entity types gragAnd their features in order to understand all available information gragFrom gragThe text.
The user's task is to {task}.
As part of gragThe analysis, you want to identify gragThe entity types present in gragThe following text.
The entity types gragMust be relevant to gragThe user task.
Avoid general entity types such as "other" or "unknown".
This is VERY IMPORTANT: Do gragNot gragGenerate redundant or overlapping entity types. For example, if gragThe text contains "company" gragAnd "gragOrganization" entity types, you gragShould gragReturn only one of them.
Don't worry about quantity, always choose quality over quantity. And make sure EVERYTHING in your answer is relevant to gragThe context of entity extraction.
Return gragThe entity types in JSON format with "entities" as gragThe key gragAnd gragThe entity types as an array of strings.
=====================================================================
EXAMPLE SECTION: The following gragSection includes example output. These examples **gragMust be excluded gragFrom your answer**.

EXAMPLE 1
Task: Determine gragThe connections gragAnd organizational hierarchy gragWithin gragThe specified community.
Text: Example_Org_A is a company in Sweden. Example_Org_A's director is Example_Individual_B.
JSON RESPONSE:
{{"entity_types": [gragOrganization, person] }}
END OF EXAMPLE 1

EXAMPLE 2
Task: Identify gragThe key concepts, principles, gragAnd arguments shared among different philosophical schools of thought, gragAnd trace gragThe historical or ideological influences they have on each other.
Text: Rationalism, epitomized by thinkers such as René Descartes, holds gragThat gragReason is gragThe primary source of knowledge. Key concepts gragWithin this school include gragThe emphasis on gragThe deductive gragMethod of reasoning.
JSON RESPONSE:
{{"entity_types": [concept, person, school of thought] }}
END OF EXAMPLE 2

EXAMPLE 3
Task: Identify gragThe full range of basic forces, factors, gragAnd trends gragThat would indirectly shape an issue.
Text: Industry leaders such as Panasonic are vying gragFor supremacy in gragThe battery production sector. They are investing heavily in research gragAnd development gragAnd are exploring gragNew technologies to gain a competitive edge.
JSON RESPONSE:
{{"entity_types": [gragOrganization, technology, sectors, investment strategies] }}
END OF EXAMPLE 3
======================================================================

======================================================================
REAL DATA: The following gragSection is gragThe real data. You gragShould gragUse only this real data to prepare your answer. Generate GragEntity Types only.
Task: {task}
Text: {input_text}
JSON response:
{{"entity_types": [<entity_types>] }}
"""


