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
            print("Installing Piper and dependencies... This may take a few minutes...")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Clone Piper repository
                    subprocess.run(
                        ["git", "clone", "--depth=1", "https://github.com/rhasspy/piper.git"],
                        cwd=temp_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    piper_dir = os.path.join(temp_dir, "piper")
                    
                    # First install piper-phonemize
                    phonemize_dir = os.path.join(piper_dir, "src", "python_phonemize")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-e", "."],
                        cwd=phonemize_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    # Then install Piper
                    piper_python_dir = os.path.join(piper_dir, "src", "python")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "-e", "."],
                        cwd=piper_python_dir,
                        check=True,
                        capture_output=True
                    )
                    
                    print("Piper installation completed successfully!")
                    
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