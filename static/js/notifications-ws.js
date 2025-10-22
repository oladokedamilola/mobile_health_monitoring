// static/js/notifications-ws.js
(function(){
  const container = document.getElementById('notifications-container');
  // Use wss on HTTPS or ws on http; adapt if you use a specific path
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const wsUrl = `${protocol}://${window.location.host}/ws/notifications/`;

  let socket;
  try {
    socket = new WebSocket(wsUrl);
  } catch (err) {
    console.warn('WS init failed', err);
    return;
  }

  socket.onmessage = function(e){
    try {
      const payload = JSON.parse(e.data);
      showToast(payload);
    } catch (err) {
      console.error('Invalid WS payload',err);
    }
  };

  function showToast(data){
    const el = document.createElement('div');
    el.className = 'toast-notif';
    el.innerHTML = `<div style="font-weight:700;margin-bottom:4px">${data.title || 'Notification'}</div><div style="font-size:.95rem">${data.message || ''}</div>`;
    container.prepend(el);
    setTimeout(()=> {
      el.style.opacity = '0';
      setTimeout(()=> el.remove(), 350);
    }, 6000);
  }
})();
