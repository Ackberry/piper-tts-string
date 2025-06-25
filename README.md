# Piper TTS String-to-Speech

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




### Basic Example
```python
from mouth import Mouth
Mouth().speak("Hello, world!")
```


## Usage 
- Make sure mouth.py, test_mouth.py, .onnx voice model and its .json config are in the same directory.
- Install the required dependencies.
- Update test_mouth.py's code with whatever the user want to output. (A current string sentence is already set for tests)
- run test_mouth.py
