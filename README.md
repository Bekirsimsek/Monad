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


## Adım adım test rehberi

Aşağıdaki akışla sistemi **STM32 bağlamadan** ve istersen sonra **STM32 + DHT22 ile** test edebilirsin.

### 1) Projeyi hazırla

```bash
git status
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Beklenen: dependency kurulumundan sonra hata almamalısın.

### 2) Unit testleri çalıştır

```bash
python3 -m unittest backend/test_core.py
python3 -m unittest backend/test_api.py
```

Beklenen: testlerin `OK` dönmesi.

### 3) API'yi ayağa kaldır

```bash
uvicorn backend.app:app --reload
```

Yeni terminal açıp sağlık kontrolü:

```bash
curl http://127.0.0.1:8000/health
```

Beklenen çıktı:

```json
{"status":"ok"}
```

### 4) Donanım olmadan sahte veri gönder (simülatör)

```bash
python3 scripts/simulate_device.py --url http://127.0.0.1:8000/ingest --device-id stm32-01
```

Beklenen: `200` status ve JSON içinde `payload_hash`.

### 5) Batch hash üretimini test et

```bash
curl -X POST http://127.0.0.1:8000/anchor-batch   -H 'content-type: application/json'   -d '{"start_ts":0,"end_ts":9999999999}'
```

Beklenen: `record_count` ve 64 karakterlik `batch_hash` dönmeli.

Opsiyonel kontrol:

```bash
cat backend/anchor_log.txt
```

Beklenen: `start_ts,end_ts,adet,hash` formatında satır.

### 6) Duplicate kontrol testi

Aynı payload'ı iki kez gönderirsen ikinci istek `409 duplicate payload` dönmeli.

```bash
curl -X POST http://127.0.0.1:8000/ingest   -H 'content-type: application/json'   -d '{"device_id":"stm32-01","timestamp":1730000001,"temperature_c":24.3,"humidity_pct":55.1}'
```

Komutu tekrar çalıştır ve ikinci yanıtta 409 bekle.

### 7) (Opsiyonel) STM32 + DHT22 ile gerçek cihaz testi

1. STM32 firmware tarafında payload'ı `firmware/payload_schema.json` formatında üret.
2. Backend'e HTTP POST `/ingest` gönder.
3. 5-10 dakika veri topla.
4. `/anchor-batch` çağırıp hash üret.
5. Üretilen hash'i `contracts/SensorBatchAnchor.sol` içindeki `anchorBatch` fonksiyonuna Monad testnet'te gönder.

### 8) Sorun giderme kısa notları

- `ModuleNotFoundError`: Sanal ortam aktif değil veya dependency kurulmamış.
- `Connection refused`: `uvicorn` çalışmıyor.
- `404 range içinde kayıt bulunamadı`: Verilen zaman aralığında kayıt yok.
- GitHub'da görünmeme: commit sonrası branch'i push et (`git push -u origin <branch-adi>`).
