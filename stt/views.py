import os
import tempfile
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from .inference import transcribe_wav_file
from django.conf import settings

try:
    # If settings specifies a custom ffmpeg binary, expose it for ffmpeg-python
    if getattr(settings, "FFMPEG_BINARY", ""):
        os.environ["FFMPEG_BINARY"] = settings.FFMPEG_BINARY
    import ffmpeg
except Exception:  # pragma: no cover
    ffmpeg = None


def index(_request: HttpRequest) -> HttpResponse:
    return render(_request, "stt/index.html")


def _convert_to_wav(src_path: str, dst_path: str) -> None:
    if ffmpeg is None:
        raise RuntimeError("ffmpeg is required to handle non-wav inputs. Please install ffmpeg and ensure it's on PATH.")
    (
        ffmpeg
        .input(src_path)
        .output(dst_path, ac=1, ar=16000, format="wav")
        .overwrite_output()
        .run(quiet=True)
    )


@api_view(["POST"])  # CSRF exempt via DRF for API usage
def transcribe(request: HttpRequest) -> JsonResponse:
    file_obj = request.FILES.get("audio")
    if not file_obj:
        return JsonResponse({"error": "No audio file uploaded as 'audio'"}, status=400)

    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, file_obj.name)
        with open(src_path, "wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        # If already wav, ensure 16k mono using ffmpeg if available; otherwise, librosa resamples in inference
        ext = os.path.splitext(src_path)[1].lower()
        wav_path = os.path.join(tmpdir, "audio.wav")
        try:
            if ext == ".wav" and ffmpeg is None:
                wav_path = src_path
            else:
                _convert_to_wav(src_path, wav_path)
        except Exception as e:
            return JsonResponse({"error": f"Failed to convert audio: {e}"}, status=400)

        try:
            text = transcribe_wav_file(wav_path)
        except Exception as e:
            return JsonResponse({"error": f"Transcription failed: {e}"}, status=500)

    return JsonResponse({"text": text})

