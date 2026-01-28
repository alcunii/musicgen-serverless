"""
MusicGen-medium RunPod Serverless Handler

RunPod serverless expects a handler function that:
1. Receives an event dict with "input" key
2. Returns a dict with the result
3. Uses runpod.serverless.start() to run

Usage:
    Deploy this as a RunPod serverless endpoint
"""

import os
import io
import base64
import runpod
import numpy as np

# Global model (loaded once per worker)
model = None


def load_model():
    """Load MusicGen model (called once per cold start)."""
    global model
    if model is None:
        print("Loading MusicGen-medium model...")
        from audiocraft.models import MusicGen
        model = MusicGen.get_pretrained('facebook/musicgen-medium')
        print("Model loaded successfully!")
    return model


def generate_music(prompt: str, duration: int = 40, cfg_coef: float = 3.0) -> dict:
    """Generate music from text prompt."""
    import scipy.io.wavfile as wavfile

    try:
        # Load model if not already loaded
        music_model = load_model()

        # Validate duration
        if duration < 1 or duration > 60:
            return {"error": "Duration must be between 1 and 60 seconds"}

        # Set generation parameters
        music_model.set_generation_params(
            duration=duration,
            cfg_coef=cfg_coef
        )

        print(f"Generating music: prompt='{prompt[:50]}...', duration={duration}s")

        # Generate audio
        wav = music_model.generate([prompt])

        # Convert to numpy array
        audio_data = wav[0].cpu().numpy()

        # MusicGen outputs at 32kHz
        sample_rate = 32000

        # Save to WAV in memory
        buffer = io.BytesIO()

        # Normalize to int16 range
        audio_float = audio_data.squeeze()
        if audio_float.max() > 1.0 or audio_float.min() < -1.0:
            audio_float = audio_float / max(abs(audio_float.max()), abs(audio_float.min()))

        audio_int16 = (audio_float * 32767).astype(np.int16)

        # Handle shape for scipy
        if len(audio_int16.shape) > 1:
            audio_int16 = audio_int16.T

        wavfile.write(buffer, sample_rate, audio_int16)

        # Encode to base64
        buffer.seek(0)
        audio_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        actual_duration = len(audio_float) / sample_rate if len(audio_float.shape) == 1 else len(audio_float[0]) / sample_rate

        print(f"Generated {len(buffer.getvalue())} bytes of audio ({actual_duration:.1f}s)")

        return {
            "audio": audio_b64,
            "duration_seconds": actual_duration,
            "sample_rate": sample_rate
        }

    except Exception as e:
        print(f"Generation failed: {e}")
        return {"error": str(e)}


def handler(event):
    """
    RunPod serverless handler function.

    Input format:
    {
        "input": {
            "prompt": "calm ambient music with soft piano",
            "duration": 40,
            "cfg_coef": 3.0
        }
    }

    Output format:
    {
        "audio": "<base64 WAV>",
        "duration_seconds": 40.0,
        "sample_rate": 32000
    }

    Or on error:
    {
        "error": "error message"
    }
    """
    try:
        # Get input from event
        input_data = event.get("input", {})

        # Extract parameters
        prompt = input_data.get("prompt")
        duration = input_data.get("duration", 40)
        cfg_coef = input_data.get("cfg_coef", 3.0)

        # Validate required fields
        if not prompt:
            return {"error": "Missing required field: prompt"}

        # Generate music
        result = generate_music(prompt, duration, cfg_coef)

        return result

    except Exception as e:
        return {"error": str(e)}


# Pre-load model on cold start (optional but recommended)
print("RunPod MusicGen Handler Starting...")
load_model()
print("Handler ready!")

# Start the serverless handler
runpod.serverless.start({"handler": handler})
