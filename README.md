# Piper TTS String-to-Speech

Efficient text-to-speech conversion using Piper TTS with direct audio playback.

## Features
- Direct text-to-speech conversion
- Real-time audio playback
- Automatic format handling
- Minimal disk usage

## Requirements

### System
- Linux (x86_64 or aarch64)
- Python 3.7+
- Working audio device

### Python Packages
```bash
pip install sounddevice numpy scipy
```

### System Libraries
Ubuntu/Debian:
```bash
sudo apt-get install portaudio19-dev
```

Fedora:
```bash
sudo dnf install portaudio-devel
```

### Model Files
Place in working directory:
- ONNX model file (e.g., `en_GB-aru-medium.onnx`)
- JSON config file (e.g., `en_GB-aru-medium.onnx.json`)

Download from [Piper releases](https://github.com/rhasspy/piper/releases)

## Usage

### Basic Example
```python
from mouth import Mouth
Mouth().speak("Hello, world!")
```

### Interactive Mode
```bash
python mouth.py
```
Enter text and press Enter twice to speak.

## Troubleshooting

### Audio Issues

1. **Sample Rate Error**
   ```
   Error: Invalid sample rate
   ```
   - Automatic resolution
   - No action needed

2. **Format Error**
   ```
   Error: Sample format not supported
   ```
   - Automatic conversion
   - No action needed

3. **No Sound**
   ```bash
   # Check audio
   speaker-test -t wav
   
   # Check devices
   aplay -l
   ```

### Installation Issues

1. **PortAudio Error**
   ```
   Error: PortAudio library not found
   ```
   ```bash
   # Ubuntu/Debian
   sudo apt-get install portaudio19-dev
   
   # Fedora
   sudo dnf install portaudio-devel
   ```

2. **Permission Error**
   ```bash
   sudo usermod -a -G audio $USER
   # Log out and back in
   ```

## Resources
- [Piper TTS](https://github.com/rhasspy/piper)
- [Voice Models](https://github.com/rhasspy/piper/releases)
- [PortAudio](http://www.portaudio.com)

## License
[Your License] 