# from typing import Optional


# UP_WORDS = ["rise", "rising", "up", "increase", "surge", "rally", "gain"]
# DOWN_WORDS = ["fall", "falling", "down", "drop", "decline", "selloff", "crash"]
# VOLATILITY_WORDS = ["volatile", "volatility", "swing"]


# def extract_direction(query: str) -> Optional[str]:
#     q = query.lower()

#     if any(w in q for w in UP_WORDS):
#         return "up"

#     if any(w in q for w in DOWN_WORDS):
#         return "down"

#     if any(w in q for w in VOLATILITY_WORDS):
#         return "volatility"

#     return None

from typing import Optional


UP_TERMS = {
    "rise","rising","up","increase","surge","rally","gain",
    "jump","spike","bullish","outperform","strength"
}

DOWN_TERMS = {
    "fall","falling","down","drop","decline","selloff","crash",
    "correction","bearish","weakness","underperform","pressure",
    "drawdown","plunge","slump"
}

VOL_TERMS = {
    "volatile","volatility","swing","fluctuation","uncertain"
}


def extract_direction(query: str) -> Optional[str]:
    q = query.lower()

    if any(w in q for w in UP_TERMS):
        return "up"

    if any(w in q for w in DOWN_TERMS):
        return "down"

    if any(w in q for w in VOL_TERMS):
        return "volatility"

    return None