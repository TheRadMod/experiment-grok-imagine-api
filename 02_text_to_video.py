"""
02 - Text-to-Video Generation

Generates a video from a text prompt using the Grok Imagine Video API.
Demonstrates the basic async workflow: submit request -> poll for status
-> download completed video.

Uses the xai-sdk Client which handles polling automatically via
client.video.generate().

API details (from docs/video_generation_api.md):
  - Endpoint: POST /v1/videos/generations
  - Model: grok-imagine-video
  - Duration: 1-15 seconds
  - Default resolution: 480p
  - Default aspect_ratio: 16:9
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import timedelta

from xai_sdk import Client

# ---------------------------------------------------------------------------
# Logging setup: terminal + file
# ---------------------------------------------------------------------------
LOG_DIR = Path(__file__).parent / "output"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "02_text_to_video.log"),
    ],
)
logger = logging.getLogger(__name__)


def generate_video(client, prompt, duration=5):
    """
    Generate a video from a text prompt.

    Args:
        client: xai-sdk Client instance
        prompt: Text description of the desired video
        duration: Video length in seconds (1-15)

    Returns:
        The response object containing the video URL
    """
    logger.info(f"Generating video: '{prompt}'")
    logger.info(f"Duration: {duration}s, Resolution: 480p, Aspect ratio: 16:9")

    start_time = time.time()

    response = client.video.generate(
        prompt=prompt,
        model="grok-imagine-video",
        duration=duration,
        aspect_ratio="16:9",
        resolution="480p",
        timeout=timedelta(minutes=10),
        interval=timedelta(seconds=5),
    )

    elapsed = time.time() - start_time
    logger.info(f"Video generated in {elapsed:.1f} seconds")

    return response


def download_video(video_url, output_path):
    """
    Download a video from a temporary URL and save to disk.

    Video URLs from the API are ephemeral — they must be downloaded promptly.

    Args:
        video_url: The temporary URL returned by the API
        output_path: Local path to save the video file
    """
    import requests

    logger.info(f"Downloading video to {output_path}...")
    response = requests.get(video_url, timeout=120)
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)

    file_size_mb = len(response.content) / (1024 * 1024)
    logger.info(f"Saved: {output_path} ({file_size_mb:.2f} MB)")


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Text-to-Video Generation")
    print("=" * 60)

    # Verify API key
    if not os.environ.get("XAI_API_KEY"):
        logger.error("XAI_API_KEY not set. Run 01_setup_and_auth.py first.")
        sys.exit(1)

    client = Client()

    # Generate a simple 5-second video with a descriptive prompt
    prompt = (
        "A golden retriever running through a sunlit meadow, "
        "wildflowers swaying in the breeze, shot in slow motion "
        "with warm cinematic lighting"
    )

    response = generate_video(client, prompt, duration=5)

    # Extract URL and download
    video_url = response.url
    logger.info(f"Video URL: {video_url}")

    output_path = LOG_DIR / "02_text_to_video.mp4"
    download_video(video_url, output_path)

    print("\n" + "=" * 60)
    print(f"  Video saved to: {output_path}")
    print("=" * 60)
