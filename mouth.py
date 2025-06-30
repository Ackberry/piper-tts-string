import os, sys, subprocess, platform
import tempfile, sounddevice as sd, wave, numpy as np
from scipy import signal
import gc, psutil, time

class Mouth:
    """
    A class to handle text-to-speech using Piper TTS with direct audio playback.
    Optimized for Raspberry Pi systems.
    """
    def __init__(self, chunk_size=1024, max_memory_mb=100):
        """
        Initializes the Mouth class, ensuring the Piper binary and model files are ready.
        
        Args:
            chunk_size (int): Audio chunk size for processing (smaller for Pi)
            max_memory_mb (int): Maximum memory usage in MB before optimization
        """
        if sys.platform not in ["linux", "linux2"]:
            raise RuntimeError("Linux systems only")
        
        self.chunk_size = chunk_size
        self.max_memory_mb = max_memory_mb
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.piper_path = "piper/piper"
        
        # Pi-specific optimizations
        if self.is_raspberry_pi:
            print("Raspberry Pi detected - applying optimizations")
            self._setup_pi_audio()
        
        self.onnx_file = "en_US-hfc_female-medium.onnx"
        self.json_file = "en_US-hfc_female-medium.onnx.json"

    def _detect_raspberry_pi(self):
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            return 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo
        except:
            return platform.machine().startswith('arm')


    def _setup_pi_audio(self):
        """Setup audio system optimizations for Raspberry Pi"""
        try:
            # Set ALSA PCM card if not already set
            if 'ALSA_CARDNO' not in os.environ:
                os.environ['ALSA_CARDNO'] = '0'
            
            # Disable PulseAudio if causing issues
            if 'PULSE_RUNTIME_PATH' in os.environ:
                del os.environ['PULSE_RUNTIME_PATH']
                
        except Exception as e:
            print(f"Warning: Audio setup issue: {e}")



    def _check_memory_usage(self):
        """Check memory usage and trigger garbage collection if needed"""
        try:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 80:  # If memory usage > 80%
                gc.collect()
                return True
        except:
            pass
        return False

    def _process_audio_efficiently(self, audio_data, sample_rate, target_rate=None):
        """Process audio with memory efficiency for Pi"""
        if target_rate is None:
            target_rate = sample_rate
            
        # Process in chunks to save memory
        if len(audio_data) > self.chunk_size * 10:  # For large audio
            processed_chunks = []
            for i in range(0, len(audio_data), self.chunk_size * 10):
                chunk = audio_data[i:i + self.chunk_size * 10]
                if sample_rate != target_rate:
                    chunk = signal.resample(chunk, int(len(chunk) * target_rate / sample_rate))
                processed_chunks.append(chunk)
                
                # Memory check every few chunks
                if i % (self.chunk_size * 50) == 0:
                    self._check_memory_usage()
                    
            audio_data = np.concatenate(processed_chunks)
        elif sample_rate != target_rate:
            audio_data = signal.resample(audio_data, int(len(audio_data) * target_rate / sample_rate))
            
        return audio_data

    def speak(self, text):
        """
        Converts the given text to speech and plays it directly through the speakers.
        Optimized for Raspberry Pi performance.
        """
        if not text.strip(): return
        
        # Memory check before processing
        self._check_memory_usage()
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp:
            try:
                # Use nice priority for Pi to avoid blocking other processes
                piper_cmd = [f"./{self.piper_path}", "--model", self.onnx_file,
                           "--config", self.json_file, "--output_file", temp.name]
                
                if self.is_raspberry_pi:
                    # Lower process priority on Pi
                    process = subprocess.Popen(['nice', '-n', '10'] + piper_cmd,
                                             stdin=subprocess.PIPE, 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate(input=text.encode())
                    if process.returncode != 0:
                        raise subprocess.CalledProcessError(process.returncode, piper_cmd, stderr)
                else:
                    subprocess.run(piper_cmd, input=text.encode(), 
                                 capture_output=True, check=True)
                
                with wave.open(temp.name, 'rb') as wav:
                    audio = np.frombuffer(wav.readframes(wav.getnframes()),
                                        dtype={1: np.int8, 2: np.int16, 4: np.int32}[wav.getsampwidth()])
                    
                    # Convert to float32 efficiently
                    audio = audio.astype(np.float32)
                    if wav.getsampwidth() == 1: 
                        audio = (audio - 128) / 128.0
                    elif wav.getsampwidth() == 2: 
                        audio /= 32768.0
                    elif wav.getsampwidth() == 4: 
                        audio /= 2147483648.0
                    
                    # Convert stereo to mono if needed
                    if wav.getnchannels() == 2:
                        audio = audio.reshape(-1, 2).mean(axis=1)
                    
                    original_rate = wav.getframerate()
                    
                    # Pi-optimized audio playback
                    if self.is_raspberry_pi:
                        self._play_audio_pi_optimized(audio, original_rate)
                    else:
                        self._play_audio_standard(audio, original_rate)
                        
            except Exception as e:
                print(f"Error: {e}")
            finally:
                try: 
                    os.unlink(temp.name)
                    gc.collect()  # Clean up memory
                except: 
                    pass

    def _play_audio_pi_optimized(self, audio, sample_rate):
        """Optimized audio playback for Raspberry Pi"""
        try:
            # Try common Pi audio rates first
            pi_rates = [48000, 44100, 22050, 16000]
            
            for rate in pi_rates:
                try:
                    if rate != sample_rate:
                        resampled = self._process_audio_efficiently(audio, sample_rate, rate)
                    else:
                        resampled = audio
                    
                    # Normalize and convert to int16 for better Pi compatibility
                    if np.max(np.abs(resampled)) > 1.0: 
                        resampled /= np.max(np.abs(resampled))
                    
                    audio_int16 = (resampled * 32767).astype(np.int16)
                    
                    # Use smaller buffer for Pi
                    sd.play(audio_int16, rate, blocksize=self.chunk_size)
                    sd.wait()
                    return
                    
                except sd.PortAudioError as e:
                    if "Invalid sample rate" not in str(e):
                        continue
                except Exception:
                    continue
                    
            # Fallback: try original rate with different formats
            try:
                audio_int16 = (audio * 32767).astype(np.int16)
                sd.play(audio_int16, sample_rate, blocksize=self.chunk_size)
                sd.wait()
            except Exception as e:
                print(f"Audio playback failed: {e}")
                
        except Exception as e:
            print(f"Pi audio optimization failed: {e}")

    def _play_audio_standard(self, audio, sample_rate):
        """Standard audio playback for non-Pi systems"""
        try:
            sd.play(audio, sample_rate)
            sd.wait()
        except sd.PortAudioError as e:
            if "Invalid sample rate" in str(e):
                for rate in [48000, 44100, 22050, 16000]:
                    try:
                        resampled = signal.resample(audio, int(len(audio) * rate / sample_rate))
                        if np.max(np.abs(resampled)) > 1.0: 
                            resampled /= np.max(np.abs(resampled))
                        sd.play((resampled * 32767).astype(np.int16), rate, blocking=True)
                        break
                    except sd.PortAudioError: 
                        continue
            elif "Sample format not supported" in str(e):
                sd.play((audio * 32767).astype(np.int16), sample_rate, blocking=True)

if __name__ == "__main__":
    try:
        Mouth().speak("Hello, world!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 
