import pyttsx3
import tempfile
import io
import os

def generate_tts_audio(text: str):
    engine = pyttsx3.init()

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        temp_path = tmp_file.name

    # Save speech to file
    engine.say(text)
    engine.runAndWait()

    # # Read file into memory
    # with open(temp_path, "rb") as f:
    #     audio_bytes = f.read()
    # print(temp_path)
    # return io.BytesIO(audio_bytes)