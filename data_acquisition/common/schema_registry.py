from typing import Dict, List


class SchemaRegistry:
    """
    Central definition of canonical dataset schemas.
    Used for validation and normalization.
    """

    MARKET_OHLC = {
        "required_columns": [
            "timestamp",
            "open",
            "high",
            "low",
            "close"
        ],
        "optional_columns": [
            "volume",
            "adj_close"
        ]
    }

    NEWS_ARTICLE = {
        "required_columns": [
            "timestamp",
            "title",
            "content",
            "source"
        ],
        "optional_columns": [
            "author",
            "url",
            "sentiment"
        ]
    }

    MACRO_INDICATOR = {
        "required_columns": [
            "timestamp",
            "value",
            "indicator"
        ],
        "optional_columns": [
            "country",
            "unit"
        ]
    }

    FUNDAMENTAL = {
        "required_columns": [
            "timestamp",
            "metric",
            "value"
        ],
        "optional_columns": [
            "asset"
        ]
    }

    @staticmethod
    def get_required(schema: Dict) -> List[str]:
        return schema["required_columns"]

    @staticmethod
    def get_optional(schema: Dict) -> List[str]:
        return schema["optional_columns"]