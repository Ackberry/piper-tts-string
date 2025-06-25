import os, sys, glob
import numpy as np
from piper.voice import PiperVoice
import sounddevice as sd

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS with direct streaming audio output.
    """
    def __init__(self):
        """
        Initializes the Mouth class, loading the Piper voice model.
        """
        if sys.platform not in ["linux", "linux2"]:
            raise RuntimeError("Linux systems only")
        
        # Find model files
        self.onnx_file = next((o for o in glob.glob("*.onnx")), None)
        if not self.onnx_file:
            raise FileNotFoundError("No ONNX model file found")
            
        # Load the Piper voice model
        try:
            self.voice = PiperVoice.load(self.onnx_file)
        except Exception as e:
            raise RuntimeError(f"Failed to load voice model: {e}")

    def speak(self, text):
        """
        Converts text to speech and streams it directly to the audio output.
        """
        if not text.strip(): 
            return
        
        try:
            # Create audio output stream
            stream = sd.OutputStream(
                samplerate=self.voice.config.sample_rate,
                channels=1,
                dtype='int16'
            )
            stream.start()

            # Stream the synthesized audio directly
            for audio_bytes in self.voice.synthesize_stream_raw(text):
                audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
                stream.write(audio_data)

        except Exception as e:
            print(f"Error during speech synthesis: {e}")
        finally:
            if 'stream' in locals():
                stream.stop()
                stream.close()

if __name__ == "__main__":
    try:
        Mouth().speak("Hello, world!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 