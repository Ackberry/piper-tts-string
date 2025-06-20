<<<<<<< HEAD
import os
import sys
import tarfile
import urllib.request
import shutil
import glob
import subprocess
import platform

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS (Linux only).
    """
    def __init__(self):
        """
        Initializes the Mouth class, ensuring the Piper binary and model files are ready.
        """
        # Check if running on Linux
        if sys.platform not in ["linux", "linux2"]:
            raise RuntimeError("This script is designed for Linux systems only.")
        
        self.piper_binary_path = self._get_piper_binary_path()
        if not self._ensure_piper_binary():
            raise RuntimeError("Failed to set up Piper TTS binary.")
        
        self.onnx_file, self.json_file = self._detect_model_files()
        if not self.onnx_file or not self.json_file:
            raise FileNotFoundError("Could not find required .onnx and .json model files in the current directory.")

    def _get_piper_binary_path(self):
        """Returns the expected path to the piper binary."""
        return "piper/piper"

    def _get_piper_download_url(self):
        """
        Determines the correct Piper TTS binary download URL based on system architecture.
        """
        machine = platform.machine()

        if machine == "x86_64":
            arch = "x86_64"
        elif machine == "aarch64":
            arch = "aarch64"
        else:
            raise RuntimeError(f"Unsupported Linux architecture: {machine}. Only x86_64 and aarch64 are supported.")
        
        piper_version = "2023.11.14-2"
        piper_tar_name = f"piper_linux_{arch}.tar.gz"
        return f"https://github.com/rhasspy/piper/releases/download/{piper_version}/{piper_tar_name}"

    def _ensure_piper_binary(self):
        """
        Ensures the Piper binary is downloaded, extracted, and executable.
        """
        if os.path.exists(self.piper_binary_path) and os.access(self.piper_binary_path, os.X_OK):
            print(f"Piper binary '{self.piper_binary_path}' already exists and is executable.")
            return True

        print("Piper binary not found or not executable. Downloading...")
        
        piper_tar_url = self._get_piper_download_url()
        piper_tar_name = os.path.basename(piper_tar_url)
        
        try:
            # Clean up previous incomplete installations
            if os.path.exists("piper"):
                shutil.rmtree("piper")

            print(f"Downloading from {piper_tar_url}...")
            urllib.request.urlretrieve(piper_tar_url, piper_tar_name)
            print("Download complete. Extracting...")

            with tarfile.open(piper_tar_name, "r:gz") as tar:
                tar.extractall()

            if os.path.exists(self.piper_binary_path):
                os.chmod(self.piper_binary_path, 0o755)
                print("Piper binary is ready.")
            else:
                print(f"Error: Piper binary not found at '{self.piper_binary_path}' after extraction.")
                return False

            os.remove(piper_tar_name)
            return True

        except Exception as e:
            print(f"Failed to download or extract Piper: {e}")
            return False
            
    def _detect_model_files(self):
        """
        Detects the ONNX model and JSON config files in the current directory.
        """
        onnx_files = glob.glob("*.onnx")
        json_files = glob.glob("*.json")

        if not onnx_files:
            print("Error: No .onnx model file found in the folder.")
            return None, None
        if not json_files:
            print("Error: No .json config file found in the folder.")
            return None, None

        # Try to match .onnx and .json files by their base name
        for onnx in onnx_files:
            base = os.path.splitext(onnx)[0]
            # Look for exact match first
            if f"{base}.onnx.json" in json_files:
                js = f"{base}.onnx.json"
                print(f"Using model: {onnx}")
                print(f"Using config: {js}")
                return onnx, js
            # Also check for just the base name with .json
            elif f"{base}.json" in json_files:
                js = f"{base}.json"
                print(f"Using model: {onnx}")
                print(f"Using config: {js}")
                return onnx, js
        
        # Fallback to using the first found files if no direct match is found
        print(f"Warning: No matching model/config pair found. Using first available files.")
        print(f"Using model: {onnx_files[0]}")
        print(f"Using config: {json_files[0]}")
        return onnx_files[0], json_files[0]

    def speak(self, text: str, output_file: str = "output.wav"):
        """
        Converts the given text to speech and saves it to a WAV file.
        """
        if not text.strip():
            print("Input text is empty. Nothing to synthesize.")
            return

        command = [
            f"./{self.piper_binary_path}",
            "--model", self.onnx_file,
            "--config", self.json_file,
            "--output_file", output_file
        ]

        print(f"Running Piper TTS: {' '.join(command)}")
        try:
            # Use subprocess.run to execute the piper command, passing the text via stdin
            process = subprocess.run(command, input=text.encode("utf-8"), capture_output=True, check=True)
            print(f"Success! Speech saved to {output_file}")
            if process.stdout:
                print(f"Piper output (stdout):\n{process.stdout.decode('utf-8')}")

        except subprocess.CalledProcessError as e:
            print(f"Piper failed with return code {e.returncode}.")
            print(f"Stderr:\n{e.stderr.decode('utf-8')}")
            print(f"Stdout:\n{e.stdout.decode('utf-8')}")
        except Exception as e:
            print(f"An unexpected error occurred while running Piper: {e}")

if __name__ == "__main__":
    try:
        mouth = Mouth()
        
        print("\nEnter the text to convert to speech.")
        print("You can enter multiple lines. Press Ctrl+D to finish.")
        
        input_lines = sys.stdin.readlines()
        
        if not input_lines:
            print("No input provided. Exiting.")
            sys.exit(0)
            
        text_to_speak = "".join(input_lines).strip()
        
        if text_to_speak:
            mouth.speak(text_to_speak)
        else:
            print("Input was empty after stripping whitespace. Nothing to do.")

    except (RuntimeError, FileNotFoundError) as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
=======
import os
import sys
import tarfile
import urllib.request
import shutil
import glob
import subprocess
import platform

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS.
    """
    def __init__(self):
        """
        Initializes the Mouth class, ensuring the Piper binary and model files are ready.
        """
        self.piper_binary_path = self._get_piper_binary_path()
        if not self._ensure_piper_binary():
            raise RuntimeError("Failed to set up Piper TTS binary.")
        
        self.onnx_file, self.json_file = self._detect_model_files()
        if not self.onnx_file or not self.json_file:
            raise FileNotFoundError("Could not find required .onnx and .json model files in the current directory.")

    def _get_piper_binary_path(self):
        """Returns the expected path to the piper binary."""
        return "piper/piper"

    def _get_piper_download_url(self):
        """
        Determines the correct Piper TTS binary download URL based on system architecture.
        This script is intended for Linux.
        """
        if sys.platform not in ["linux", "linux2"]:
            print(f"Warning: This script is intended for Linux, but you are on {sys.platform}.")
            print("Defaulting to download for x86_64 architecture, which may not be correct for your target system.")
            machine = 'x86_64'
        else:
            machine = platform.machine()

        if machine == "x86_64":
            arch = "x86_64"
        elif machine == "aarch64":
            arch = "aarch64"
        else:
            raise RuntimeError(f"Unsupported Linux architecture: {machine}. Only x86_64 and aarch64 are supported.")
        
        piper_version = "2023.11.14-2"
        piper_tar_name = f"piper_linux_{arch}.tar.gz"
        return f"https://github.com/rhasspy/piper/releases/download/{piper_version}/{piper_tar_name}"

    def _ensure_piper_binary(self):
        """
        Ensures the Piper binary is downloaded, extracted, and executable.
        """
        if os.path.exists(self.piper_binary_path) and os.access(self.piper_binary_path, os.X_OK):
            print(f"Piper binary '{self.piper_binary_path}' already exists and is executable.")
            return True

        print("Piper binary not found or not executable. Downloading...")
        
        piper_tar_url = self._get_piper_download_url()
        piper_tar_name = os.path.basename(piper_tar_url)
        
        try:
            # Clean up previous incomplete installations
            if os.path.exists("piper"):
                shutil.rmtree("piper")

            print(f"Downloading from {piper_tar_url}...")
            urllib.request.urlretrieve(piper_tar_url, piper_tar_name)
            print("Download complete. Extracting...")

            with tarfile.open(piper_tar_name, "r:gz") as tar:
                tar.extractall()

            if os.path.exists(self.piper_binary_path):
                os.chmod(self.piper_binary_path, 0o755)
                print("Piper binary is ready.")
            else:
                print(f"Error: Piper binary not found at '{self.piper_binary_path}' after extraction.")
                return False

            os.remove(piper_tar_name)
            return True

        except Exception as e:
            print(f"Failed to download or extract Piper: {e}")
            return False
            
    def _detect_model_files(self):
        """
        Detects the ONNX model and JSON config files in the current directory.
        """
        onnx_files = glob.glob("*.onnx")
        json_files = glob.glob("*.json")

        if not onnx_files:
            print("Error: No .onnx model file found in the folder.")
            return None, None
        if not json_files:
            print("Error: No .json config file found in the folder.")
            return None, None

        # Try to match .onnx and .json files by their base name
        for onnx in onnx_files:
            base = os.path.splitext(onnx)[0]
            if f"{base}.onnx.json" in json_files:
                js = f"{base}.onnx.json"
                print(f"Using model: {onnx}")
                print(f"Using config: {js}")
                return onnx, js
        
        # Fallback to using the first found files if no direct match is found
        print(f"Warning: No matching model/config pair found. Using first available files.")
        print(f"Using model: {onnx_files[0]}")
        print(f"Using config: {json_files[0]}")
        return onnx_files[0], json_files[0]

    def speak(self, text: str, output_file: str = "output.wav"):
        """
        Converts the given text to speech and saves it to a WAV file.
        """
        if not text.strip():
            print("Input text is empty. Nothing to synthesize.")
            return

        command = [
            f"./{self.piper_binary_path}",
            "--model", self.onnx_file,
            "--config", self.json_file,
            "--output_file", output_file
        ]

        print(f"Running Piper TTS: {' '.join(command)}")
        try:
            # Use subprocess.run to execute the piper command, passing the text via stdin
            process = subprocess.run(command, input=text.encode("utf-8"), capture_output=True, check=True)
            print(f"Success! Speech saved to {output_file}")
            if process.stdout:
                print(f"Piper output (stdout):\n{process.stdout.decode('utf-8')}")

        except subprocess.CalledProcessError as e:
            print(f"Piper failed with return code {e.returncode}.")
            print(f"Stderr:\n{e.stderr.decode('utf-8')}")
            print(f"Stdout:\n{e.stdout.decode('utf-8')}")
        except Exception as e:
            print(f"An unexpected error occurred while running Piper: {e}")

if __name__ == "__main__":
    try:
        mouth = Mouth()
        
        print("\nEnter the text to convert to speech.")
        print("You can enter multiple lines. Press Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows) to finish.")
        
        input_lines = sys.stdin.readlines()
        
        if not input_lines:
            print("No input provided. Exiting.")
            sys.exit(0)
            
        text_to_speak = "".join(input_lines).strip()
        
        if text_to_speak:
            mouth.speak(text_to_speak)
        else:
            print("Input was empty after stripping whitespace. Nothing to do.")

    except (RuntimeError, FileNotFoundError) as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
>>>>>>> 2953ed757ea86f94ce97b2bb96d4be75472efa09
        sys.exit(1) 