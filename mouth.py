import os, sys, tarfile, urllib.request, shutil, glob, subprocess, platform
import tempfile, sounddevice as sd, wave, numpy as np
from scipy import signal

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS with direct audio playback.
    """
    def __init__(self):
        """
        Initializes the Mouth class, ensuring the Piper binary and model files are ready.
        """
        if sys.platform not in ["linux", "linux2"]:
            raise RuntimeError("Linux systems only")
        
        self.piper_path = "piper/piper"
        self._setup_piper()
        self.onnx_file, self.json_file = next(((o, f"{os.path.splitext(o)[0]}.onnx.json" if f"{os.path.splitext(o)[0]}.onnx.json" in j else f"{os.path.splitext(o)[0]}.json") 
            for o in glob.glob("*.onnx") for j in [glob.glob("*.json")] if j), (None, None))
        if not (self.onnx_file and self.json_file):
            raise FileNotFoundError("Missing model files")
        
        # Try to find a working audio device
        try:
            devices = sd.query_devices()
            default_output = sd.query_devices(kind='output')
            self.device = default_output['name']
            print(f"Using audio device: {self.device}")
        except:
            self.device = None
            print("Warning: Could not query audio devices")

    def _setup_piper(self):
        if not (os.path.exists(self.piper_path) and os.access(self.piper_path, os.X_OK)):
            try:
                if os.path.exists("piper"): shutil.rmtree("piper")
                url = f"https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_{'x86_64' if platform.machine()=='x86_64' else 'aarch64'}.tar.gz"
                tar_name = os.path.basename(url)
                urllib.request.urlretrieve(url, tar_name)
                with tarfile.open(tar_name, "r:gz") as tar: tar.extractall()
                if os.path.exists(self.piper_path):
                    os.chmod(self.piper_path, 0o755)
                    os.remove(tar_name)
                    return
            except Exception as e:
                raise RuntimeError(f"Piper setup failed: {e}")
            raise RuntimeError("Piper binary not found after setup")

    def speak(self, text):
        """
        Converts the given text to speech and plays it directly through the speakers.
        """
        if not text.strip(): return
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            try:
                subprocess.run([f"./{self.piper_path}", "--model", self.onnx_file,
                              "--config", self.json_file, "--output_file", temp.name],
                             input=text.encode(), capture_output=True, check=True)
                
                with wave.open(temp.name, 'rb') as wav:
                    audio = np.frombuffer(wav.readframes(wav.getnframes()),
                                        dtype={1: np.int8, 2: np.int16, 4: np.int32}[wav.getsampwidth()])
                    
                    # Convert to float32 in range [-1, 1]
                    audio = audio.astype(np.float32)
                    if wav.getsampwidth() == 1: audio = (audio - 128) / 128.0
                    elif wav.getsampwidth() == 2: audio /= 32768.0
                    elif wav.getsampwidth() == 4: audio /= 2147483648.0
                    
                    # Convert stereo to mono if needed
                    if wav.getnchannels() == 2:
                        audio = audio.reshape(-1, 2).mean(axis=1)

                    # Normalize audio
                    if np.max(np.abs(audio)) > 1.0:
                        audio /= np.max(np.abs(audio))

                    # Try to play with basic settings first
                    try:
                        if self.device:
                            sd.play(audio, wav.getframerate(), device=self.device)
                        else:
                            sd.play(audio, wav.getframerate())
                        sd.wait()
                        return
                    except sd.PortAudioError as e:
                        print(f"Initial playback failed: {e}")

                    # If that fails, try different sample rates with int16 format
                    for rate in [48000, 44100, 22050, 16000]:
                        try:
                            # Resample if needed
                            if rate != wav.getframerate():
                                audio_data = signal.resample(audio, int(len(audio) * rate / wav.getframerate()))
                                if np.max(np.abs(audio_data)) > 1.0:
                                    audio_data /= np.max(np.abs(audio_data))
                            else:
                                audio_data = audio

                            # Convert to int16
                            int16_data = (audio_data * 32767).astype(np.int16)
                            
                            # Try with device if available
                            if self.device:
                                sd.play(int16_data, rate, device=self.device)
                            else:
                                sd.play(int16_data, rate)
                            sd.wait()
                            return
                        except Exception as e:
                            print(f"Failed with rate {rate}: {e}")
                            continue
                    
                    raise RuntimeError("Could not find working audio configuration")
                    
            except Exception as e:
                print(f"Error: {e}")
            finally:
                try: os.unlink(temp.name)
                except: pass

if __name__ == "__main__":
    try:
        Mouth().speak("Hello, world!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 