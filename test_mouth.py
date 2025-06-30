#!/usr/bin/env python3
"""
Simple test for Mouth TTS class - convert text to speech
"""

from mouth import Mouth

def test_basic_speech():
    """Test basic text-to-speech functionality"""
    try:
        # Initialize TTS engine
        tts = Mouth()
        
        # Test with a simple string
        test_text = "Hello there! This is a test of the text to speech system."
        tts.speak(test_text)
        
    except Exception as e:
        print(f" Speech test failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_speech() 