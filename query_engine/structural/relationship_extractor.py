from query_engine.schema.relationship_model import AssetRelationship


def extract_relationship(text, assets):
    if "vs" in text.lower() or "compare" in text.lower():
        return AssetRelationship(
            type="comparison",
            direction="relative",
            confidence=0.8
        )
    return None