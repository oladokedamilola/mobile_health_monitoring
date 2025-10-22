// static/js/sensors/placeholder-sensors.js
document.getElementById('activate-sensors')?.addEventListener('click', async () => {
  const status = document.getElementById('sensor-status');
  try {
    // Camera permission (for PPG)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      await navigator.mediaDevices.getUserMedia({ video: true });
    }
    // Microphone
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      await navigator.mediaDevices.getUserMedia({ audio: true });
    }
    // DeviceMotion (may require permission on iOS)
    if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {
      const p = await DeviceMotionEvent.requestPermission();
      if (p !== 'granted') console.warn('DeviceMotion permission not granted');
    }
    status.textContent = 'Sensors: Active (permissions granted)';
  } catch (err) {
    console.error('Sensor activation error', err);
    status.textContent = 'Sensors: Permission denied or not supported';
  }
});
