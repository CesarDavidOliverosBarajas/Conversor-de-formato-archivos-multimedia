import re
import os
import sys
import subprocess
import shutil
from typing import Optional, Callable
from .base_converter import BaseConverter


def get_ffmpeg_path():
    """Busca ffmpeg: bundle PyInstaller, luego bin/ local, luego PATH del sistema."""
    if hasattr(sys, '_MEIPASS'):
        bundled = os.path.join(sys._MEIPASS, 'ffmpeg')
        if os.name == 'nt':
            bundled += '.exe'
        if os.path.exists(bundled):
            return bundled

    local = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'bin', 'ffmpeg')
    if os.name == 'nt':
        local += '.exe'
    if os.path.exists(local):
        return os.path.normpath(local)

    which = shutil.which('ffmpeg')
    if which:
        return which

    return 'ffmpeg'


class MediaConverter(BaseConverter):
    """
    Controlador para convertir Audio y Video usando FFmpeg nativo a través de Subprocess.
    Lee stderr en tiempo real y parsea el progreso exacto.
    """

    def _get_ffmpeg_command(self):
        """Construye el comando ffmpeg con codecs explícitos para compatibilidad Windows."""
        target_ext = os.path.splitext(self.output_path)[1].lower().replace('.', '')
        is_audio = target_ext in ['mp3', 'wav', 'flac', 'aac', 'ogg']
        video_exts = ['mp4', 'mkv', 'avi', 'mov', 'mts', 'mpeg', 'mpg']

        cmd = [get_ffmpeg_path(), '-y', '-i', self.input_path]

        input_video_exts = ['.mp4', '.mkv', '.avi', '.mov', '.mts', '.mpeg', '.mpg']
        input_is_video = os.path.splitext(self.input_path)[1].lower() in input_video_exts

        if is_audio:
            if input_is_video:
                cmd.append('-vn')
            audio_quality = {
                "Sin pérdida": "320k",
                "Alta": "256k",
                "Media": "128k",
                "Baja": "64k"
            }
            if target_ext == 'mp3':
                cmd.extend(['-c:a', 'libmp3lame'])
            elif target_ext == 'aac':
                cmd.extend(['-c:a', 'aac'])
            elif target_ext == 'ogg':
                cmd.extend(['-c:a', 'libvorbis'])
            if target_ext not in ['wav', 'flac']:
                cmd.extend(['-b:a', audio_quality.get(self.quality, "192k")])
        elif target_ext in video_exts:
            video_quality = {
                "Sin pérdida": "0",
                "Alta": "18",
                "Media": "23",
                "Baja": "28"
            }
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-crf', video_quality.get(self.quality, "23"),
                '-pix_fmt', 'yuv420p'
            ])
        else:
            raise ValueError(f"Formato de salida no soportado: {target_ext}")

        cmd.append(self.output_path)
        return cmd

    def convert(self, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        try:
            ffmpeg_path = get_ffmpeg_path()
            if not os.path.exists(ffmpeg_path) and shutil.which(ffmpeg_path) is None:
                raise FileNotFoundError(
                    f"No se encontró ffmpeg en: {ffmpeg_path}\n"
                    "Descarga ffmpeg para Windows 10 desde:\n"
                    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip\n"
                    "Extrae el .exe en la carpeta bin/ del programa."
                )

            cmd = self._get_ffmpeg_command()

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

            duration_secs = 0.0
            stderr_output = []

            time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            duration_regex = re.compile(r"Duration: (\d+):(\d+):(\d+\.\d+)")

            for line in process.stderr:
                stderr_output.append(line)
                if duration_secs == 0.0:
                    dur_match = duration_regex.search(line)
                    if dur_match:
                        h, m, s = dur_match.groups()
                        duration_secs = int(h) * 3600 + int(m) * 60 + float(s)
                t_match = time_regex.search(line)
                if t_match and duration_secs > 0:
                    h, m, s = t_match.groups()
                    current_secs = int(h) * 3600 + int(m) * 60 + float(s)
                    if progress_callback:
                        prog = int((current_secs / duration_secs) * 100)
                        progress_callback(min(max(prog, 0), 99))

            process.communicate()

            if process.returncode != 0:
                error_details = "".join(stderr_output[-20:])
                raise Exception(
                    f"FFmpeg falló (código {process.returncode}).\n"
                    f"Últimas líneas de error:\n{error_details}"
                )

            if progress_callback:
                progress_callback(100)

            return True

        except FileNotFoundError as e:
            raise Exception(str(e))
        except Exception as e:
            raise Exception(f"Error en conversión multimedia:\n{str(e)}")
