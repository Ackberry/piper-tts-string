import os, sys, tarfile, urllib.request, shutil, glob, subprocess, platform
import tempfile

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS with direct audio playback using ALSA.
    """
    def __init__(self):
        """
        Initializes the Mouth class, ensuring the Piper binary and model files are ready.
        """
        if sys.platform not in ["linux", "linux2"]:
            raise RuntimeError("Linux systems only")
        self.piper_path = "piper/piper"
        self._setup_piper()
        self.onnx_file, self.json_file = self._find_model_files()
        if not (self.onnx_file and self.json_file):
            raise FileNotFoundError("Missing model files (.onnx and .json)")
        print(f"[INFO] Model: {os.path.basename(self.onnx_file)} | Config: {os.path.basename(self.json_file)}")

    def _find_model_files(self):
        """
        Finds the ONNX model and its corresponding JSON config file.s
        """
        for onnx in glob.glob("*.onnx"):
            base = os.path.splitext(onnx)[0]
            for json_name in [f"{base}.onnx.json", f"{base}.json"]:
                if os.path.exists(json_name):
                    return onnx, json_name
        return None, None

    def _setup_piper(self):
        """
        Ensures the Piper binary is present and executable, downloads if needed.
        """
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
                    print("[INFO] Piper binary setup complete.")
                    return
            except Exception as e:
                raise RuntimeError(f"Piper setup failed: {e}")
            raise RuntimeError("Piper binary not found after setup")

    def _play_audio(self, wav_path, sample_rate=22050):
        """
        Tries to play the WAV file on available ALSA devices, in order of preference.
        """
        devices = [
            'plughw:1,0',  # USB Audio device
            'plughw:0,0',  # HDMI-0
            'plughw:2,0',  # HDMI-1
            'default'      # System default
        ]
        for device in devices:
            try:
                print(f"[INFO] Playing on device: {device} | Sample rate: {sample_rate} Hz")
                subprocess.run(['aplay', '-D', device, wav_path], check=True, capture_output=True)
                print("[INFO] ✓ Playback successful.")
                return True
            except subprocess.CalledProcessError as e:
                print(f"[WARN] Failed on {device}: {e}")
        print("[ERROR] Failed to play audio on any available device.")
        return False

    def speak(self, text):
        """
        Converts the given text to speech and plays it directly through the speakers using ALSA.
        """
        if not text.strip():
            print("[WARN] No text provided for TTS.")
            return
        print(f"[INFO] Speaking: '{text}'")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            try:
                # Generate speech using Piper
                subprocess.run([
                    f"./{self.piper_path}", "--model", self.onnx_file,
                    "--config", self.json_file, "--output_file", temp.name
                ], input=text.encode(), capture_output=True, check=True)
                self._play_audio(temp.name)
            except Exception as e:
                print(f"[ERROR] TTS or playback failed: {e}")
            finally:
                try:
                    os.unlink(temp.name)
                except Exception:
                    pass 