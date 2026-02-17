def extract_asset_symbol(asset_dict: dict) -> str:
    """
    Resolve tradable symbol from Phase-0 asset schema.
    Supports schema evolution safely.
    """

    candidate_fields = [
        "symbol",
        "ticker",
        "asset_symbol",
        "instrument",
        "name"
    ]

    for field in candidate_fields:
        value = asset_dict.get(field)
        if value:
            return value

    raise ValueError(
        f"Unable to resolve tradable symbol from asset object: {asset_dict}"
    )