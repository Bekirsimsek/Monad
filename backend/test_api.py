import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import backend.app as app_module


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        app_module.DB_PATH = Path(self.tmp_dir.name) / "sensor_data.db"
        app_module.ANCHOR_LOG = Path(self.tmp_dir.name) / "anchor_log.txt"
        app_module.init_db()
        self.client = TestClient(app_module.app)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_ingest_and_anchor_batch(self):
        ingest = self.client.post(
            "/ingest",
            json={
                "device_id": "stm32-01",
                "timestamp": 1730000001,
                "temperature_c": 24.3,
                "humidity_pct": 55.1,
            },
        )
        self.assertEqual(ingest.status_code, 200)
        self.assertIn("payload_hash", ingest.json())

        anchor = self.client.post(
            "/anchor-batch", json={"start_ts": 1730000000, "end_ts": 1730000010}
        )
        self.assertEqual(anchor.status_code, 200)
        body = anchor.json()
        self.assertEqual(body["record_count"], 1)
        self.assertEqual(len(body["batch_hash"]), 64)

    def test_invalid_payload_rejected(self):
        response = self.client.post(
            "/ingest",
            json={
                "device_id": "stm32-01",
                "timestamp": 1730000001,
                "temperature_c": 24.3,
                "humidity_pct": 155.1,
            },
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
