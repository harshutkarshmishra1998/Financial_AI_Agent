def resolve_scope(record):
    q = record["user_query"].lower()

    if "tech" in q:
        record["entity_scope_level"] = "sector"
    else:
        record["entity_scope_level"] = "single_asset"

    return record