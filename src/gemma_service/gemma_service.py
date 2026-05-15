from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from ollama import chat
import time
from pathlib import Path

import base64
import numpy as np
import cv2
import os


app = FastAPI()

PROMPTS_DIR = Path("prompts")
SAVE_DIR = "frames"
os.makedirs(SAVE_DIR, exist_ok=True)

# Load prompts
def load_prompt(file_name: str, base_dir: Path) -> str:
    with open(base_dir / file_name, "r") as f:
        return f.read()

phrase_prompt = load_prompt("phrase.txt", PROMPTS_DIR)
sentence_prompt = load_prompt("sentence.txt", PROMPTS_DIR)
guided_qa_prompt = load_prompt("guided_QA.txt", PROMPTS_DIR)
safety_people_count_prompt = load_prompt("unsafe_num_people.txt", PROMPTS_DIR)
position_prompt = load_prompt("position_prompt.txt", PROMPTS_DIR)
breathing_prompt = load_prompt("breathing_prompt.txt", PROMPTS_DIR)
medication_prompt = load_prompt("medication_prompt.txt", PROMPTS_DIR)
summary_prompt = load_prompt("summary_prompt.txt", PROMPTS_DIR)

class LLMRequest(BaseModel):
    text: str
    user_request: Optional[str] = None
    image_for_intent: Optional[str] = None


def decode_image_and_save_to_temp(image_base64: str) -> str:
    img_data = base64.b64decode(image_base64)
    nparr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(SAVE_DIR, f"frame_{timestamp}.jpg")

    cv2.imwrite(filename, frame)
    return filename


def build_prompt(user_request: str, text: str) -> str:

    if user_request == "phrase":
        return f"{phrase_prompt}\nList of Words: {text}"

    elif user_request == "sentence":
        return f"{sentence_prompt}\nWords: {text}"

    elif user_request == "story":
        return f"Write a short 10-line story.\nGenre: {text}"

    elif user_request == "image":
        return f"{safety_people_count_prompt}"

    elif user_request == "pain":
        return f"{guided_qa_prompt}\n{text}"

    elif user_request == "pain_end":
        return f"Summarize the text\n{text}"
    
    elif user_request == "position":
        return f"{position_prompt}"
    
    elif user_request == "breathing":
        return f"{breathing_prompt}"
    
    elif user_request == "medication":
        return f"{medication_prompt}"
    
    elif user_request == "summary":
        return f"{summary_prompt} Logs: {text}"
    
    else:
        return text

def run_gemma(prompt: str, request: str, image_base64: Optional[str] = None):

    start = time.time()

    try:

        # IMAGE PATH
        if image_base64:
            image_path = decode_image_and_save_to_temp(image_base64)

            response = chat(
                model="gemma4:e2b",
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [image_path]
                }],
                stream=False
            )

        # TEXT ONLY
        else:
            response = chat(
                model="gemma4:e2b",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                stream=False
            )

        output = response.message.content

        # special handling for phrase mode
        if request == "phrase":
            output = output.split(",") + ["End"]

        return {
            "response": output,
            "latency_ms": round((time.time() - start) * 1000, 2)
        }

    except Exception as e:
        return {
            "error": str(e),
            "latency_ms": round((time.time() - start) * 1000, 2)
        }

@app.post("/gemma")
def gemma_endpoint(req: LLMRequest):

    text = req.text
    user_request = (req.user_request or "").lower()
    image = req.image_for_intent

    prompt = build_prompt(user_request, text)

    return run_gemma(
        prompt=prompt,
        request=user_request,
        image_base64=image
    )