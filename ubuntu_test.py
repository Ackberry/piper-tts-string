#!/usr/bin/env python3
"""
Ubuntu/Linux test script for the Mouth TTS class.
This script is specifically designed to test the TTS functionality on Ubuntu systems.
"""

import platform
from piper_tts_script import Mouth

def test_ubuntu_compatibility():
    """Test the Mouth TTS functionality on Ubuntu."""
    try:
        # Check system information
        system = platform.system()
        machine = platform.machine()
        print(f"Detected system: {system}")
        print(f"Machine architecture: {machine}")
        
        if system.lower() != "linux":
            print("Warning: This script is designed for Ubuntu/Linux systems.")
        
        # Initialize the Mouth TTS system
        print("\nInitializing Mouth TTS system...")
        mouth = Mouth()
        
        # Test with Ubuntu-specific text
        test_text = "Welcome to Ubuntu! This is a test of the text-to-speech system."
        
        print(f"Converting text to speech: '{test_text}'")
        
        # Convert text to speech
        output_file = mouth.speak(test_text, "ubuntu_test.wav")
        
        print(f"Success! Audio saved to: {output_file}")
        print("The Mouth TTS system is working correctly on Ubuntu!")
        
        # Display system-specific information
        print(f"\nSystem details:")
        print(f"- OS: {platform.system()} {platform.release()}")
        print(f"- Architecture: {platform.machine()}")
        print(f"- Python: {platform.python_version()}")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Ubuntu/Linux Mouth TTS Test ===")
    success = test_ubuntu_compatibility()
    if success:
        print("\n✅ Test completed successfully!")
        print("The Mouth TTS system is ready for use on Ubuntu.")
    else:
        print("\n❌ Test failed!")
        print("Please check the error messages above.") 