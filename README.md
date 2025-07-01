# Piper TTS for Raspberry Pi 5

Simple text-to-speech system for Raspberry Pi 5 using Piper TTS engine.


### 1. Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev alsa-utils python3-pip
```

### 2. (Recommended) Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install piper-tts
```

### 4. Install Piper TTS Engine
```bash
# Download Piper for Raspberry Pi 5 (AArch64)
wget https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_aarch64.tar.gz

# Extract and setup
tar -xzf piper_linux_aarch64.tar.gz
rm piper_linux_aarch64.tar.gz
chmod +x piper/piper

# Verify installation
./piper/piper --help
```

### Run the Test
```bash
python3 test_mouth.py
```