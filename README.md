# Piper TTS String-to-Speech

A Python-based text-to-speech system that converts text strings directly to speech output using Piper TTS. This project focuses on real-time audio playback without storing audio files.

## Features

- Direct text-to-speech conversion
- Real-time audio playback through system speakers
- No permanent audio files stored
- Support for multiple text lines input
- Automatic Piper binary and model management

## Prerequisites

### System Requirements
- Linux operating system (x86_64 or aarch64 architecture)
- Python 3.7 or higher
- Working audio output device

### Required Python Packages
```bash
pip install sounddevice numpy
```

### Required Files
The following files must be present in your working directory:
- A Piper ONNX model file (e.g., `en_GB-aru-medium.onnx`)
- The corresponding JSON config file (e.g., `en_GB-aru-medium.onnx.json`)

You can download voice models from the [official Piper repository](https://github.com/rhasspy/piper/releases).

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd <repo-directory>
```

2. Install required Python packages:
```bash
pip install sounddevice numpy
```

3. Place your ONNX model and JSON config files in the project directory.

## Usage

1. Run the script:
```bash
python mouth1.py
```

2. Enter the text you want to convert to speech:
   - Type your text (can be multiple lines)
   - Press Enter twice (double Enter) to finish input
   - The text will be converted to speech and played immediately

Example:
```bash
$ python mouth1.py

Enter the text to convert to speech.
Press Enter twice (double Enter) to finish.
Hello, this is a test of the text-to-speech system.
[Press Enter]
[Press Enter]
```

## How It Works

1. **Initialization**:
   - Checks for Linux environment
   - Downloads and sets up Piper binary if not present
   - Detects ONNX model and config files

2. **Text Processing**:
   - Accepts multi-line text input
   - Processes text when double Enter is detected

3. **Speech Generation**:
   - Uses Piper TTS for speech synthesis
   - Creates temporary WAV file
   - Plays audio through system speakers
   - Automatically cleans up temporary files

## Project Structure

- `mouth1.py`: Main script for text-to-speech conversion
- `*.onnx`: Piper voice model file
- `*.json`: Model configuration file
- `piper/`: Directory containing Piper binary and dependencies (auto-downloaded)

## Troubleshooting

1. **"No such file or directory" Error**:
   - Ensure the ONNX model and JSON files are in the same directory as the script
   - Check if the Piper binary was downloaded successfully

2. **Audio Playback Issues**:
   - Verify your system's audio output is working
   - Check if sounddevice is installed correctly
   - Ensure you have proper permissions for audio output

3. **"Linux systems only" Error**:
   - This script is designed for Linux systems only
   - Check if you're running on a supported Linux distribution

## License

[Your License Information]

## Acknowledgments

- [Piper TTS](https://github.com/rhasspy/piper) for the text-to-speech engine
- The developers of sounddevice and numpy 