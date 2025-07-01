import runpod
import requests
import json
import os
import time
import base64
from pydantic import BaseModel

COMFY_API = "http://127.0.0.1:8188"
WORKFLOW_PATH = "/app/comfyui_workflow.json"
OUTPUT_FOLDER = "/app/ComfyUI/output"

def start_comfyui():
    os.system("cd /app/ComfyUI && python3 main.py --dont-print-server --port 8188 &")
    time.sleep(25)

class GenerateRequest(BaseModel):
    prompt: str

def run_workflow(inputs):
    # Boot ComfyUI if not started
    if not os.path.exists("/tmp/comfyui_started"):
        start_comfyui()
        with open("/tmp/comfyui_started", "w") as f:
            f.write("yes")

    prompt = inputs.get("prompt", "A woman posing in lingerie")

    # Load base workflow
    with open(WORKFLOW_PATH, "r") as f:
        workflow = json.load(f)

    # Inject dynamic prompt
    if "370" in workflow:
        workflow["370"]["inputs"]["prompt"] = prompt

    # Send workflow to ComfyUI
    res = requests.post(f"{COMFY_API}/prompt", json=workflow)
    res.raise_for_status()
    prompt_id = res.json().get("prompt_id")

    # Poll until ready
    result = None
    for _ in range(60):
        time.sleep(2)
        r = requests.get(f"{COMFY_API}/history/{prompt_id}")
        if r.status_code == 200 and r.json():
            result = r.json()
            break

    if not result:
        return {"status": "failed", "message": "Timeout or no output."}

    for node_id, node in result.items():
        if "images" in node:
            image_filename = node["images"][0]["filename"]
            image_path = os.path.join(OUTPUT_FOLDER, image_filename)
            with open(image_path, "rb") as img_file:
                image_b64 = base64.b64encode(img_file.read()).decode()
                return {"status": "success", "image_base64": image_b64}

    return {"status": "failed", "message": "No image found in output"}

# Main handler
def handler(event):
    # Ensure ComfyUI is started once
    if not os.path.exists("/tmp/comfyui_started"):
        start_comfyui()
        with open("/tmp/comfyui_started", "w") as f:
            f.write("yes")

    path = event.get("endpoint", "/")
    body = event.get("input", {})

    if path == "/generate":
        return run_workflow(body)
    else:
        return {"error": "Invalid endpoint. Use POST /generate"}

# Register with RunPod
runpod.serverless.start({"handler": handler})
