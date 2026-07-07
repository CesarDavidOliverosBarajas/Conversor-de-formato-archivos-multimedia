import io
import json
import os
import sys
import wave
import zipfile
import subprocess
import tempfile
from typing import Optional, Callable

from .media_converter import get_ffmpeg_path

VOSK_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
VOSK_MODEL_DIR = "vosk-model-small-es-0.42"


def get_bin_dir():
    return os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bin')
    )


def get_vosk_model_path():
    if hasattr(sys, '_MEIPASS'):
        bundled = os.path.join(sys._MEIPASS, VOSK_MODEL_DIR)
        if os.path.isdir(bundled):
            return bundled

    local_dir = get_bin_dir()
    if os.path.isdir(local_dir):
        for entry in sorted(os.listdir(local_dir)):
            full = os.path.join(local_dir, entry)
            if os.path.isdir(full) and entry.startswith('vosk-model'):
                return os.path.normpath(full)

    return None


class Transcriber:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.model_path = get_vosk_model_path()

    def _download_model(self, progress_callback: Optional[Callable[[int], None]] = None):
        import requests

        bin_dir = get_bin_dir()
        os.makedirs(bin_dir, exist_ok=True)

        zip_path = os.path.join(bin_dir, VOSK_MODEL_DIR + ".zip")

        resp = requests.get(VOSK_MODEL_URL, stream=True)
        resp.raise_for_status()

        total = int(resp.headers.get('content-length', 0))
        downloaded = 0

        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total > 0:
                    prog = int((downloaded / total) * 50)
                    progress_callback(min(prog, 50))

        if progress_callback:
            progress_callback(50)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(bin_dir)

        os.unlink(zip_path)

        self.model_path = get_vosk_model_path()

    def _ensure_wav(self) -> str:
        ext = os.path.splitext(self.input_path)[1].lower()
        wav_exts = ['.wav']
        vid_exts = ['.mp4', '.mkv', '.avi', '.mov', '.mts', '.mpeg', '.mpg']

        if ext in wav_exts:
            return self.input_path

        ffmpeg = get_ffmpeg_path()
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        tmp.close()

        cmd = [
            ffmpeg, '-y', '-i', self.input_path,
            '-vn',
            '-ar', '16000',
            '-ac', '1',
            '-c:a', 'pcm_s16le',
            tmp.name
        ]

        startup_info = None
        if os.name == 'nt':
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        process = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
            startupinfo=startup_info
        )
        process.communicate()

        if process.returncode != 0:
            os.unlink(tmp.name)
            raise Exception("No se pudo convertir el audio a WAV (16kHz, mono) para transcripción.")

        return tmp.name

    def transcribe(self, progress_callback: Optional[Callable[[int], None]] = None) -> str:
        if self.model_path is None:
            self._download_model(progress_callback)

        from vosk import Model, KaldiRecognizer

        model = Model(self.model_path)

        wav_path = self._ensure_wav()

        try:
            wf = wave.open(wav_path, "rb")

            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                wf.close()
                raise Exception("El audio debe ser mono, 16-bit, 16kHz WAV.")

            rec = KaldiRecognizer(model, 16000)
            rec.SetWords(True)

            total_frames = wf.getnframes()
            frames_processed = 0

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)
                frames_processed += 4000
                if progress_callback:
                    prog = int((frames_processed / total_frames) * 100)
                    progress_callback(min(prog, 99))

            result = json.loads(rec.FinalResult())
            text = result.get("text", "")

            wf.close()

            if progress_callback:
                progress_callback(100)

            return text

        finally:
            if wav_path != self.input_path and os.path.exists(wav_path):
                os.unlink(wav_path)

    @staticmethod
    def save_txt(text: str, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    @staticmethod
    def save_docx(text: str, output_path: str):
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "La librería python-docx no está instalada.\n"
                "Ejecuta: pip install python-docx"
            )

        doc = Document()
        for paragraph in text.split('\n'):
            doc.add_paragraph(paragraph)
        doc.save(output_path)
