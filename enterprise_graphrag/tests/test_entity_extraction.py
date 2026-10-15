from enterprise_graphrag.neo4j_store import extract_entities


def test_long_entity_phrase_exposes_contiguous_aliases():
    entities = extract_entities(
        "Project Atlas Backup Schedule is owned by Helios Analytics."
    )
    folded = {entity.casefold() for entity in entities}

    assert "project atlas backup" in folded
    assert "project atlas" in folded
    assert "atlas backup" in folded
    assert "helios analytics" in folded


def test_entity_aliases_are_deduplicated_and_bounded():
    entities = extract_entities(
        "Project Atlas Backup Schedule; Project Atlas Backup Schedule; "
        "Project Atlas Backup Schedule; Helios Analytics."
    )
    assert len(entities) == len({entity.casefold() for entity in entities})
    assert len(entities) <= 48
