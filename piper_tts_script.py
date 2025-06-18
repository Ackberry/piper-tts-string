import os
import sys
import tarfile
import urllib.request
import shutil
import glob
import subprocess
import platform
import zipfile

class Mouth:
    def __init__(self, model_dir="."):
        """
        Initialize the Mouth TTS system.
        
        Args:
            model_dir (str): Directory containing .onnx and .json model files
        """
        self.model_dir = model_dir
        self.piper_binary_path = None
        self.onnx_file = None
        self.json_file = None
        self._setup_piper()
        self._detect_model_files()
    
    def _get_piper_url(self):
        """Get the appropriate Piper binary URL based on the operating system."""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        if system == "windows":
            if "x86_64" in machine or "amd64" in machine:
                return "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
            elif "arm64" in machine or "aarch64" in machine:
                return "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_arm64.zip"
        elif system == "linux":
            if "x86_64" in machine or "amd64" in machine:
                return "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_amd64.tar.gz"
            elif "arm64" in machine or "aarch64" in machine:
                return "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz"
        elif system == "darwin":  # macOS
            if "x86_64" in machine or "amd64" in machine:
                return "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_macos_amd64.tar.gz"
            elif "arm64" in machine or "aarch64" in machine:
                return "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_macos_arm64.tar.gz"
        
        raise RuntimeError(f"Unsupported platform: {system} {machine}")
    
    def _setup_piper(self):
        """Download and setup the Piper binary."""
        system = platform.system().lower()
        
        # Determine binary name and path
        if system == "windows":
            self.piper_binary_path = "piper/piper.exe"
        else:
            self.piper_binary_path = "piper/piper"
        
        # Check if binary already exists and is executable
        if os.path.exists(self.piper_binary_path):
            if system != "windows" and not os.access(self.piper_binary_path, os.X_OK):
                os.chmod(self.piper_binary_path, 0o755)
            print(f"Piper binary '{self.piper_binary_path}' already exists.")
            return
        
        print("Piper binary not found. Downloading...")
        try:
            # Remove existing piper directory if it exists but is incomplete
            if os.path.exists("piper"):
                shutil.rmtree("piper")
            
            url = self._get_piper_url()
            archive_name = url.split("/")[-1]
            
            print(f"Downloading from: {url}")
            urllib.request.urlretrieve(url, archive_name)
            print("Download complete. Extracting...")
            
            # Extract based on file type
            if archive_name.endswith('.zip'):
                with zipfile.ZipFile(archive_name, 'r') as zip_ref:
                    zip_ref.extractall()
            else:
                with tarfile.open(archive_name, "r:gz") as tar:
                    tar.extractall()
            
            # Make the binary executable on Unix-like systems
            if system != "windows" and os.path.exists(self.piper_binary_path):
                os.chmod(self.piper_binary_path, 0o755)
            
            if os.path.exists(self.piper_binary_path):
                print("Piper binary is ready.")
            else:
                raise RuntimeError("Piper binary not found after extraction.")
            
            # Clean up the downloaded archive
            os.remove(archive_name)
            
        except Exception as e:
            print(f"Failed to download or extract Piper: {e}")
            raise
    
    def _detect_model_files(self):
        """Detect .onnx and .json model files in the model directory."""
        # Change to model directory for file detection
        original_dir = os.getcwd()
        os.chdir(self.model_dir)
        
        try:
            onnx_files = glob.glob("*.onnx")
            json_files = glob.glob("*.json")
            
            if not onnx_files:
                raise RuntimeError("No .onnx model file found in the model directory.")
            if not json_files:
                raise RuntimeError("No .json config file found in the model directory.")
            
            # Try to match .onnx and .json by base name
            for onnx in onnx_files:
                base = os.path.splitext(onnx)[0]
                for js in json_files:
                    if os.path.splitext(js)[0] == base:
                        self.onnx_file = onnx
                        self.json_file = js
                        print(f"Using model: {onnx}")
                        print(f"Using config: {js}")
                        return
            
            # Fallback: just use the first of each
            self.onnx_file = onnx_files[0]
            self.json_file = json_files[0]
            print(f"Warning: No matching .onnx/.json pair found. Using {onnx_files[0]} and {json_files[0]}")
            
        finally:
            # Return to original directory
            os.chdir(original_dir)
    
    def speak(self, text, output_file="output.wav"):
        """
        Convert text to speech and save as a WAV file.
        
        Args:
            text (str): The text to convert to speech
            output_file (str): Output WAV file path (default: "output.wav")
        
        Returns:
            str: Path to the generated WAV file
        """
        if not text.strip():
            raise ValueError("Input text is empty.")
        
        # Ensure we're in the right directory for the binary
        original_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            cmd = [
                self.piper_binary_path,
                "--model", os.path.join(self.model_dir, self.onnx_file),
                "--config", os.path.join(self.model_dir, self.json_file),
                "--output_file", output_file
            ]
            
            print(f"Running Piper: {' '.join(cmd)}")
            proc = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
            
            if proc.returncode != 0:
                error_msg = proc.stderr.decode('utf-8') if proc.stderr else "Unknown error"
                raise RuntimeError(f"Piper failed with error: {error_msg}")
            
            print(f"Success! Output written to {output_file}")
            return output_file
            
        finally:
            # Return to original directory
            os.chdir(original_dir)

def main():
    """Main function for command-line usage."""
    try:
        # Initialize the Mouth TTS system
        mouth = Mouth()
        
        # Get text input from user
        print("\nEnter the text you want to convert to speech (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        text = "\n".join(lines[:-1])  # Remove the last empty line
        
        # Convert text to speech
        output_file = mouth.speak(text)
        print(f"Audio saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 