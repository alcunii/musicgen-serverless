# MusicGen-medium RunPod Serverless Dockerfile
#
# Build: docker build -t your-username/musicgen-runpod:latest .
# Push:  docker push your-username/musicgen-runpod:latest

FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app

# Install system dependencies required for audiocraft/PyAV
RUN apt-get update && apt-get install -y \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install \
    runpod \
    audiocraft \
    scipy \
    numpy

# Copy handler
COPY handler.py /app/handler.py

# Set the handler as entrypoint
CMD ["python", "-u", "/app/handler.py"]
