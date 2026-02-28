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

## GitHub'da neden görünmüyor?

Genelde sebep kodun sadece lokal branch'te commitli kalmasıdır. Aşağıdaki adımları çalıştır:

```bash
git status
git branch --show-current
git remote -v
git push -u origin <branch-adi>
```

Eğer GitHub'da PR açılmadıysa, branch push edildikten sonra web arayüzünden Compare & Pull Request ile açabilirsin.

## Donanım olmadan test (STM32 + DHT22 bağlı değilken)

Evet, donanım olmadan da test edebilirsin:

1. Unit testler:

```bash
python3 -m unittest backend/test_core.py
python3 -m unittest backend/test_api.py
```

2. API'yi ayağa kaldırıp simülatörle sahte sensör verisi gönder:

```bash
uvicorn backend.app:app --reload
python3 scripts/simulate_device.py --url http://127.0.0.1:8000/ingest --device-id stm32-01
```

Bu şekilde tüm ingest + hash + batch akışını gerçek sensör olmadan doğrulamış olursun.
