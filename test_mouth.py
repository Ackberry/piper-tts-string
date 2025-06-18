#!/usr/bin/env python3
"""
Test script for the Mouth TTS class.
This demonstrates how to use the Mouth class to convert text to speech.
"""

from piper_tts_script import Mouth

def test_mouth():
    """Test the Mouth TTS functionality."""
    try:
        # Initialize the Mouth TTS system
        print("Initializing Mouth TTS system...")
        mouth = Mouth()
        
        # Test text
        test_text = "Hi! This is Blossom, and you are at the Rare lab."
        
        print(f"Converting text to speech: '{test_text}'")
        
        # Convert text to speech
        output_file = mouth.speak(test_text, "test_output.wav")
        
        print(f"Success! Audio saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_mouth()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!") 