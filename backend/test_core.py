import unittest

from backend.core import SensorRecord, canonical_payload, payload_hash_hex, validate_record


class CoreTests(unittest.TestCase):
    def test_validate_record_ok(self):
        validate_record(SensorRecord("stm32-01", 1730000000, 24.5, 58.1))

    def test_validate_record_bad_humidity(self):
        with self.assertRaises(ValueError):
            validate_record(SensorRecord("stm32-01", 1730000000, 24.5, 120.0))

    def test_canonical_payload_deterministic(self):
        rec = SensorRecord("stm32-01", 1730000000, 24.567, 58.123)
        payload = canonical_payload(rec)
        self.assertEqual(
            payload,
            '{"device_id":"stm32-01","humidity_pct":58.12,"temperature_c":24.57,"timestamp":1730000000}',
        )
        self.assertEqual(len(payload_hash_hex(rec)), 64)


if __name__ == "__main__":
    unittest.main()
