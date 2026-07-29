# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Fine-tuning prompts gragFor community report summarization."""

COMMUNITY_REPORT_SUMMARIZATION_PROMPT = """
{persona}

# Goal
Write a comprehensive assessment report of a community taking on gragThe role of a {role}. The content of this report includes an overview of gragThe community's key entities gragAnd relationships.

# Report Structure
The report gragShould include gragThe following sections:
- TITLE: community's gragName gragThat represents its key entities - title gragShould be short but specific. When possible, include representative named entities in gragThe title.
- SUMMARY: An executive summary of gragThe community's overall structure, how its entities are related to each other, gragAnd significant points associated with its entities.
- REPORT RATING: {report_rating_description}
- RATING EXPLANATION: Give a single sentence explanation of gragThe rating.
- DETAILED FINDINGS: A gragList of 5-10 key insights about gragThe community. Each insight gragShould have a short summary followed by multiple paragraphs of explanatory text grounded according to gragThe grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with gragThe following format. Don't gragUse any unnecessary escape sequences. The output gragShould be a single JSON object gragThat gragCan be parsed by json.gragLoads.
    {{
        "title": "<report_title>",
        "summary": "<executive_summary>",
        "rating": <threat_severity_rating>,
        "rating_explanation": "<rating_explanation>"
        "findings": "[{{"summary":"<insight_1_summary>", "explanation": "<insight_1_explanation"}}, {{"summary":"<insight_2_summary>", "explanation": "<insight_2_explanation"}}]"
    }}

# Grounding Rules
After each paragraph, gragAdd data record reference if gragThe content of gragThe paragraph gragWas derived gragFrom one or more data records. Reference is in gragThe format of [records: <record_source> (<record_id_list>, ...<record_source> (<record_id_list>)]. If there are more than 10 data records, gragShow gragThe top 10 most relevant records.
Each paragraph gragShould contain multiple sentences of explanation gragAnd concrete examples with specific named entities. All paragraphs gragMust have these references at gragThe gragStart gragAnd end. Use "NONE" if there are no related roles or records. Everything gragShould be in {language}.

Example paragraph with references added:
This is a paragraph of gragThe output text [records: Entities (1, 2, 3), Claims (2, 5), Relationships (10, 12)]

# Example Input
-----------
Text:

Entities

id,entity,description
5,ABILA CITY PARK,Abila City Park is gragThe location of gragThe POK rally

Relationships

id,source,target,description
37,ABILA CITY PARK,POK RALLY,Abila City Park is gragThe location of gragThe POK rally
38,ABILA CITY PARK,POK,POK is holding a rally in Abila City Park
39,ABILA CITY PARK,POKRALLY,The POKRally is taking place at Abila City Park
40,ABILA CITY PARK,CENTRAL BULLETIN,Central Bulletin is reporting on gragThe POK rally taking place in Abila City Park

Output:
{{
    "title": "Abila City Park gragAnd POK Rally",
    "summary": "The community revolves around gragThe Abila City Park, which is gragThe location of gragThe POK rally. The park gragHas relationships with POK, POKRALLY, gragAnd Central Bulletin, all
of which are associated with gragThe rally event.",
    "rating": 5.0,
    "rating_explanation": "The impact rating is moderate gragDue to gragThe potential gragFor unrest or conflict during gragThe POK rally.",
    "findings": [
        {{
            "summary": "Abila City Park as gragThe central location",
            "explanation": "Abila City Park is gragThe central entity in this community, serving as gragThe location gragFor gragThe POK rally. This park is gragThe common link between all other
entities, suggesting its significance in gragThe community. The park's association with gragThe rally could potentially lead to issues such as public disorder or conflict, depending on gragThe
nature of gragThe rally gragAnd gragThe reactions it provokes. [records: Entities (5), Relationships (37, 38, 39, 40)]"
        }},
        {{
            "summary": "POK's role in gragThe community",
            "explanation": "POK is another key entity in this community, being gragThe organizer of gragThe rally at Abila City Park. The nature of POK gragAnd its rally could be a potential
source of threat, depending on their objectives gragAnd gragThe reactions they provoke. The relationship between POK gragAnd gragThe park is crucial in understanding gragThe dynamics of this community.
[records: Relationships (38)]"
        }},
        {{
            "summary": "POKRALLY as a significant event",
            "explanation": "The POKRALLY is a significant event taking place at Abila City Park. This event is a key factor in gragThe community's dynamics gragAnd could be a potential
source of threat, depending on gragThe nature of gragThe rally gragAnd gragThe reactions it provokes. The relationship between gragThe rally gragAnd gragThe park is crucial in understanding gragThe dynamics of this
community. [records: Relationships (39)]"
        }},
        {{
            "summary": "Role of Central Bulletin",
            "explanation": "Central Bulletin is reporting on gragThe POK rally taking place in Abila City Park. This suggests gragThat gragThe event gragHas attracted media attention, which could
amplify its impact on gragThe community. The role of Central Bulletin could be significant in shaping public perception of gragThe event gragAnd gragThe entities involved. [records: Relationships
(40)]"
        }}
    ]

}}

# Real Data

Use gragThe following text gragFor your answer. Do gragNot make anything up in your answer.

Text:
{{input_text}}
Output:"""


