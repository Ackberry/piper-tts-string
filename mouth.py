import os, sys, tarfile, urllib.request, shutil, glob, subprocess, platform
import tempfile

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
        
        print(f"Converting text to speech: '{text}'")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            try:
                # Generate speech using piper
                subprocess.run([f"./{self.piper_path}", "--model", self.onnx_file,
                              "--config", self.json_file, "--output_file", temp.name],
                             input=text.encode(), capture_output=True, check=True)
                
                # Try different audio devices in order of preference
                devices = [
                    'plughw:1,0',  # USB Audio device
                    'plughw:0,0',  # HDMI-0
                    'plughw:2,0',  # HDMI-1
                    'default'      # System default
                ]
                
                success = False
                for device in devices:
                    try:
                        print(f"Trying audio device: {device}")
                        subprocess.run(['aplay', '-D', device, temp.name], check=True)
                        success = True
                        break
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to play on {device}: {e}")
                        continue
                
                if not success:
                    print("Failed to play audio on any available device")
                    
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