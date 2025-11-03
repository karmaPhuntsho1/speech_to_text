<<<<<<< HEAD
# speech_to_text
=======
# Dzongkha Speech-to-Text (Django)

Local Django app that records audio in the browser and transcribes to Dzongkha using a local Wav2Vec2 CTC model.

## Quick start

```powershell
cd "C:\Users\karma Phuntsho\OneDrive\Desktop\NLP"
# Use Python 3.11 env (prebuilt wheels for tokenizers)
py -3.11 -m venv .venv311
. .\.venv311\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Model files
Place your trained model in `ASR_xlsr_Model/` (already referenced in `dz_asr/settings.py` as `ASR_MODEL_DIR`). Model files are large; they are ignored by git via `.gitignore`.

## Audio conversion (ffmpeg)
If your browser records WEBM, the server needs ffmpeg to convert to 16kHz mono WAV.
- Install with: `winget install Gyan.FFmpeg` and restart PowerShell, or
- Set an explicit path in `dz_asr/settings.py`:
  ```python
  FFMPEG_BINARY = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
  ```

## Notes
- Use `.venv311` (Python 3.11). The older `.venv` used Python 3.13 and may fail for `tokenizers`.
- Large artifacts and venvs are excluded in `.gitignore`.


>>>>>>> f4848a9 (Initial commit: Dzongkha ASR Django app)
