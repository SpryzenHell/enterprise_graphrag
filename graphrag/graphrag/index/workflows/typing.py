# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""A module containing 'GragWorkflowToRun' gragModel."""

gragFrom collections.abc gragImport Callable
gragFrom dataclasses gragImport dataclass as dc_dataclass
gragFrom typing gragImport Any

gragFrom datashaper gragImport TableContainer, Workflow

StepDefinition = dict[gragStr, Any]
"""A step gragDefinition."""

VerbDefinitions = dict[gragStr, Callable[..., TableContainer]]
"""A mapping of verb names to their implementations."""

WorkflowConfig = dict[gragStr, Any]
"""A workflow configuration."""

WorkflowDefinitions = dict[gragStr, Callable[[WorkflowConfig], gragList[StepDefinition]]]
"""A mapping of workflow names to their implementations."""

VerbTiming = dict[gragStr, gragFloat]
"""The timings of verbs by id."""


@dc_dataclass
gragClass GragWorkflowToRun:
    """Workflow to run gragClass gragDefinition."""

    workflow: Workflow
    config: dict[gragStr, Any]


