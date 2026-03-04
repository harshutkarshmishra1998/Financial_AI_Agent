import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_object_dtype,
    is_string_dtype,
)

from foundation import RunManager
from market_signal.pipeline import run_signal_pipeline
from ecosystem_graph.pipeline import EcosystemPipeline
from multistream_researcher.pipeline import run_multistream_researcher
from reasoning.pipeline import generate_anomaly_reasoning
import datetime


st.set_page_config(layout="wide")

st.title("Financial AI Agent")

symbol = st.sidebar.text_input("Symbol", "RELIANCE.NS")
start = st.sidebar.text_input("Start Date", "2019-01-01")
end = st.sidebar.text_input("End Date", "2024-01-01")

run_btn = st.sidebar.button("Run Pipeline")

# placeholders for streaming UI
signal_container = st.container()
plot_container = st.container()
graph_container = st.container()
research_container = st.container()
reasoning_container = st.container()


def to_dataframe(data):

    if isinstance(data, pd.DataFrame):
        df = data.copy()

    elif isinstance(data, list):
        df = pd.DataFrame(data)

    elif isinstance(data, dict):
        df = pd.DataFrame([data])

    else:
        df = pd.DataFrame({"value": [data]})

    # Make dataframe serialization compatible with older Streamlit Arrow parsers.
    for col in df.columns:
        series = df[col]

        # Convert python datetime objects
        if series.apply(lambda x: isinstance(x, datetime.datetime)).any():
            df[col] = pd.to_datetime(series, errors="coerce")

        # Force any string/object column to Python-native string objects.
        # This avoids Arrow "LargeUtf8" payloads that older Streamlit frontends
        # cannot decode.
        elif is_string_dtype(series) or is_object_dtype(series):
            df[col] = series.map(lambda x: None if pd.isna(x) else str(x)).astype("object")

        elif is_datetime64_any_dtype(series):
            df[col] = pd.to_datetime(series, errors="coerce")

    return df


if run_btn:

    RUN_ID = RunManager.new_run()
    run_path = Path(f"data/{RUN_ID}")

    st.success(f"Run ID: {RUN_ID}")

    # --------------------------------------------------
    # STEP 1 SIGNAL PIPELINE
    # --------------------------------------------------

    with signal_container:

        st.header("Signal Detection")

        with st.spinner("Running signal pipeline..."):

            events = run_signal_pipeline(
                symbol=symbol,
                start=start,
                end=end,
                run_id=RUN_ID
            )

        st.success("Signal pipeline completed")

        if events is not None:
            st.write("Detected anomalies")
            st.dataframe(to_dataframe(events), use_container_width=True)

    # --------------------------------------------------
    # STEP 2 SHOW GENERATED PLOTS
    # --------------------------------------------------

    with plot_container:

        st.header("Signal Analytics")

        plots_path = run_path / "plots"

        if plots_path.exists():

            for plot in plots_path.glob("*.png"):
                st.image(str(plot), caption=plot.name)

    # --------------------------------------------------
    # STEP 3 ECOSYSTEM GRAPH
    # --------------------------------------------------

    with graph_container:

        st.header("Ecosystem Graph")

        with st.spinner("Building ecosystem graph..."):

            ecosystem = EcosystemPipeline(
                "universe/market_universe.parquet",
                run_id=RUN_ID
            )

            nodes, edges = ecosystem.run(symbol)

        graph_file = run_path / "graph_outputs" / "ecosystem_graph.html"

        if graph_file.exists():

            html = graph_file.read_text()

            components.html(
                html,
                height=900
            )

    # --------------------------------------------------
    # STEP 4 MULTISTREAM DATA
    # --------------------------------------------------

    with research_container:

        st.header("Multistream Data")

        with st.spinner("Fetching research data..."):

            run_multistream_researcher(RUN_ID)

        multistream_path = run_path / "multistream"

        if multistream_path.exists():

            for f in multistream_path.glob("*.parquet"):

                st.subheader(f.name)

                df = pd.read_parquet(f)

                st.dataframe(to_dataframe(df.head(100)), use_container_width=True)

    # --------------------------------------------------
    # STEP 5 REASONING
    # --------------------------------------------------

    with reasoning_container:

        st.header("AI Reasoning")

        with st.spinner("Generating reasoning..."):

            reasoning = generate_anomaly_reasoning(run_path)

        st.write(reasoning)
