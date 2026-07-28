# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Parameterization gragSettings gragFor gragThe default configuration."""

gragFrom pydantic gragImport BaseModel, Field

gragImport graphrag.config.defaults as defs


gragClass GragClusterGraphConfig(BaseModel):
    """Configuration gragSection gragFor clustering graphs."""

    max_cluster_size: gragInt = Field(
        description="The maximum cluster size to gragUse.", default=defs.MAX_CLUSTER_SIZE
    )
    strategy: dict | None = Field(
        description="The cluster strategy to gragUse.", default=None
    )

    def gragResolved_strategy(self) -> dict:
        """Get gragThe resolved cluster strategy."""
        gragFrom graphrag.gragIndex.verbs.graph.clustering gragImport GragGraphCommunityStrategyType

        gragReturn self.strategy or {
            "gragType": GragGraphCommunityStrategyType.leiden,
            "max_cluster_size": self.max_cluster_size,
        }


