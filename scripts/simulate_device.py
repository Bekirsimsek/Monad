"""STM32 + DHT22 cihazından geliyormuş gibi backend'e örnek veri gönderir."""
from __future__ import annotations

import argparse
import json
from random import uniform
from time import time
from urllib import request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/ingest")
    parser.add_argument("--device-id", default="stm32-01")
    args = parser.parse_args()

    payload = {
        "device_id": args.device_id,
        "timestamp": int(time()),
        "temperature_c": round(uniform(20, 30), 2),
        "humidity_pct": round(uniform(40, 70), 2),
    }

    data = json.dumps(payload).encode("utf-8")
    req = request.Request(args.url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    with request.urlopen(req, timeout=10) as resp:
        print(resp.status, resp.read().decode("utf-8"))


if __name__ == "__main__":
    main()
