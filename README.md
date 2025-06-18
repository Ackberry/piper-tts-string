# piper-tts-string

# Mouth TTS - Text-to-Speech with Piper

A Python wrapper for the Piper TTS engine that provides a simple `Mouth` class for text-to-speech conversion.

## Features

- **Cross-platform support**: Automatically detects your operating system and downloads the appropriate Piper binary
- **Easy to use**: Simple class-based interface with a `speak()` method
- **Automatic model detection**: Automatically finds and pairs .onnx and .json model files
- **Flexible output**: Specify custom output file names

## Requirements

- Python 3.6+
- Internet connection (for initial binary download)
- .onnx and .json model files (Piper voice models)

## Installation

1. Place your Piper model files (.onnx and .json) in the same directory as the script
2. Run the script - it will automatically download the appropriate Piper binary for your system

## Usage

### Basic Usage

```python
from piper_tts_script import Mouth

# Initialize the TTS system
mouth = Mouth()

# Convert text to speech
output_file = mouth.speak("Hello, world!")
print(f"Audio saved to: {output_file}")
```

### Advanced Usage

```python
from piper_tts_script import Mouth

# Initialize with custom model directory
mouth = Mouth(model_dir="./models")

# Convert text to speech with custom output file
output_file = mouth.speak(
    "This is a custom message.", 
    output_file="my_audio.wav"
)
```

### Command Line Usage

Run the script directly for interactive text input:

```bash
python piper_tts_script.py
```

## Class Reference

### Mouth Class

#### `__init__(model_dir=".")`
Initialize the Mouth TTS system.

**Parameters:**
- `model_dir` (str): Directory containing .onnx and .json model files (default: current directory)

#### `speak(text, output_file="output.wav")`
Convert text to speech and save as a WAV file.

**Parameters:**
- `text` (str): The text to convert to speech
- `output_file` (str): Output WAV file path (default: "output.wav")

**Returns:**
- `str`: Path to the generated WAV file

**Raises:**
- `ValueError`: If input text is empty
- `RuntimeError`: If Piper fails to process the text

## Supported Platforms

- **Windows**: x86_64, ARM64
- **Linux**: x86_64, ARM64
- **macOS**: x86_64, ARM64

## Model Files

The script automatically detects and pairs .onnx and .json files in the model directory. Make sure you have:

1. A `.onnx` file (the voice model)
2. A corresponding `.json` file (the model configuration)

The files should have matching base names (e.g., `en_US-john-medium.onnx` and `en_US-john-medium.onnx.json`).

## Error Handling

The script includes comprehensive error handling for:
- Missing model files
- Network connectivity issues
- Unsupported platforms
- Piper execution errors

## Example

```python
from piper_tts_script import Mouth

try:
    # Initialize TTS system
    mouth = Mouth()
    
    # Convert text to speech
    text = "Welcome to the Rare Lab! This is Blossom speaking."
    output_file = mouth.speak(text, "welcome_message.wav")
    
    print(f"Successfully created: {output_file}")
    
except Exception as e:
    print(f"Error: {e}")
```

## Testing

Run the test script to verify everything is working:

```bash
python test_mouth.py
```

This will create a test audio file using the sample text.