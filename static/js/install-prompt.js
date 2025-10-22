// static/js/install-prompt.js
let deferredPrompt;
const installPromptEl = document.getElementById('installPrompt');
const btnInstall = document.getElementById('btnInstall');

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  if (installPromptEl) installPromptEl.style.display = 'flex';
});

if (btnInstall) {
  btnInstall.addEventListener('click', async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      if (installPromptEl) installPromptEl.style.display = 'none';
    }
    deferredPrompt = null;
  });
}
