import os, sys, glob, subprocess, tempfile, shutil
import numpy as np
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
        
        # Ensure Piper is installed
        self._ensure_piper_installed()
        
        # Now we can import PiperVoice
        from piper import PiperVoice
        
        # Find model files
        self.onnx_file = next((o for o in glob.glob("*.onnx")), None)
        if not self.onnx_file:
            raise FileNotFoundError("No ONNX model file found")
            
        # Load the Piper voice model
        try:
            self.voice = PiperVoice.load(self.onnx_file)
            print(f"Voice loaded: {os.path.basename(self.onnx_file)} | Sample rate: {self.voice.config.sample_rate} Hz")
        except Exception as e:
            raise RuntimeError(f"Failed to load voice model: {e}")

    def _ensure_piper_installed(self):
        """
        Ensures Piper and its dependencies are installed.
        """
        try:
            import piper
            return  # Piper is already installed
        except ImportError:
            print("Installing Piper... Please wait.")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # First install piper-phonemize from PyPI
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "piper-phonemize"],
                        check=True,
                        capture_output=True
                    )
                    
                    # Clone Piper repository
                    subprocess.run(
                        ["git", "clone", "--depth=1", "https://github.com/rhasspy/piper.git"],
                        cwd=temp_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    piper_dir = os.path.join(temp_dir, "piper")
                    
                    # Install Piper from the correct directory
                    piper_python_dir = os.path.join(piper_dir, "src", "python_run")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-e", "."],
                        cwd=piper_python_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    print("Piper installed successfully!")
                    
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f"Failed to install Piper: {e.stderr.decode()}")
                except Exception as e:
                    raise RuntimeError(f"Failed to install Piper: {e}")

    def speak(self, text):
        """
        Converts text to speech and streams it directly to the audio output.
        """
        if not text.strip(): 
            return
        
        print(f"Speaking: '{text}' | Rate: {self.voice.config.sample_rate} Hz")
        
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

            print("✓ Speech completed")

        except Exception as e:
            print(f"✗ Error: {e}")
        finally:
            if 'stream' in locals():
                stream.stop()
                stream.close() 