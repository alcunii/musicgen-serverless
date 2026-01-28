# MusicGen-medium RunPod Serverless Dockerfile
# Using pre-built audiocraft image to avoid dependency issues
#
# Build: docker build -t your-username/musicgen-runpod:latest .
# Push:  docker push your-username/musicgen-runpod:latest

# Use pre-built audiocraft image with all dependencies resolved
FROM d1abo/audiocraft:3.3.0

WORKDIR /app

# Install runpod SDK (audiocraft, torch, scipy, numpy already installed)
RUN pip install --no-cache-dir runpod

# Copy handler
COPY handler.py /app/handler.py

# Set the handler as entrypoint
CMD ["python", "-u", "/app/handler.py"]
