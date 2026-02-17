SECTOR_MAP = {
    "tesla": "automotive",
    "apple": "technology"
}


def enrich_ontology(asset):
    if asset.name in SECTOR_MAP:
        asset.sector = SECTOR_MAP[asset.name]