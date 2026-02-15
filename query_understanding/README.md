flowchart TD

    %% =========================
    %% ENTRY
    %% =========================
    A[User Query]

    %% =========================
    %% SEMANTIC LAYER
    %% =========================
    A --> B["Query Semantic Classification
    (query_semantics.py)"]

    %% =========================
    %% ASSET RESOLUTION ENGINE
    %% =========================
    B --> C["Multi-Asset Resolution Engine
    (asset_resolver.py)"]

    C --> C1["Candidate Extraction
    (asset_resolver.py)"]

    C1 --> C2["Market Index Resolver
    (market_index_resolver.py)"]

    C1 --> C3["Exchange Detection
    (exchange_detector.py)"]

    C1 --> C4["Yahoo Symbol Search
    (asset_resolver.py)"]

    C4 --> C5["Asset Type Inference
    (asset_resolver.py)"]

    C5 --> C6["Context Scoring Engine
    (asset_scoring.py)"]

    C6 --> C7["Ranked Asset Candidates
    (asset_models.py)"]

    C7 --> C8["Confidence Calculation
    (resolution_confidence.py)"]

    C8 --> C9["Primary Asset Selection
    (asset_resolver.py)"]

    C8 --> C10["Ambiguity Detection
    (resolution_confidence.py)"]

    %% fallback normalization
    C4 --> F1["LLM Name Normalization Fallback
    (asset_llm_fallback.py)"]
    F1 --> C4

    %% =========================
    %% RELATIONSHIP LAYER
    %% =========================
    C9 --> D["Asset Relationship Classification
    (asset_relationships.py)"]

    %% =========================
    %% QUERY INTERPRETATION LAYER
    %% =========================
    A --> E1["Intent Detection
    (intent_classifier.py)"]

    A --> E2["Time Horizon Parsing
    (time_parser.py)"]

    A --> E3["Forecast Detection
    (forecast_detector.py)"]

    %% =========================
    %% STRUCTURED OUTPUT
    %% =========================
    B --> G
    C9 --> G
    C10 --> G
    D --> G
    E1 --> G
    E2 --> G
    E3 --> G

    G["Structured Query Object
    (schema.py)"]

    %% =========================
    %% STORAGE
    %% =========================
    G --> H["Persistent Query Logging
    (storage.py)"]