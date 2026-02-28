# Monad IoT MVP (STM32 + DHT22)

Bu MVP, STM32 üzerinden okunan DHT22 sıcaklık/nem verisini önce veritabanına yazıp ardından batch hash olarak Monad testnet'e anchor etmeyi hedefler.

## Mimari

1. **Cihaz katmanı (STM32 + DHT22)**
   - Ölçüm üretir.
   - JSON payload gönderir.
2. **Backend API (FastAPI)**
   - `/ingest`: veriyi doğrular, SQLite'a kaydeder.
   - `/anchor-batch`: belirli zaman aralığındaki kayıtların hash zincirini hesaplar.
3. **On-chain katman (Solidity sözleşmesi)**
   - `contracts/SensorBatchAnchor.sol` ile batch hash saklanır.

> MVP'de `/anchor-batch` yalnızca `backend/anchor_log.txt` dosyasına yazıyor. Sonraki adımda bu hash'i direkt Monad testnet'e gönderen bir worker eklenmeli.

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```

## Örnek veri gönderimi

```bash
python3 scripts/simulate_device.py --url http://127.0.0.1:8000/ingest --device-id stm32-01
```

## Batch hash üretimi

```bash
curl -X POST http://127.0.0.1:8000/anchor-batch \
  -H 'content-type: application/json' \
  -d '{"start_ts":1730000000,"end_ts":1739999999}'
```

## Sonraki geliştirmeler

- MQTT desteği (cihazdan backend'e)
- Mesaj imzası (ECDSA/HMAC) ve replay koruması
- Postgres/TimescaleDB'ye geçiş
- Monad testnet'e gerçek transaction gönderen worker
- Grafana dashboard
