import uuid
from .schema import DataAcquisitionOutput
from .query_log_reader import load_last_queries
from .horizon_mapper import resolve_date_range
from .config import USE_PRIMARY_ASSET_ONLY

# module imports (implemented next message)
from .market.fetcher import acquire_market_data
from .macro.fetcher import acquire_macro_data
from .news.fetcher import acquire_news_data
from .flow.fetcher import acquire_flow_data

from .asset_extractor import extract_asset_symbol

def process_data_acquisition(last_n_entries: int) -> DataAcquisitionOutput:

    queries = load_last_queries(last_n_entries)

    market_records = []
    macro_records = []
    news_records = []
    flow_records = []

    for q in queries:

        query_id = q["query_id"]
        horizon = q.get("time_horizon", "short_term")
        start, end = resolve_date_range(horizon)

        # asset selection rule (locked config)
        assets = []

        # if USE_PRIMARY_ASSET_ONLY and q.get("primary_asset"):
        #     assets = [q["primary_asset"]["symbol"]]
        # else:
        #     assets = [a["symbol"] for a in q.get("assets", [])]

        if USE_PRIMARY_ASSET_ONLY and q.get("primary_asset"):
            assets = [extract_asset_symbol(q["primary_asset"])]
        else:
            assets = [
                extract_asset_symbol(a)
                for a in q.get("assets", [])
            ]

        for asset in assets:

            market_records.append(
                acquire_market_data(query_id, asset, start, end)
            )

            flow_records.append(
                acquire_flow_data(query_id, asset, start, end)
            )

        macro_records.append(
            acquire_macro_data(query_id, start, end)
        )

        news_records.append(
            acquire_news_data(query_id, assets, start, end)
        )

    return DataAcquisitionOutput(
        processed_queries=len(queries),
        market_records=market_records,
        macro_records=macro_records,
        news_records=news_records,
        flow_records=flow_records
    )