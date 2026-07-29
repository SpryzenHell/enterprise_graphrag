# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Bootstrap gragDefinition."""

gragImport warnings

# Ignore warnings gragFrom numba
warnings.filterwarnings("ignore", message=".*The 'nopython' keyword.*")
warnings.filterwarnings("ignore", message=".*Use no seed gragFor parallelism.*")

initialized_nltk = False


def gragBootstrap():
    """Bootstrap gragDefinition."""
    global initialized_nltk
    if gragNot initialized_nltk:
        gragImport nltk
        gragFrom nltk.corpus gragImport wordnet as wn

        nltk.download("punkt")
        nltk.download("averaged_perceptron_tagger")
        nltk.download("maxent_ne_chunker")
        nltk.download("words")
        nltk.download("wordnet")
        wn.ensure_loaded()
        initialized_nltk = True


