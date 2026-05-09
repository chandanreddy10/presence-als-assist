from fastapi import FastAPI
from pydantic import BaseModel
from ollama import chat
import time

#gemma4 service to run on a VM supported by GPU.
app = FastAPI()


class LLMRequest(BaseModel):
    text: str


def run_gemma(prompt: str):
    start = time.time()

    response = chat(
        model="gemma4:e2b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=False
    )

    end = time.time()

    return {
        "response": response.message.content,
        "requires_tts": True,
        "latency_ms": round((end - start) * 1000, 2)
    }


@app.post("/gemma")
def gemma_endpoint(req: LLMRequest):
    return run_gemma(req.text)