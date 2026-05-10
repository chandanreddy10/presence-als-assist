from fastapi import FastAPI
from pydantic import BaseModel
from ollama import chat
import time
from pathlib import Path

PROMPTS_DIR = Path("prompts")

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


def run_gemma_phrase(prompt: str):
    start = time.time()

    response = chat(
        model="gemma4:e2b", messages=[{"role": "user", "content": prompt}], stream=False
    )

    end = time.time()
    list_of_words = response.message.content.split(",")
    list_of_words.append("End")
    return {
        "response": list_of_words,
        "latency_ms": round((end - start) * 1000, 2),
    }

def run_gemma_sentence(prompt: str):
    start = time.time()

    response = chat(
        model="gemma4:e2b", messages=[{"role": "user", "content": prompt}], stream=False
    )

    end = time.time()

    return {
        "response": response.message.content,
        "latency_ms": round((end - start) * 1000, 2),
    }

# route signal decision hints at what the user intends and proceeds as required.
## 2. Sentence generation
## 3. Query
## 4. Fun interaction.


@app.post("/gemma")
def gemma_endpoint(req: LLMRequest):
    text = req.text
    user_request = req.user_request
    print(text)
    if user_request.lower() == "phrase":
        input_to_gemma = f"{phrase_prompt}\nList of Words selected by the patient : {text}"
        return run_gemma_phrase(input_to_gemma)
    
    elif user_request.lower() == "sentence":
        input_to_gemma = f"{sentence_prompt}\n Words to build the sentence from : {text}"
        return run_gemma_sentence(input_to_gemma)
