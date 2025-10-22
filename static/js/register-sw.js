// static/js/register-sw.js
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/service-worker.js')
      .then((reg) => {
        console.log('SW registered', reg);
      })
      .catch((err) => console.error('SW reg failed', err));
  });
}
