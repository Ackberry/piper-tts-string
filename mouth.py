import os
import sys
import tarfile
import urllib.request
import shutil
import glob
import subprocess
import platform
import tempfile
import sounddevice as sd
import wave
import numpy as np

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS with direct audio playback.
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

    def speak(self, text: str):
        """
        Converts the given text to speech and plays it directly through the speakers.
        """
        if not text.strip():
            print("Input text is empty. Nothing to synthesize.")
            return

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_path = temp_wav.name

        try:
            # Generate speech to temporary file
            command = [
                f"./{self.piper_binary_path}",
                "--model", self.onnx_file,
                "--config", self.json_file,
                "--output_file", temp_path
            ]

            print(f"Running Piper TTS: {' '.join(command)}")
            process = subprocess.run(command, input=text.encode("utf-8"), capture_output=True, check=True)
            
            # Read and play the temporary WAV file
            with wave.open(temp_path, 'rb') as wav_file:
                # Get WAV file parameters
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                
                # Read all frames
                frames = wav_file.readframes(n_frames)
                
                # Convert bytes to numpy array
                dtype_map = {1: np.int8, 2: np.int16, 4: np.int32}
                audio_data = np.frombuffer(frames, dtype=dtype_map[sample_width])
                
                # Play audio with error handling for sample rate issues
                print("Playing audio...")
                try:
                    # Try playing with original framerate
                    sd.play(audio_data, framerate)
                    sd.wait()
                except sd.PortAudioError as e:
                    if "Invalid sample rate" in str(e):
                        print("Sample rate issue detected. Trying with default sample rate...")
                        # Try with a standard sample rate
                        standard_rates = [44100, 48000, 22050, 16000]
                        for rate in standard_rates:
                            try:
                                sd.play(audio_data, rate)
                                sd.wait()
                                print(f"Successfully played audio at {rate}Hz")
                                break
                            except sd.PortAudioError:
                                continue
                        else:
                            print("Failed to play audio with any standard sample rate.")
                    else:
                        raise
                print("Audio playback complete.")

        except subprocess.CalledProcessError as e:
            print(f"Piper failed with return code {e.returncode}.")
            print(f"Stderr:\n{e.stderr.decode('utf-8')}")
            print(f"Stdout:\n{e.stdout.decode('utf-8')}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except:
                pass

if __name__ == "__main__":
    try:
        mouth = Mouth()
        
        print("\nEnter the text to convert to speech.")
        print("Press Enter twice (double Enter) to finish.")
        
        input_lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = input()
                if line.strip() == "":
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                    input_lines.append(line)
            except EOFError:
                break
        
        if not input_lines:
            print("No input provided. Exiting.")
            sys.exit(0)
            
        text_to_speak = "\n".join(input_lines).strip()
        
        if text_to_speak:
            mouth.speak(text_to_speak)
        else:
            print("Input was empty after stripping whitespace. Nothing to do.")

    except (RuntimeError, FileNotFoundError) as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1) 
