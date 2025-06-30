# Piper TTS for Raspberry Pi 5

Simple text-to-speech system for Raspberry Pi 5 using Piper TTS engine.

## What it does

- **mouth.py**: Contains the `Mouth` class that converts text to speech and plays it directly through Pi 5 speakers
- **test_mouth.py**: Simple test script that imports `Mouth` class and speaks a test sentence

## Setup for Raspberry Pi 5

### 1. Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev alsa-utils python3-pip
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Piper TTS Engine
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

### 4. Download Voice Model
```bash
# Download US English female voice model for Pi 5
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/hfc_female/medium/en_US-hfc_female-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/hfc_female/medium/en_US-hfc_female-medium.onnx.json
```

## How to Use



### Run the Test
```bash
python3 test_mouth.py
```

This will output: `Converting to speech: 'Hello there! This is a test of the text to speech system.'` and play the audio.


## Audio Setup on Pi 5

```bash
# Test audio output
aplay /usr/share/sounds/alsa/Front_Left.wav

# Configure audio output (choose 3.5mm jack or HDMI)
sudo raspi-config
# Navigate to: Advanced Options > Audio
```

s