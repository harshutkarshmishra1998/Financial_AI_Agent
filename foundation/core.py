import uuid
import json
import hashlib
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Type, TypeVar

import pandas as pd
from pydantic import BaseModel, Field

from .config import DATA_ROOT, SCHEMA_VERSION, RUN_DB, SCHEMA_REGISTRY


# =========================================================
# UTILITIES
# =========================================================

def now():
    return datetime.utcnow()

def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()

def data_hash(df: pd.DataFrame) -> str:
    return hashlib.md5(pd.util.hash_pandas_object(df).values).hexdigest() #type: ignore


# =========================================================
# SCHEMA REGISTRY (prevents silent contract drift)
# =========================================================

class SchemaRegistry:

    @staticmethod
    def register(model: Type[BaseModel]):
        schema = model.model_json_schema()
        signature = hashlib.md5(json.dumps(schema, sort_keys=True).encode()).hexdigest()

        registry = {}
        if SCHEMA_REGISTRY.exists():
            registry = json.loads(SCHEMA_REGISTRY.read_text())

        name = model.__name__

        if name in registry and registry[name] != signature:
            raise RuntimeError(f"SCHEMA DRIFT DETECTED for {name}")

        registry[name] = signature
        SCHEMA_REGISTRY.write_text(json.dumps(registry, indent=2))


# =========================================================
# BASE ARTIFACT
# =========================================================

class BaseArtifact(BaseModel):
    run_id: str
    phase: str
    schema_version: str = SCHEMA_VERSION
    created_at: datetime = Field(default_factory=now)

    # lineage
    data_hash: str
    model_name: str
    feature_window: str


# =========================================================
# PHASE 1 ARTIFACT
# =========================================================

class AnomalyEvent(BaseArtifact):

    # market reality timestamp
    event_timestamp: datetime

    symbol: str
    anomaly_score: float
    price_change_pct: float


SchemaRegistry.register(AnomalyEvent)


# =========================================================
# RUN LEDGER (sqlite)
# =========================================================

class RunLedger:

    @staticmethod
    def init():
        conn = sqlite3.connect(RUN_DB)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS runs(
            run_id TEXT PRIMARY KEY,
            created_at TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS phase_runs(
            run_id TEXT,
            phase TEXT,
            duration_sec REAL,
            rows_written INTEGER,
            artifact_hash TEXT,
            timestamp TEXT
        )
        """)

        conn.commit()
        conn.close()

    @staticmethod
    def log_run(run_id: str):
        RunLedger.init()
        conn = sqlite3.connect(RUN_DB)
        conn.execute(
            "INSERT INTO runs VALUES (?,?)",
            (run_id, now().isoformat())
        )
        conn.commit()
        conn.close()

    @staticmethod
    def log_phase(run_id, phase, duration, rows, artifact_hash):
        RunLedger.init()   # ⭐ ENSURE TABLES EXIST
        conn = sqlite3.connect(RUN_DB)
        conn.execute(
            "INSERT INTO phase_runs VALUES (?,?,?,?,?,?)",
            (run_id, phase, duration, rows, artifact_hash, now().isoformat())
        )
        conn.commit()
        conn.close()


RunLedger.init()


# =========================================================
# RUN MANAGER
# =========================================================

class RunManager:

    @staticmethod
    def new_run():
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        (DATA_ROOT / run_id).mkdir(parents=True, exist_ok=True)
        RunLedger.log_run(run_id)
        return run_id


# =========================================================
# STORAGE ENGINE
# =========================================================

T = TypeVar("T", bound=BaseArtifact)

class ArtifactStore:

    @staticmethod
    def _phase_dir(run_id, phase):
        p = DATA_ROOT / run_id / phase
        p.mkdir(parents=True, exist_ok=True)
        return p

    @classmethod
    def write(cls, artifacts: List[T], filename: str):

        if not artifacts:
            raise ValueError("Empty artifact list")

        start = time.time()

        run_id = artifacts[0].run_id
        phase = artifacts[0].phase

        df = pd.DataFrame([a.model_dump() for a in artifacts])
        path = cls._phase_dir(run_id, phase) / f"{filename}.parquet"
        df.to_parquet(path, index=False)

        h = file_hash(path)
        duration = time.time() - start

        RunLedger.log_phase(run_id, phase, duration, len(df), h)

        meta = {
            "rows": len(df),
            "hash": h,
            "duration_sec": duration
        }

        with open(path.with_suffix(".meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

        return path

    @classmethod
    def read(cls, run_id, phase, filename, model: Type[T]) -> List[T]:
        path = DATA_ROOT / run_id / phase / f"{filename}.parquet"
        df = pd.read_parquet(path)
        return [model(**r) for r in df.to_dict("records")] #type: ignore
