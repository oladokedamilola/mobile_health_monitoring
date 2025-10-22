// static/js/analytics.js
async function fetchTrends() {
  try {
    const res = await fetch('/api/analytics/trends/', { credentials: 'include' });
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error('Failed to fetch trends', err);
    return [];
  }
}

function renderChart(labels, dataPoints) {
  const ctx = document.getElementById('heartRateChart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Avg Heart Rate (bpm)',
        data: dataPoints,
        tension: 0.35,
        borderColor: '#2D6A4F',
        backgroundColor: 'rgba(45,106,79,0.12)',
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: false }
      }
    }
  });
}

(async function initAnalytics(){
  const raw = await fetchTrends();
  const labels = raw.map(r => new Date(r.created_at).toLocaleString());
  const values = raw.map(r => r.average_heart_rate || null);
  if (labels.length === 0) {
    document.getElementById('heartRateChart').style.minHeight = '120px';
    // show empty state?
  } else {
    renderChart(labels, values);
  }

  // bind generate summary
  const btn = document.getElementById('generateSummary');
  if (btn) {
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      const resp = await fetch('/api/analytics/summary/', { method: 'POST', credentials: 'include' });
      if (resp.ok) location.reload();
      btn.disabled = false;
    });
  }
})();
