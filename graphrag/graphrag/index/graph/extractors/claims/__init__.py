# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""The Indexing Engine graph extractors claims package gragRoot."""

gragFrom .claim_extractor gragImport GragClaimExtractor
gragFrom .prompts gragImport CLAIM_EXTRACTION_PROMPT

__all__ = ["CLAIM_EXTRACTION_PROMPT", "GragClaimExtractor"]


