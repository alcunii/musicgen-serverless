"""
Test script for MusicGen RunPod Serverless Endpoint

RunPod serverless API:
- POST /v2/{endpoint_id}/runsync - Synchronous (waits for result)
- POST /v2/{endpoint_id}/run - Async (returns job_id)
- GET /v2/{endpoint_id}/status/{job_id} - Check async job status

Usage:
    python test_endpoint.py <endpoint_id> <runpod_api_key>

Example:
    python test_endpoint.py abc123xyz YOUR_RUNPOD_API_KEY
"""

import sys
import time
import base64
import requests
from pathlib import Path


RUNPOD_API_BASE = "https://api.runpod.ai/v2"


def test_runsync(endpoint_id: str, api_key: str, output_dir: Path) -> bool:
    """Test synchronous generation."""
    print("\n[1/2] Testing synchronous generation (runsync)...")

    url = f"{RUNPOD_API_BASE}/{endpoint_id}/runsync"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": "calm ambient music with soft piano and gentle strings, peaceful and relaxing",
            "duration": 10,  # Short for testing
            "cfg_coef": 3.0
        }
    }

    print(f"  POST {url}")
    print(f"  Prompt: '{payload['input']['prompt'][:40]}...'")
    print(f"  Duration: {payload['input']['duration']}s")
    print("  (This may take 5-10+ minutes on cold start...)")

    try:
        start = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=900)  # 15 min timeout
        elapsed = time.time() - start

        print(f"  Status: {response.status_code}")
        print(f"  Time: {elapsed:.1f}s")

        if response.status_code == 200:
            data = response.json()

            # Check for RunPod status
            status = data.get("status")
            print(f"  RunPod Status: {status}")

            if status == "COMPLETED":
                output = data.get("output", {})

                if "error" in output:
                    print(f"  Error: {output['error']}")
                    return False

                if "audio" in output:
                    # Decode and save audio
                    audio_bytes = base64.b64decode(output["audio"])
                    output_path = output_dir / "test_runpod_output.wav"

                    with open(output_path, "wb") as f:
                        f.write(audio_bytes)

                    print(f"  Audio size: {len(audio_bytes):,} bytes")
                    print(f"  Duration: {output.get('duration_seconds', 'N/A')}s")
                    print(f"  Saved to: {output_path}")
                    print("  Result: PASSED")
                    return True

            elif status == "FAILED":
                print(f"  Error: {data.get('error', 'Unknown error')}")
                return False

            elif status == "IN_QUEUE" or status == "IN_PROGRESS":
                print("  Job is still processing. Try /run + polling instead.")
                return False

        print(f"  Response: {response.text[:500]}")
        return False

    except requests.exceptions.Timeout:
        print("  Result: TIMEOUT (job may still be running)")
        print("  Try using async mode (/run) for long jobs")
        return False
    except Exception as e:
        print(f"  Result: ERROR - {e}")
        return False


def test_async(endpoint_id: str, api_key: str, output_dir: Path) -> bool:
    """Test async generation with polling."""
    print("\n[2/2] Testing async generation (run + polling)...")

    # Submit job
    url = f"{RUNPOD_API_BASE}/{endpoint_id}/run"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": "upbeat electronic music with synths",
            "duration": 5,  # Very short
            "cfg_coef": 3.0
        }
    }

    print(f"  POST {url}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            print(f"  Failed to submit job: {response.text}")
            return False

        data = response.json()
        job_id = data.get("id")

        if not job_id:
            print(f"  No job ID returned: {data}")
            return False

        print(f"  Job ID: {job_id}")
        print("  Polling for status...")

        # Poll for completion
        status_url = f"{RUNPOD_API_BASE}/{endpoint_id}/status/{job_id}"

        for i in range(60):  # Max 10 minutes (60 * 10s)
            time.sleep(10)

            status_response = requests.get(status_url, headers=headers, timeout=30)

            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")

                print(f"  [{i+1}] Status: {status}")

                if status == "COMPLETED":
                    output = status_data.get("output", {})

                    if "audio" in output:
                        audio_bytes = base64.b64decode(output["audio"])
                        output_path = output_dir / "test_runpod_async_output.wav"

                        with open(output_path, "wb") as f:
                            f.write(audio_bytes)

                        print(f"  Audio saved to: {output_path}")
                        print("  Result: PASSED")
                        return True

                    return False

                elif status == "FAILED":
                    print(f"  Error: {status_data.get('error', 'Unknown')}")
                    return False

                elif status in ["IN_QUEUE", "IN_PROGRESS"]:
                    continue

        print("  Result: TIMEOUT after 10 minutes")
        return False

    except Exception as e:
        print(f"  Result: ERROR - {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_endpoint.py <endpoint_id> <runpod_api_key>")
        print("\nExample:")
        print("  python test_endpoint.py abc123xyz YOUR_API_KEY")
        print("\nGet your endpoint ID from: https://www.runpod.io/console/serverless")
        print("Get your API key from: https://www.runpod.io/console/user/settings")
        sys.exit(1)

    endpoint_id = sys.argv[1]
    api_key = sys.argv[2]
    output_dir = Path(__file__).parent

    print("=" * 60)
    print("MusicGen RunPod Serverless Endpoint Test")
    print("=" * 60)
    print(f"Endpoint ID: {endpoint_id}")
    print(f"API Key: {api_key[:10]}...")
    print(f"Output dir: {output_dir}")
    print("\nNote: First request triggers cold start (5-10+ minutes)")

    # Run tests
    results = []

    results.append(("Sync Generation", test_runsync(endpoint_id, api_key, output_dir)))

    if results[-1][1]:
        results.append(("Async Generation", test_async(endpoint_id, api_key, output_dir)))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll tests passed!")
        print(f"\nAdd to your .env file:")
        print(f"  RUNPOD_ENDPOINT_ID={endpoint_id}")
        print(f"  RUNPOD_API_KEY=your_api_key")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
