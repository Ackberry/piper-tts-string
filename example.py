
from mouth import Mouth

def main():
    try:
        tts = Mouth()
        text = "Hello there! This is a test of the text to speech system."
        print(f"Converting text to speech: '{text}'")
        tts.speak(text)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 