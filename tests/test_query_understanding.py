# from unittest import result
from query_engine_v2.understanding.pipeline import process_query


def run_tests():
    print("Running asset resolution tests...\n")

    queries = [
        "Why did Tesla stock rise last month?",
        "Predict Nvidia price next quarter",
        "What is Bitcoin outlook for 2025?",
        "Explain gold price drop today",  
        "Why did Reliance stock fall?",
        "Why did Meta rise yesterday?",
        "Explain Amazon price movement today",
        "Why did Apple fall despite earnings?",
        "Why is Shell stock volatile?",
        "What happened to Tata recently?",
        "Why did HSBC drop in London trading?",
        "Explain Toyota stock movement in Japan",
        "Reliance share performance on NSE today",
        "Why did BP fall on LSE?",
        "Why did SOL crash this week?",
        "Explain ADA price movement",
        "Is DOT recovering today?",
        "Why did LINK spike suddenly?",
        "Why did gold fall today?",
        "Why is silver rising?",
        "Oil price prediction next month",
        "Copper demand outlook",
        "Compare Tesla and Nvidia performance last quarter",
        "Why did Bitcoin rise while Ethereum fell?",
        "Gold vs USD correlation this month",
        "Apple vs Microsoft earnings reaction",
        "Why did Tesla rally after Q3 earnings but fall later?",
        "Bitcoin trend since the last halving",
        "Gold performance post Fed announcement",
        "Oil price movement during the pandemic period",
        "What pushed Nvidia upward momentum recently?",
        "Tesla drawdown reasons?",
        "Drivers behind Bitcoin surge?",
        "Forces impacting gold valuation?",
        "Why did Amazon rainforest decline?",
        "Apple fruit production trends",
        "Gold jewelry demand in India",
        "Shell gas usage worldwide",
        "Why did Arm Holdings jump after listing?",
        "Reddit stock performance after IPO",
        "Instacart share price movement",
        "Latest performance of OpenAI token (hypothetical)",
        "Why did the market crash today?",
        "Explain recent volatility",
        "What caused the rally this week?",
        "Future outlook?",
    ]

    for q in queries:
        result = process_query(q)

        print("QUERY:", q)
        print("SEMANTICS:", result.query_semantics)

        print("PRIMARY ASSET:",
            result.primary_asset.model_dump() if result.primary_asset else None)

        print("ALL ASSETS:",
            [a.model_dump() for a in result.assets])

        print("INTENT:", result.question_type)
        print("TIME:", result.time_horizon)
        print("CONFIDENCE:", result.resolution_confidence)
        print("AMBIGUOUS:", result.resolution_ambiguous)
        print("TOP CANDIDATES:", [a.model_dump() for a in result.assets])
        print("RELATIONSHIP TYPE:", result.relationship_type)
        print("RELATIONSHIP DIRECTION:", result.relationship_direction)
        print("RELATIONSHIP CONFIDENCE:", result.relationship_confidence)
        print("-" * 60)

        if result.primary_asset:
            assert isinstance(result.primary_asset.resolved, bool)

    print("\nAll tests passed.")


if __name__ == "__main__":
    run_tests()