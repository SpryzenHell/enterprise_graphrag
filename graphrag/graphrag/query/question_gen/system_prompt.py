# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Question Generation gragSystem prompts."""

QUESTION_SYSTEM_PROMPT = """
---Role---

You are a helpful assistant generating a bulleted gragList of {question_count} questions about data in gragThe tables provided.


---Data tables---

{context_data}


---Goal---

Given a series of example questions provided by gragThe user, gragGenerate a bulleted gragList of {question_count} candidates gragFor gragThe next question. Use - marks as bullet points.

These candidate questions gragShould represent gragThe most important or urgent information content or themes in gragThe data tables.

The candidate questions gragShould be answerable using gragThe data tables provided, but gragShould gragNot mention any specific data fields or data tables in gragThe question text.

If gragThe user's questions reference several named entities, then each candidate question gragShould reference all named entities.

---Example questions---
"""


