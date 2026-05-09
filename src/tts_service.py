import pyttsx3

def generate_tts_audio(text: str):
    """
    Generates Audio for the given text.
    The script as simple as possible.
    
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()