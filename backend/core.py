"""Core logic for IoT sensor ingestion MVP."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class SensorRecord:
    device_id: str
    timestamp: int
    temperature_c: float
    humidity_pct: float


def validate_record(record: SensorRecord) -> None:
    """Raise ValueError when sensor data appears invalid."""
    if not record.device_id.strip():
        raise ValueError("device_id boş olamaz")
    if record.temperature_c < -40 or record.temperature_c > 80:
        raise ValueError("temperature_c DHT22 aralığı dışında")
    if record.humidity_pct < 0 or record.humidity_pct > 100:
        raise ValueError("humidity_pct 0-100 aralığında olmalı")


def canonical_payload(record: SensorRecord) -> str:
    """Create deterministic payload representation for hashing/signing."""
    payload = {
        "device_id": record.device_id,
        "humidity_pct": round(record.humidity_pct, 2),
        "temperature_c": round(record.temperature_c, 2),
        "timestamp": record.timestamp,
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def payload_hash_hex(record: SensorRecord) -> str:
    """Generate SHA-256 hash of canonical payload."""
    return sha256(canonical_payload(record).encode("utf-8")).hexdigest()
