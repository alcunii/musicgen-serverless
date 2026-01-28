# MusicGen RunPod Serverless

This directory contains everything needed to deploy MusicGen-medium as a RunPod serverless endpoint.

## Files

```
runpod/
├── handler.py              # RunPod serverless handler
├── Dockerfile              # Docker build configuration
├── test_endpoint.py        # Test script
├── README.md               # This file
└── .github/
    └── workflows/
        └── build-push.yml  # GitHub Actions workflow
```

## Setup Guide (GitHub Actions + RunPod)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `musicgen-serverless`
3. Make it **Public** (free unlimited GitHub Actions) or Private (2000 free minutes/month)

### Step 2: Create Docker Hub Access Token

1. Go to https://hub.docker.com/settings/security
2. Click **"New Access Token"**
3. Description: `github-actions`
4. Permissions: **Read & Write**
5. Click **Generate**
6. **Copy the token** (you won't see it again!)

### Step 3: Add GitHub Secrets

1. Go to your new repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add two secrets:

| Name | Value |
|------|-------|
| `DOCKER_USERNAME` | `dmrabh` (your Docker Hub username) |
| `DOCKER_PASSWORD` | (paste the access token from Step 2) |

### Step 4: Push Code to GitHub

From this directory (`serverless/runpod/`), run:

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: MusicGen RunPod serverless"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/musicgen-serverless.git

# Push
git push -u origin main
```

### Step 5: Verify GitHub Actions Build

1. Go to your repo on GitHub
2. Click **"Actions"** tab
3. You should see the workflow running
4. Wait for it to complete (10-15 minutes first time)
5. Check Docker Hub - image should appear at `dmrabh/musicgen-runpod:latest`

### Step 6: Create RunPod Serverless Endpoint

1. Go to https://www.runpod.io/console/serverless
2. Click **"New Endpoint"**
3. Select **"Import from Docker Registry"**
4. Enter image: `dmrabh/musicgen-runpod:latest`
5. Configure:
   - **GPU**: RTX 3090 or RTX 4090 (24GB VRAM required)
   - **Container Disk**: 20 GB
   - **Min Workers**: 0 (scale to zero)
   - **Max Workers**: 1
6. Click **Create**

### Step 7: Get API Key

1. Go to https://www.runpod.io/console/user/settings
2. Find or create an **API Key**
3. Copy it

### Step 8: Test the Endpoint

```bash
# From the serverless/runpod directory
python test_endpoint.py YOUR_ENDPOINT_ID YOUR_API_KEY
```

## API Reference

### Input Format

```json
{
  "input": {
    "prompt": "calm ambient music with soft piano",
    "duration": 40,
    "cfg_coef": 3.0
  }
}
```

### Output Format

```json
{
  "audio": "<base64 encoded WAV>",
  "duration_seconds": 40.0,
  "sample_rate": 32000
}
```

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /v2/{id}/runsync` | Synchronous - waits for result |
| `POST /v2/{id}/run` | Async - returns job ID |
| `GET /v2/{id}/status/{job_id}` | Check async job status |

## Costs

| Item | Cost |
|------|------|
| GitHub Actions | Free (public repo) or 2000 min/month (private) |
| Docker Hub | Free (public images) |
| RunPod GPU | ~$0.00025/sec (~$0.90/hour for RTX 4090) |

For occasional use generating 15 videos/month, expect ~$1-3 in RunPod costs.
