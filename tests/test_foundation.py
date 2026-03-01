from foundation import RunManager, ArtifactStore, AnomalyEvent, data_hash, now
import pandas as pd
from pathlib import Path
import shutil


from pathlib import Path
import shutil

def clear_directory(folder_path: str | Path):
    folder = Path(folder_path)

    if not folder.exists():
        print(f"Directory not found → {folder}")
        return

    for item in folder.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print(f"Cleared everything inside → {folder}")


def mock_anomaly_batch(run_id: str):
    df = pd.DataFrame({
        "symbol": ["RELIANCE.NS", "TCS.NS"],
        "price": [2500, 3800]
    })

    d_hash = data_hash(df)

    return [
        AnomalyEvent(
            run_id=run_id,
            phase="signal",
            symbol=row.symbol, #type: ignore
            anomaly_score=0.9,
            price_change_pct=5,
            event_timestamp=now(),
            data_hash=d_hash,
            model_name="isolation_forest_v1",
            feature_window="30d"
        )
        for row in df.itertuples(index=False)
    ]


def test_foundation():

    run_id = RunManager.new_run()

    batch = mock_anomaly_batch(run_id)

    path = ArtifactStore.write(batch, "anomalies")

    loaded = ArtifactStore.read(run_id, "signal", "anomalies", AnomalyEvent)

    assert len(loaded) == len(batch)
    assert loaded[0].model_name == "isolation_forest_v1"
    assert loaded[0].data_hash is not None

    print("FOUNDATION FULL TEST PASSED")


if __name__ == "__main__":
    clear_directory("data")
    test_foundation()