#!/usr/bin/env python3
"""
Simple test script for the Mouth TTS class.
"""

from piper_tts_script import Mouth

def main():
    """Simple test of the Mouth TTS functionality."""
    try:
        # Initialize the Mouth TTS system
        print("Initializing Mouth TTS system...")
        mouth = Mouth()
        
        # Test with a simple message
        test_text = "Hello, this is a test message from the Mouth TTS system."
        
        print(f"Converting text to speech: '{test_text}'")
        
        # Convert text to speech
        output_file = mouth.speak(test_text, "simple_test.wav")
        
        print(f"Success! Audio saved to: {output_file}")
        print("The script is now working correctly!")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!") 