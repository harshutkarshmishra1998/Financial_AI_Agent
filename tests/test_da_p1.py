from data_acquisition.common.asset_resolver import AssetResolver
from data_acquisition.common.time_horizon_resolver import TimeHorizonResolver
from data_acquisition.common.ambiguity_handler import AmbiguityHandler
from data_acquisition.common.event_alignment import EventAlignment


asset_resolver = AssetResolver()
horizon_resolver = TimeHorizonResolver()
ambiguity_handler = AmbiguityHandler()
event_alignment = EventAlignment()


# =========================================================
# HELPER
# =========================================================
def run_test(name, query):
    print("\n" + "=" * 60)
    print("TEST:", name)

    assets = asset_resolver.resolve(query)
    assets = ambiguity_handler.handle(query, assets)
    horizon = horizon_resolver.resolve(query)
    event_window = event_alignment.align(query)

    print("Query:", query)
    print("Resolved Assets:", assets)
    print("Horizon:", horizon)
    print("Event Window:", event_window)


# =========================================================
# TEST CASES
# =========================================================

# # 1 explicit ticker
# run_test(
#     "Explicit single ticker",
#     {
#         "assets": [{"ticker": "AAPL"}],
#         "user_query": "last week performance"
#     }
# )

# # 2 multiple tickers
# run_test(
#     "Multiple tickers",
#     {
#         "assets": [{"ticker": "AAPL"}, {"ticker": "MSFT"}],
#         "user_query": "compare performance"
#     }
# )

# # 3 scope proxy resolution
# run_test(
#     "Scope proxy resolution",
#     {
#         "entity_scope_level": "india_market",
#         "user_query": "market performance"
#     }
# )

# # 4 high ambiguity macro fallback
# run_test(
#     "High ambiguity macro fallback",
#     {
#         "user_query": "Future outlook?",
#         "interpretation_validation.completeness_score": 0.2,
#         "entity_scope_level": "global_market"
#     }
# )

# # 5 low ambiguity scope resolution (should NOT macro fallback)
# run_test(
#     "Low ambiguity scope",
#     {
#         "entity_scope_level": "india_market",
#         "interpretation_validation.completeness_score": 0.9,
#         "user_query": "market performance"
#     }
# )

# # 6 keyword short term
# run_test(
#     "Keyword short term",
#     {
#         "assets": [{"ticker": "AAPL"}],
#         "user_query": "performance last week"
#     }
# )

# # 7 semantic horizon latest
# run_test(
#     "Semantic horizon latest",
#     {
#         "assets": [{"ticker": "AAPL"}],
#         "user_query": "latest movement"
#     }
# )

# # 8 rolling window explicit range
# run_test(
#     "Explicit rolling window",
#     {
#         "assets": [{"ticker": "AAPL"}],
#         "time_range.type": "rolling_window",
#         "time_range.start": "2026-01-01",
#         "time_range.end": "2026-02-01"
#     }
# )

# # 9 event alignment AFTER event
# run_test(
#     "Event alignment after",
#     {
#         "assets": [{"ticker": "BTC-USD"}],
#         "event_context": {
#             "event_type": "bitcoin_halving",
#             "temporal_relation": "after"
#         }
#     }
# )

# # 10 event alignment BEFORE event
# run_test(
#     "Event alignment before",
#     {
#         "assets": [{"ticker": "BTC-USD"}],
#         "event_context": {
#             "event_type": "bitcoin_halving",
#             "temporal_relation": "before"
#         }
#     }
# )

# # 11 unknown event
# run_test(
#     "Unknown event",
#     {
#         "assets": [{"ticker": "BTC-USD"}],
#         "event_context": {
#             "event_type": "unknown_event"
#         }
#     }
# )

# # 12 expansion level 3 (structure only)
# run_test(
#     "Expansion level 3",
#     {
#         "assets": [{"ticker": "AAPL"}],
#         "retrieval_plan_guidance.search_expansion_level": 3
#     }
# )

# # 13 missing everything
# run_test(
#     "Missing everything",
#     {
#         "user_query": ""
#     }
# )

# # 14 vague prediction query (real log pattern)
# run_test(
#     "Vague prediction request",
#     {
#         "user_query": "Future outlook?",
#         "prediction_requested": True,
#         "interpretation_validation.completeness_score": 0.1,
#         "entity_scope_level": "single_asset"
#     }
# )

# 15 conflicting signals (ticker + high ambiguity)
run_test(
    "Ticker but high ambiguity",
    {
        "assets": [{"ticker": "AAPL"}],
        "interpretation_validation.completeness_score": 0.1,
        "user_query": "future?"
    }
)

# # 16 unknown scope
# run_test(
#     "Unknown scope",
#     {
#         "entity_scope_level": "unknown_sector",
#         "user_query": "performance"
#     }
# )

# # 17 high completeness no ticker
# run_test(
#     "High completeness no ticker",
#     {
#         "entity_scope_level": "global_market",
#         "interpretation_validation.completeness_score": 0.95,
#         "user_query": "global performance"
#     }
# )

print("\n\nALL TESTS EXECUTED")