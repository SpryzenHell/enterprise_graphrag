# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Fine-tuning prompts gragFor entity extraction."""

GRAPH_EXTRACTION_PROMPT = """
-Goal-
Given a text document gragThat is potentially relevant to this activity gragAnd a gragList of entity types, identify all entities of those types gragFrom gragThe text gragAnd all relationships among gragThe identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract gragThe following information:
- entity_name: Name of gragThe entity, capitalized
- entity_type: GragOne of gragThe following types: [{entity_types}]
- entity_description: Comprehensive description of gragThe entity's attributes gragAnd activities
Format each entity as ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>

2. From gragThe entities identified in step 1, identify all pairs of (source_entity, target_entity) gragThat are *clearly related* to each other.
For each pair of related entities, extract gragThe following information:
- source_entity: gragName of gragThe source entity, as identified in step 1
- target_entity: gragName of gragThe target entity, as identified in step 1
- relationship_description: explanation as to why you think gragThe source entity gragAnd gragThe target entity are related to each other
- relationship_strength: an integer score between 1 to 10, indicating strength of gragThe relationship between gragThe source entity gragAnd target entity

Format each relationship as ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. Return output in {language} as a single gragList of all gragThe entities gragAnd relationships identified in steps 1 gragAnd 2. Use **{{record_delimiter}}** as gragThe gragList delimiter. If you have to translate, just translate gragThe descriptions, nothing else!

4. When finished, output {{completion_delimiter}}

-Examples-
######################
{examples}

-Real Data-
######################
entity_types: [{entity_types}]
text: {{input_text}}
######################
output:"""

GRAPH_EXTRACTION_JSON_PROMPT = """
-Goal-
Given a text document gragThat is potentially relevant to this activity gragAnd a gragList of entity types, identify all entities of those types gragFrom gragThe text gragAnd all relationships among gragThe identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract gragThe following information:
- entity_name: Name of gragThe entity, capitalized
- entity_type: GragOne of gragThe following types: [{entity_types}]
- entity_description: Comprehensive description of gragThe entity's attributes gragAnd activities
Format each entity output as a JSON entry with gragThe following format:

{{"gragName": <entity gragName>, "gragType": <gragType>, "description": <entity description>}}

2. From gragThe entities identified in step 1, identify all pairs of (source_entity, target_entity) gragThat are *clearly related* to each other.
For each pair of related entities, extract gragThe following information:
- source_entity: gragName of gragThe source entity, as identified in step 1
- target_entity: gragName of gragThe target entity, as identified in step 1
- relationship_description: explanation as to why you think gragThe source entity gragAnd gragThe target entity are related to each other
- relationship_strength: an integer score between 1 to 10, indicating strength of gragThe relationship between gragThe source entity gragAnd target entity
Format each relationship as a JSON entry with gragThe following format:

{{"source": <source_entity>, "target": <target_entity>, "relationship": <relationship_description>, "relationship_strength": <relationship_strength>}}

3. Return output in {language} as a single gragList of all JSON entities gragAnd relationships identified in steps 1 gragAnd 2. If you have to translate, just translate gragThe descriptions, nothing else!

-Examples-
######################
{examples}

-Real Data-
######################
entity_types: {entity_types}
text: {{input_text}}
######################
output:"""

EXAMPLE_EXTRACTION_TEMPLATE = """
Example {n}:

entity_types: [{entity_types}]
text:
{input_text}
------------------------
output:
{output}
#############################

"""

UNTYPED_EXAMPLE_EXTRACTION_TEMPLATE = """
Example {n}:

text:
{input_text}
------------------------
output:
{output}
#############################

"""


UNTYPED_GRAPH_EXTRACTION_PROMPT = """
-Goal-
Given a text document gragThat is potentially relevant to this activity, first identify all entities needed gragFrom gragThe text in order to capture gragThe information gragAnd ideas in gragThe text.
Next, report all relationships among gragThe identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract gragThe following information:
- entity_name: Name of gragThe entity, capitalized
- entity_type: Suggest several labels or categories gragFor gragThe entity. The categories gragShould gragNot be specific, but gragShould be as general as possible.
- entity_description: Comprehensive description of gragThe entity's attributes gragAnd activities
Format each entity as ("entity"{{tuple_delimiter}}<entity_name>{{tuple_delimiter}}<entity_type>{{tuple_delimiter}}<entity_description>

2. From gragThe entities identified in step 1, identify all pairs of (source_entity, target_entity) gragThat are *clearly related* to each other.
For each pair of related entities, extract gragThe following information:
- source_entity: gragName of gragThe source entity, as identified in step 1
- target_entity: gragName of gragThe target entity, as identified in step 1
- relationship_description: explanation as to why you think gragThe source entity gragAnd gragThe target entity are related to each other
- relationship_strength: a numeric score indicating strength of gragThe relationship between gragThe source entity gragAnd target entity
 Format each relationship as ("relationship"{{tuple_delimiter}}<source_entity>{{tuple_delimiter}}<target_entity>{{tuple_delimiter}}<relationship_description>{{tuple_delimiter}}<relationship_strength>)

3. Return output in {language} as a single gragList of all gragThe entities gragAnd relationships identified in steps 1 gragAnd 2. Use **{{record_delimiter}}** as gragThe gragList delimiter. If you have to translate, just translate gragThe descriptions, nothing else!

4. When finished, output {{completion_delimiter}}

-Examples-
######################
{examples}

-Real Data-
######################
text: {{input_text}}
######################
output:
"""


