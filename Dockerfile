# MusicGen-medium RunPod Serverless Dockerfile
#
# Build: docker build -t your-username/musicgen-runpod:latest .
# Push:  docker push your-username/musicgen-runpod:latest
#
# Or use RunPod's GitHub integration to build automatically

FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip && \
    pip install \
    runpod \
    audiocraft \
    scipy \
    numpy

# Copy handler
COPY handler.py /app/handler.py

# Pre-download model during build (optional - makes image larger but faster cold starts)
# Uncomment if you want model baked into image:
# RUN python -c "from audiocraft.models import MusicGen; MusicGen.get_pretrained('facebook/musicgen-medium')"

# Set the handler as entrypoint
CMD ["python", "-u", "/app/handler.py"]
