import os
import sounddevice as sd
import numpy as np
import gc
from piper.voice import PiperVoice

class Mouth:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.voicedir = "./"
        self.model = self.voicedir + "en_US-hfc_female-medium.onnx"
        self.voice = PiperVoice.load(self.model)
        self.sample_rate = self.voice.config.sample_rate
        self._setup_pi_audio()

    def _setup_pi_audio(self):
        if 'ALSA_CARDNO' not in os.environ:
            os.environ['ALSA_CARDNO'] = '0'
        if 'PULSE_RUNTIME_PATH' in os.environ:
            del os.environ['PULSE_RUNTIME_PATH']

    def speak(self, text):
        if not text.strip():
            return
        
        audio_chunks = []
        for audio_bytes in self.voice.synthesize_stream_raw(text):
            int_data = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_chunks.append(int_data)
        if not audio_chunks:
            return
        audio = np.concatenate(audio_chunks)
        # Normalize to float32 in [-1, 1]
        audio = audio.astype(np.float32) / 32768.0
        # Ensure mono
        if len(audio.shape) > 1 and audio.shape[1] == 2:
            audio = audio.mean(axis=1)
        self._play_audio(audio, self.sample_rate)
        gc.collect()

    def _play_audio(self, audio, sample_rate):
        try:
            if np.max(np.abs(audio)) > 1.0:
                audio = audio / np.max(np.abs(audio))
            audio_int16 = (audio * 32767).astype(np.int16)
            sd.play(audio_int16, sample_rate, blocksize=self.chunk_size)
            sd.wait()
        except Exception as e:
            print(f"Audio playback failed: {e}")
