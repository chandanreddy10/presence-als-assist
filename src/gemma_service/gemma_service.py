from fastapi import FastAPI
from pydantic import BaseModel
from ollama import chat
import time
from pathlib import Path

import base64
import numpy as np 
import cv2
import os 

PROMPTS_DIR = Path("prompts")
SAVE_DIR = "frames"
os.makedirs(SAVE_DIR, exist_ok=True)


phrase_prompt = PROMPTS_DIR / "phrase.txt"
sentence_prompt = PROMPTS_DIR / "sentence.txt"

with open(phrase_prompt, "r") as file:
    phrase_prompt = file.read()

with open(sentence_prompt, "r") as file:
    sentence_prompt = file.read()

# gemma4 service to run on a VM supported by GPU.
app = FastAPI()


class LLMRequest(BaseModel):
    text: str
    user_request: str


def run_gemma(prompt: str, request:str, image:str=False):
    
    start = time.time()
    if not image:
        response = chat(
            model="gemma4:e2b", messages=[{"role": "user", "content": prompt}], stream=False
        )

        end = time.time()
        if request == "phrase":
            list_of_words = response.message.content.split(",")
            list_of_words.append("End")
            return {
                "response": list_of_words,
                "latency_ms": round((end - start) * 1000, 2),
            }
        else:
            return {
            "response": response.message.content,
            "latency_ms": round((end - start) * 1000, 2),
        }
    elif image:
        response = chat(
        model="gemma4:e2b",
        messages=[{
            "role": "user",
            "content":f"Output Yes if there is a person in the image",
            "images":[f"{prompt}"]
        }],
        stream=False
        )
        end = time.time()

        return {
            "response": response.message.content,
            "latency_ms": round((end - start) * 1000, 2),
        }

def decode_image_and_save_to_temp(jpg_as_text):
     # 1. decode base64 string
    img_data = base64.b64decode(jpg_as_text)

    # 2. convert to numpy array
    nparr = np.frombuffer(img_data, np.uint8)

    # 3. decode image
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 4. save frame
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"frame_{timestamp}.jpg")

    cv2.imwrite(filename, frame)

    return filename
# route signal decision hints at what the user intends and proceeds as required.
## 2. Sentence generation
## 3. Query
## 4. Fun interaction.


@app.post("/gemma")
def gemma_endpoint(req: LLMRequest):
    text = req.text
    user_request = req.user_request

    if user_request.lower() == "phrase":
        input_to_gemma = f"{phrase_prompt}\nList of Words selected by the patient : {text}"
        return run_gemma(input_to_gemma, user_request.lower())
    
    elif user_request.lower() == "sentence":
        input_to_gemma = f"{sentence_prompt}\n Words to build the sentence from : {text}"
        return run_gemma(input_to_gemma, user_request.lower())
    
    elif user_request.lower() == "story":
        input_to_gemma = f"Build a short story from the Genre 10 lines. Gnere:\n{text}"
        return run_gemma(input_to_gemma, user_request.lower())

    elif user_request.lower() == "image":
        input_to_gemma = decode_image_and_save_to_temp(text)
        # input_to_gemma=text
        return run_gemma(input_to_gemma, user_request.lower(), image=True)

    