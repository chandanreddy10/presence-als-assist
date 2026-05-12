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
            "content": "Output Yes if there is a person in the image.",
            "images": [prompt]   # 👈 IMPORTANT PART
        }],
        stream=False
        )
        end = time.time()

        return {
            "response": response.message.content,
            "latency_ms": round((end - start) * 1000, 2),
        }

@app.post("/gemma")
def gemma_endpoint(req: LLMRequest):
    text = req.text
    user_request = req.user_request
    # print(text)
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
        input_to_gemma = text 
        return run_gemma(input_to_gemma, user_request.lower())

    