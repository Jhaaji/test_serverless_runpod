import os
import json
import time
import base64
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
COMFY_URL = "http://127.0.0.1:8188"
OUTPUT_FOLDER = "/workspace/ComfyUI/output"
WORKFLOW_FILE = "/workspace/workflow_api.json"

@app.on_event("startup")
async def startup_event():
    import subprocess
    subprocess.Popen(["python", "ComfyUI/main.py"], cwd="/workspace")

@app.post("/generate")
async def generate(request: Request):
    body = await request.json()
    workflow = json.load(open(WORKFLOW_FILE))

    if "prompt" in body:
        workflow["prompt"][1]["inputs"]["text"] = body["prompt"]

    for file in os.listdir(OUTPUT_FOLDER):
        os.remove(os.path.join(OUTPUT_FOLDER, file))

    requests.post(f"{COMFY_URL}/prompt", json=workflow)

    timeout = 30
    poll_interval = 2
    elapsed = 0
    image_path = None

    while elapsed < timeout:
        files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".png")]
        if files:
            image_path = os.path.join(OUTPUT_FOLDER, files[0])
            break
        time.sleep(poll_interval)
        elapsed += poll_interval

    if not image_path:
        return JSONResponse(status_code=504, content={"error": "Image generation timed out"})

    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

    return {
        "image_base64": encoded_string,
        "filename": os.path.basename(image_path),
        "status": "success"
    }
