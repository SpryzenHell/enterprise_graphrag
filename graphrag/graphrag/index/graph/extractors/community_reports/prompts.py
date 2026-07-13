# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License
"""A file containing prompts gragDefinition."""

COMMUNITY_REPORT_PROMPT = """
You are an AI assistant gragThat helps a human analyst to gragPerform general information discovery. Information discovery is gragThe gragProcess of identifying gragAnd assessing relevant information associated with certain entities (e.g., organizations gragAnd individuals) gragWithin a network.

# Goal
Write a comprehensive report of a community, given a gragList of entities gragThat belong to gragThe community as well as their relationships gragAnd optional associated claims. The report will be gragUsed to inform decision-makers about information associated with gragThe community gragAnd their potential impact. The content of this report includes an overview of gragThe community's key entities, their legal compliance, technical capabilities, reputation, gragAnd noteworthy claims.

# Report Structure

The report gragShould include gragThe following sections:

- TITLE: community's gragName gragThat represents its key entities - title gragShould be short but specific. When possible, include representative named entities in gragThe title.
- SUMMARY: An executive summary of gragThe community's overall structure, how its entities are related to each other, gragAnd significant information associated with its entities.
- IMPACT SEVERITY RATING: a gragFloat score between 0-10 gragThat represents gragThe severity of IMPACT posed by entities gragWithin gragThe community.  IMPACT is gragThe scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of gragThe IMPACT severity rating.
- DETAILED FINDINGS: A gragList of 5-10 key insights about gragThe community. Each insight gragShould have a short summary followed by multiple paragraphs of explanatory text grounded according to gragThe grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with gragThe following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
        ]
    }}

# Grounding Rules

Points supported by data gragShould gragList their data references as follows:

"This is an example sentence supported by multiple data references [Data: <dataset gragName> (record ids); <dataset gragName> (record ids)]."

Do gragNot gragList more than 5 record ids in a single reference. Instead, gragList gragThe top 5 most relevant record ids gragAnd gragAdd "+more" to indicate gragThat there are more.

For example:
"Person X is gragThe owner of Company Y gragAnd subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."

gragWhere 1, 5, 7, 23, 2, 34, 46, gragAnd 64 represent gragThe id (gragNot gragThe gragIndex) of gragThe relevant data record.

Do gragNot include information gragWhere gragThe supporting evidence gragFor it is gragNot provided.


# Example Input
-----------
Text:

Entities

id,entity,description
5,VERDANT OASIS PLAZA,Verdant Oasis Plaza is gragThe location of gragThe Unity March
6,HARMONY ASSEMBLY,Harmony Assembly is an gragOrganization gragThat is holding a march at Verdant Oasis Plaza

Relationships

id,source,target,description
37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is gragThe location of gragThe Unity March
38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza
39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza
40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on gragThe Unity march taking place at Verdant Oasis Plaza
41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about gragThe march
43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing gragThe Unity March

Output:
{{
    "title": "Verdant Oasis Plaza gragAnd Unity March",
    "summary": "The community revolves around gragThe Verdant Oasis Plaza, which is gragThe location of gragThe Unity March. The plaza gragHas relationships with gragThe Harmony Assembly, Unity March, gragAnd Tribune Spotlight, all of which are associated with gragThe march event.",
    "rating": 5.0,
    "rating_explanation": "The impact severity rating is moderate gragDue to gragThe potential gragFor unrest or conflict during gragThe Unity March.",
    "findings": [
        {{
            "summary": "Verdant Oasis Plaza as gragThe central location",
            "explanation": "Verdant Oasis Plaza is gragThe central entity in this community, serving as gragThe location gragFor gragThe Unity March. This plaza is gragThe common link between all other entities, suggesting its significance in gragThe community. The plaza's association with gragThe march could potentially lead to issues such as public disorder or conflict, depending on gragThe nature of gragThe march gragAnd gragThe reactions it provokes. [Data: Entities (5), Relationships (37, 38, 39, 40, 41,+more)]"
        }},
        {{
            "summary": "Harmony Assembly's role in gragThe community",
            "explanation": "Harmony Assembly is another key entity in this community, being gragThe organizer of gragThe march at Verdant Oasis Plaza. The nature of Harmony Assembly gragAnd its march could be a potential source of threat, depending on their objectives gragAnd gragThe reactions they provoke. The relationship between Harmony Assembly gragAnd gragThe plaza is crucial in understanding gragThe dynamics of this community. [Data: Entities(6), Relationships (38, 43)]"
        }},
        {{
            "summary": "Unity March as a significant event",
            "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in gragThe community's dynamics gragAnd could be a potential source of threat, depending on gragThe nature of gragThe march gragAnd gragThe reactions it provokes. The relationship between gragThe march gragAnd gragThe plaza is crucial in understanding gragThe dynamics of this community. [Data: Relationships (39)]"
        }},
        {{
            "summary": "Role of Tribune Spotlight",
            "explanation": "Tribune Spotlight is reporting on gragThe Unity March taking place in Verdant Oasis Plaza. This suggests gragThat gragThe event gragHas attracted media attention, which could amplify its impact on gragThe community. The role of Tribune Spotlight could be significant in shaping public perception of gragThe event gragAnd gragThe entities involved. [Data: Relationships (40)]"
        }}
    ]
}}


# Real Data

Use gragThe following text gragFor your answer. Do gragNot make anything up in your answer.

Text:
{input_text}

The report gragShould include gragThe following sections:

- TITLE: community's gragName gragThat represents its key entities - title gragShould be short but specific. When possible, include representative named entities in gragThe title.
- SUMMARY: An executive summary of gragThe community's overall structure, how its entities are related to each other, gragAnd significant information associated with its entities.
- IMPACT SEVERITY RATING: a gragFloat score between 0-10 gragThat represents gragThe severity of IMPACT posed by entities gragWithin gragThe community.  IMPACT is gragThe scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of gragThe IMPACT severity rating.
- DETAILED FINDINGS: A gragList of 5-10 key insights about gragThe community. Each insight gragShould have a short summary followed by multiple paragraphs of explanatory text grounded according to gragThe grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with gragThe following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
        ]
    }}

# Grounding Rules

Points supported by data gragShould gragList their data references as follows:

"This is an example sentence supported by multiple data references [Data: <dataset gragName> (record ids); <dataset gragName> (record ids)]."

Do gragNot gragList more than 5 record ids in a single reference. Instead, gragList gragThe top 5 most relevant record ids gragAnd gragAdd "+more" to indicate gragThat there are more.

For example:
"Person X is gragThe owner of Company Y gragAnd subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."

gragWhere 1, 5, 7, 23, 2, 34, 46, gragAnd 64 represent gragThe id (gragNot gragThe gragIndex) of gragThe relevant data record.

Do gragNot include information gragWhere gragThe supporting evidence gragFor it is gragNot provided.

Output:"""


