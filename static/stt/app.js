const recordBtn = document.getElementById('recordBtn');
const out = document.getElementById('output');
const clearBtn = document.getElementById('clearBtn');
const copyBtn = document.getElementById('copyBtn');

let mediaRecorder = null;
let chunks = [];
let isRecording = false;

async function start() {
  if (!navigator.mediaDevices?.getUserMedia) {
    alert('getUserMedia not supported in this browser');
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  // Prefer WAV if supported (avoids server-side ffmpeg), else fall back to WEBM
  const preferredTypes = [
    'audio/wav;codecs=pcm',
    'audio/wav',
    'audio/webm;codecs=opus',
    'audio/webm'
  ];
  const chosenType = preferredTypes.find(type => MediaRecorder.isTypeSupported?.(type));
  mediaRecorder = new MediaRecorder(stream, chosenType ? { mimeType: chosenType } : undefined);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) chunks.push(e.data); };
  mediaRecorder.onstop = async () => {
    const mime = mediaRecorder.mimeType || 'audio/webm';
    const ext = mime.includes('wav') ? 'wav' : 'webm';
    const blob = new Blob(chunks, { type: mime });
    const form = new FormData();
    form.append('audio', blob, `recording.${ext}`);
    recordBtn.disabled = true; recordBtn.textContent = 'Transcribing…';
    try {
      const resp = await fetch('/api/transcribe/', { method: 'POST', body: form });
      const data = await resp.json();
      if (data.text) out.value += (out.value ? '\n' : '') + data.text;
      else alert(data.error || 'Unknown error');
    } catch (e) { alert('Request failed: ' + e.message); }
    finally { recordBtn.disabled = false; recordBtn.textContent = '🎤 Tap to Record'; }
  };
  mediaRecorder.start();
}

recordBtn.addEventListener('click', async () => {
  if (!isRecording) {
    await start();
    isRecording = true;
    recordBtn.textContent = '⏹️ Stop';
  } else {
    mediaRecorder?.stop();
    isRecording = false;
  }
});

clearBtn.addEventListener('click', () => out.value = '');
copyBtn.addEventListener('click', async () => { await navigator.clipboard.writeText(out.value || ''); });

