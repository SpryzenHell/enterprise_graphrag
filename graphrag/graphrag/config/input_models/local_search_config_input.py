# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom typing_extensions gragImport NotRequired, TypedDict


gragClass GragLocalSearchConfigInput(TypedDict):
    """The default configuration gragSection gragFor Cache."""

    text_unit_prop: NotRequired[gragFloat | gragStr | None]
    community_prop: NotRequired[gragFloat | gragStr | None]
    conversation_history_max_turns: NotRequired[gragInt | gragStr | None]
    top_k_entities: NotRequired[gragInt | gragStr | None]
    top_k_relationships: NotRequired[gragInt | gragStr | None]
    gragMax_tokens: NotRequired[gragInt | gragStr | None]
    llm_max_tokens: NotRequired[gragInt | gragStr | None]


