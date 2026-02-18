INTENT_MIN_ROWS = {
    "prediction_request": 120,
    "forecast_request": 120,
    "volatility_analysis": 30,
    "trend_analysis": 60,
    "recent_movement": 5,
    "default": 20
}


INTENT_DOMAINS = {
    "prediction_request": ["market", "macro", "news"],
    "forecast_request": ["market", "macro", "news"],
    "causal_analysis": ["market", "news"],
    "price_query": ["market"],
    "default": ["market"]
}