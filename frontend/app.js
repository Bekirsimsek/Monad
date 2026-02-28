const backendUrlInput = document.getElementById('backendUrl');
const saved = localStorage.getItem('backendUrl');
if (saved) backendUrlInput.value = saved;

const now = Math.floor(Date.now() / 1000);
document.querySelector('input[name="timestamp"]').value = now;

function getBaseUrl() {
  return backendUrlInput.value.replace(/\/$/, '');
}

async function callApi(path, payload) {
  const res = await fetch(`${getBaseUrl()}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(JSON.stringify(data));
  return data;
}

document.getElementById('saveUrl').onclick = () => {
  localStorage.setItem('backendUrl', backendUrlInput.value);
  alert('Backend URL kaydedildi');
};

document.getElementById('ingestForm').onsubmit = async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {
    device_id: String(fd.get('device_id')),
    timestamp: Number(fd.get('timestamp')),
    temperature_c: Number(fd.get('temperature_c')),
    humidity_pct: Number(fd.get('humidity_pct')),
  };
  const out = document.getElementById('ingestResult');
  out.textContent = 'Gönderiliyor...';
  try {
    const result = await callApi('/ingest', payload);
    out.textContent = JSON.stringify(result, null, 2);
    await loadReadings();
  } catch (err) {
    out.textContent = `Hata: ${err.message}`;
  }
};

document.getElementById('anchorForm').onsubmit = async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {
    start_ts: Number(fd.get('start_ts')),
    end_ts: Number(fd.get('end_ts')),
  };
  const out = document.getElementById('anchorResult');
  out.textContent = 'Hesaplanıyor...';
  try {
    const result = await callApi('/anchor-batch', payload);
    out.textContent = JSON.stringify(result, null, 2);
  } catch (err) {
    out.textContent = `Hata: ${err.message}`;
  }
};

async function loadReadings() {
  const tbody = document.getElementById('readingsBody');
  tbody.innerHTML = '<tr><td colspan="6">Yükleniyor...</td></tr>';
  try {
    const res = await fetch(`${getBaseUrl()}/readings?limit=10`);
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data));
    const rows = data.items || [];
    if (!rows.length) {
      tbody.innerHTML = '<tr><td colspan="6">Kayıt bulunamadı</td></tr>';
      return;
    }
    tbody.innerHTML = rows
      .map(
        (r) => `<tr>
          <td>${r.id}</td>
          <td>${r.device_id}</td>
          <td>${r.timestamp}</td>
          <td>${r.temperature_c}</td>
          <td>${r.humidity_pct}</td>
          <td title="${r.payload_hash}">${r.payload_hash.slice(0, 12)}...</td>
        </tr>`
      )
      .join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">Hata: ${err.message}</td></tr>`;
  }
}

document.getElementById('refreshReadings').onclick = loadReadings;
loadReadings();
