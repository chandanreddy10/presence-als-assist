import pyttsx3

def generate_tts_audio(text: str, voice="default"):
    """
    Generates Audio for the given text.
    The script as simple as possible.
    
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voice == "default":
        engine.say(text)
        engine.runAndWait()
    else:
        engine.setProperty('voice', voices[1].id)
        engine.say(text)
        engine.runAndWait()