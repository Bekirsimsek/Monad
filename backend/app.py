from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.core import SensorRecord, payload_hash_hex, validate_record

DB_PATH = Path(__file__).resolve().parent / "sensor_data.db"
ANCHOR_LOG = Path(__file__).resolve().parent / "anchor_log.txt"

app = FastAPI(title="Monad IoT MVP", version="0.1.0")


class SensorIn(BaseModel):
    device_id: str = Field(..., min_length=1)
    timestamp: int
    temperature_c: float
    humidity_pct: float


class BatchAnchorRequest(BaseModel):
    start_ts: int
    end_ts: int


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                temperature_c REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                payload_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
def ingest(data: SensorIn) -> dict[str, str | int]:
    record = SensorRecord(**data.model_dump())
    try:
        validate_record(record)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    p_hash = payload_hash_hex(record)
    created = datetime.now(tz=timezone.utc).isoformat()

    try:
        with _db() as conn:
            cur = conn.execute(
                """
                INSERT INTO sensor_readings (
                    device_id, timestamp, temperature_c, humidity_pct, payload_hash, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.device_id,
                    record.timestamp,
                    record.temperature_c,
                    record.humidity_pct,
                    p_hash,
                    created,
                ),
            )
            conn.commit()
            row_id = cur.lastrowid
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="duplicate payload") from exc

    return {"id": row_id, "payload_hash": p_hash}


@app.post("/anchor-batch")
def anchor_batch(req: BatchAnchorRequest) -> dict[str, str | int]:
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT payload_hash FROM sensor_readings
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC, id ASC
            """,
            (req.start_ts, req.end_ts),
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="range içinde kayıt bulunamadı")

    joined = "".join(row["payload_hash"] for row in rows)
    from hashlib import sha256

    batch_hash = sha256(joined.encode("utf-8")).hexdigest()
    line = f"{req.start_ts},{req.end_ts},{len(rows)},{batch_hash}\n"
    ANCHOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    ANCHOR_LOG.write_text(
        ANCHOR_LOG.read_text() + line if ANCHOR_LOG.exists() else line,
        encoding="utf-8",
    )

    return {
        "record_count": len(rows),
        "batch_hash": batch_hash,
        "note": "MVP: bu hash Monad testnet'e yazılacak veri olarak hazırlandı",
    }
