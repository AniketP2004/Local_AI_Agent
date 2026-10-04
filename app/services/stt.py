import os
import tempfile
import threading
import whisper

_model = None
_lock = threading.Lock()


def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = whisper.load_model("base")
    return _model


def transcribe(audio_bytes: bytes) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".webm", delete=False)
    try:
        tmp.write(audio_bytes)
        tmp.close()  # release lock before ffmpeg touches it
        result = get_model().transcribe(tmp.name, language="en", fp16=False)
        return result["text"].strip()
    finally:
        os.unlink(tmp.name)