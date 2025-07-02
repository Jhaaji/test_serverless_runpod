FROM python:3.10-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y git wget && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir torch torchvision torchaudio xformers fastapi uvicorn requests

RUN git clone https://github.com/comfyanonymous/ComfyUI.git
RUN git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git /workspace/ComfyUI/custom_nodes/ComfyUI_UltimateSDUpscale

RUN mkdir -p /workspace/ComfyUI/models/checkpoints && \
    wget -O /workspace/ComfyUI/models/checkpoints/juggernautXL_v8.safetensors \
    https://huggingface.co/RunDiffusion/Juggernaut-XL-v8/resolve/main/juggernautXL_v8.safetensors

COPY handler.py /workspace/handler.py
COPY workflow_api.json /workspace/workflow_api.json

EXPOSE 3000
CMD ["uvicorn", "handler:app", "--host", "0.0.0.0", "--port", "3000"]
