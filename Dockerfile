FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y git ffmpeg libgl1 unzip wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/comfyanonymous/ComfyUI.git
WORKDIR /app/ComfyUI
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/ComfyUI/custom_nodes
RUN git clone https://github.com/rgthree/rgthree-comfy.git
RUN git clone https://github.com/AP-Next/ComfyUI-APNext.git
RUN git clone https://github.com/black-forest-labs/ComfyUI_Flux.git
RUN git clone https://github.com/kijai/ComfyUI-KJNodes.git
RUN git clone https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes.git
RUN git clone https://github.com/BilboAI/bilbox-nodes.git
RUN git clone https://github.com/TencentARC/Portrait-Master-ComfyUI.git

WORKDIR /app/ComfyUI/models
RUN mkdir -p checkpoints vae clip t5 style_models Lora upscale_models bbox sam

WORKDIR /app/ComfyUI/models/checkpoints
RUN wget -O flux1-dev.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors

WORKDIR /app/ComfyUI/models/vae
RUN wget -O ae.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors

WORKDIR /app/ComfyUI/models/clip
RUN wget -O clip_l.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/clip_l.safetensors

WORKDIR /app/ComfyUI/models/t5
RUN wget -O t5xxl_fp16.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/t5xxl_fp16.safetensors

WORKDIR /app/ComfyUI/models/style_models
RUN wget -O flux1-redux-dev.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-redux-dev.safetensors

WORKDIR /app
COPY comfyui_workflow.json comfyui_workflow.json
COPY requirements.txt requirements.txt
COPY handler.py handler.py
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "handler.py"]
