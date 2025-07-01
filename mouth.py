import os
import tempfile
import subprocess
import sounddevice as sd
import wave
import numpy as np
from scipy import signal
import gc

class Mouth:
    """
    Simplified TTS handler for Raspberry Pi 5 using Piper and direct audio playback.
    """
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.piper_path = "piper/piper"
        self.onnx_file = "en_US-hfc_female-medium.onnx"
        self.json_file = "en_US-hfc_female-medium.onnx.json"
        self._setup_pi_audio()

    def _setup_pi_audio(self):
        # Set ALSA PCM card if not already set
        if 'ALSA_CARDNO' not in os.environ:
            os.environ['ALSA_CARDNO'] = '0'
        if 'PULSE_RUNTIME_PATH' in os.environ:
            del os.environ['PULSE_RUNTIME_PATH']

    def _process_audio(self, audio_data, sample_rate, target_rate=None):
        if target_rate is None or target_rate == sample_rate:
            return audio_data
        return signal.resample(audio_data, int(len(audio_data) * target_rate / sample_rate))

    def speak(self, text):
        if not text.strip():
            return
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            try:
                piper_cmd = [f"./{self.piper_path}", "--model", self.onnx_file,
                             "--config", self.json_file, "--output_file", temp.name]
                process = subprocess.Popen(['nice', '-n', '10'] + piper_cmd,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                process.communicate(input=text.encode())
                with wave.open(temp.name, 'rb') as wavf:
                    audio = np.frombuffer(wavf.readframes(wavf.getnframes()),
                                         dtype={1: np.int8, 2: np.int16, 4: np.int32}[wavf.getsampwidth()])
                    audio = audio.astype(np.float32)
                    if wavf.getsampwidth() == 1:
                        audio = (audio - 128) / 128.0
                    elif wavf.getsampwidth() == 2:
                        audio /= 32768.0
                    elif wavf.getsampwidth() == 4:
                        audio /= 2147483648.0
                    if wavf.getnchannels() == 2:
                        audio = audio.reshape(-1, 2).mean(axis=1)
                    original_rate = wavf.getframerate()
                    self._play_audio(audio, original_rate)
            finally:
                try:
                    os.unlink(temp.name)
                    gc.collect()
                except:
                    pass

    def _play_audio(self, audio, sample_rate):
        pi_rates = [48000, 44100, 22050, 16000]
        for rate in pi_rates:
            try:
                resampled = self._process_audio(audio, sample_rate, rate)
                if np.max(np.abs(resampled)) > 1.0:
                    resampled /= np.max(np.abs(resampled))
                audio_int16 = (resampled * 32767).astype(np.int16)
                sd.play(audio_int16, rate, blocksize=self.chunk_size)
                sd.wait()
                return
            except Exception:
                continue
        # Fallback: try original rate
        try:
            audio_int16 = (audio * 32767).astype(np.int16)
            sd.play(audio_int16, sample_rate, blocksize=self.chunk_size)
            sd.wait()
        except Exception as e:
            print(f"Audio playback failed: {e}")
