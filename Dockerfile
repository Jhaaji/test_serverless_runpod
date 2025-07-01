FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y git ffmpeg libgl1 unzip wget
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Clone ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /app/ComfyUI
RUN pip install -r requirements.txt

# Install API dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy serverless handler and workflow
COPY handler.py handler.py
COPY comfyui_workflow.json comfyui_workflow.json

# RunPod expects a handler file
CMD ["python3", "handler.py"]
