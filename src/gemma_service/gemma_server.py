from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import httpx
import asyncio

app = FastAPI()

# gemma URL for serving
GEMMA_URL = "http://localhost:8001/gemma"

SEM = asyncio.Semaphore(2)

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()

    async with httpx.AsyncClient(timeout=300.0) as client:

        try:
            while True:
                data = await websocket.receive_json()

                request_id = data.get("request_id")
                user_request = data.get("request")
                user_text = data.get("text")
                ## Manage the context.
                ##
                async with SEM:
                    resp = await client.post(
                        GEMMA_URL,
                        json={"text": user_text, "user_request": user_request},
                    )

                result = resp.json()

                # single full response
                await websocket.send_json(
                    {
                        "request_id": request_id,
                        "text": result["response"],
                        "input": data.get("text"),
                        "latency_llm": result.get("latency_ms"),
                        "done": True,
                    }
                )

        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print("Error:", e)
