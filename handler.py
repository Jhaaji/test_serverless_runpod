import runpod
import requests
import json
import os
import time

COMFY_API = "http://127.0.0.1:8188"
WORKFLOW_PATH = "/app/comfyui_workflow.json"

def start_comfyui():
    os.system("cd /app/ComfyUI && python3 main.py --dont-print-server --port 8188 &")
    time.sleep(30)

def handler(event):
    if not os.path.exists("/tmp/comfyui_started"):
        start_comfyui()
        with open("/tmp/comfyui_started", "w") as f:
            f.write("yes")

    path = event.get("endpoint", "/")
    input_data = event.get("input", {})

    if path == "/prompt":
        with open(WORKFLOW_PATH, "r") as f:
            workflow = json.load(f)

        if "35" in workflow and "prompt" in input_data:
            workflow["35"]["inputs"]["prompt"] = input_data["prompt"]

        r = requests.post(f"{COMFY_API}/prompt", json=workflow)
        return r.json()

    elif path.startswith("/history/"):
        prompt_id = path.split("/history/")[1]
        r = requests.get(f"{COMFY_API}/history/{prompt_id}")
        return r.json()

    elif path == "/queue":
        r = requests.get(f"{COMFY_API}/queue")
        return r.json()

    else:
        return {"error": "Invalid endpoint. Use /prompt, /history/{id}, or /queue"}

runpod.serverless.start({"handler": handler})
