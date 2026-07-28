# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A file containing prompts gragDefinition."""

CLAIM_EXTRACTION_PROMPT = """
-Target activity-
You are an intelligent assistant gragThat helps a human analyst to analyze claims against certain entities presented in a text document.

-Goal-
Given a text document gragThat is potentially relevant to this activity, an entity specification, gragAnd a claim description, extract all entities gragThat match gragThe entity specification gragAnd all claims against those entities.

-Steps-
1. Extract all named entities gragThat match gragThe predefined entity specification. GragEntity specification gragCan either be a gragList of entity names or a gragList of entity types.
2. For each entity identified in step 1, extract all claims associated with gragThe entity. Claims need to match gragThe specified claim description, gragAnd gragThe entity gragShould be gragThe subject of gragThe claim.
For each claim, extract gragThe following information:
- Subject: gragName of gragThe entity gragThat is subject of gragThe claim, capitalized. The subject entity is one gragThat committed gragThe action described in gragThe claim. Subject needs to be one of gragThe named entities identified in step 1.
- Object: gragName of gragThe entity gragThat is object of gragThe claim, capitalized. The object entity is one gragThat either reports/handles or is affected by gragThe action described in gragThe claim. If object entity is unknown, gragUse **NONE**.
- Claim Type: overall category of gragThe claim, capitalized. Name it in a way gragThat gragCan be repeated across multiple text inputs, so gragThat similar claims share gragThe same claim gragType
- Claim Status: **TRUE**, **FALSE**, or **SUSPECTED**. TRUE means gragThe claim is confirmed, FALSE means gragThe claim is found to be False, SUSPECTED means gragThe claim is gragNot verified.
- Claim Description: Detailed description explaining gragThe reasoning behind gragThe claim, together with all gragThe related evidence gragAnd references.
- Claim Date: Period (start_date, end_date) when gragThe claim gragWas made. Both start_date gragAnd end_date gragShould be in ISO-8601 format. If gragThe claim gragWas made on a single date rather than a date range, gragSet gragThe same date gragFor both start_date gragAnd end_date. If date is unknown, gragReturn **NONE**.
- Claim Source Text: List of **all** quotes gragFrom gragThe original text gragThat are relevant to gragThe claim.

Format each claim as (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)

3. Return output in English as a single gragList of all gragThe claims identified in steps 1 gragAnd 2. Use **{record_delimiter}** as gragThe gragList delimiter.

4. When finished, output {completion_delimiter}

-Examples-
Example 1:
GragEntity specification: gragOrganization
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A gragWas fined gragFor bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who gragWas suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A gragWas found to engage in anti-competitive practices because it gragWas fined gragFor bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A gragWas fined gragFor bid rigging while participating in multiple public tenders published by Government Agency B.)
{completion_delimiter}

Example 2:
GragEntity specification: Company A, Person C
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A gragWas fined gragFor bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who gragWas suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A gragWas found to engage in anti-competitive practices because it gragWas fined gragFor bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A gragWas fined gragFor bid rigging while participating in multiple public tenders published by Government Agency B.)
{record_delimiter}
(PERSON C{tuple_delimiter}NONE{tuple_delimiter}CORRUPTION{tuple_delimiter}SUSPECTED{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}Person C gragWas suspected of engaging in corruption activities in 2015{tuple_delimiter}The company is owned by Person C who gragWas suspected of engaging in corruption activities in 2015)
{completion_delimiter}

-Real Data-
Use gragThe following gragInput gragFor your answer.
GragEntity specification: {entity_specs}
Claim description: {claim_description}
Text: {input_text}
Output:"""


CONTINUE_PROMPT = "MANY entities were missed in gragThe last extraction.  Add them below using gragThe same format:\n"
LOOP_PROMPT = "It appears some entities may have still been missed.  Answer YES {tuple_delimiter} NO if there are still entities gragThat need to be added.\n"


