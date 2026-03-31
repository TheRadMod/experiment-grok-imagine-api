"""
04 - Image-to-Video Generation

Demonstrates animating a still image into a video using the Grok Imagine API.
The source image becomes the first frame, and the prompt drives what motion
and animation are applied.

Two input methods are tested:
  1. URL — pass the image URL directly (from a generated image)
  2. Base64 — load a local image file, base64-encode it, pass as data URI

This script also generates its own source image via the image API, making
it fully self-contained.

API details (from docs/video_generation_api.md):
  - Parameter: `image_url` (URL or base64 data URI)
  - The image becomes the first frame of the video
  - Cannot combine `image_url` with `reference_image_urls` (400 error)
"""

import base64
import logging
import os
import sys
import time
from datetime import timedelta
from pathlib import Path

import requests
from xai_sdk import Client

# ---------------------------------------------------------------------------
# Logging setup: terminal + file
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(OUTPUT_DIR / "04_image_to_video.log"),
    ],
)
logger = logging.getLogger(__name__)

# Prompt for the source image (what to draw)
IMAGE_PROMPT = (
    "A serene Japanese garden with a stone lantern beside a still koi pond, "
    "cherry blossom trees in full bloom, soft morning light"
)

# Prompt for the video animation (what motion to apply to the still image)
VIDEO_PROMPT = (
    "Cherry blossom petals gently fall from the trees, "
    "koi fish glide slowly beneath the pond surface, "
    "a soft breeze ripples the water"
)


def generate_source_image(client):
    """
    Generate a source image using the image API.

    Returns:
        Tuple of (image_url, local_file_path)
    """
    print("\n--- Step 1: Generating source image ---")
    logger.info(f"Image prompt: '{IMAGE_PROMPT[:80]}...'")

    start_time = time.time()
    response = client.image.sample(
        prompt=IMAGE_PROMPT,
        model="grok-imagine-image",
        aspect_ratio="16:9",
    )
    elapsed = time.time() - start_time

    image_url = response.url
    logger.info(f"Image generated in {elapsed:.1f}s")
    logger.info(f"Image URL: {image_url[:80]}...")

    # Download and save locally
    output_path = OUTPUT_DIR / "04_source_image.png"
    image_data = requests.get(image_url, timeout=60)
    image_data.raise_for_status()
    output_path.write_bytes(image_data.content)

    file_size_kb = len(image_data.content) / 1024
    print(f"  Source image saved: {output_path} ({file_size_kb:.1f} KB)")
    print(f"  Generation time: {elapsed:.1f}s")
    logger.info(f"Saved: {output_path} ({file_size_kb:.1f} KB)")

    return image_url, output_path


def image_to_video_from_url(client, image_url):
    """
    Generate a video from an image URL (image becomes first frame).

    Args:
        client: xai-sdk Client instance
        image_url: Public URL of the source image

    Returns:
        Dict with generation stats
    """
    print("\n--- Step 2: Image-to-video (URL input) ---")
    logger.info(f"Video prompt: '{VIDEO_PROMPT[:80]}...'")
    logger.info(f"Image URL: {image_url[:80]}...")

    start_time = time.time()
    response = client.video.generate(
        prompt=VIDEO_PROMPT,
        model="grok-imagine-video",
        image_url=image_url,
        duration=5,
        resolution="480p",
        timeout=timedelta(minutes=10),
        interval=timedelta(seconds=5),
    )
    elapsed = time.time() - start_time

    # Download video
    output_path = OUTPUT_DIR / "04_from_url.mp4"
    video_data = requests.get(response.url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Video saved: {output_path} ({file_size_mb:.2f} MB)")
    print(f"  Generation time: {elapsed:.1f}s")
    logger.info(f"[URL] Generated in {elapsed:.1f}s, saved: {output_path} ({file_size_mb:.2f} MB)")

    return {
        "method": "URL",
        "gen_time_s": round(elapsed, 1),
        "file_size_mb": round(file_size_mb, 2),
        "path": str(output_path),
    }


def image_to_video_from_base64(client, local_image_path):
    """
    Generate a video from a base64-encoded local image.

    Reads the local image file, encodes it as a base64 data URI,
    and passes it as the image_url parameter.

    Args:
        client: xai-sdk Client instance
        local_image_path: Path to the local image file

    Returns:
        Dict with generation stats
    """
    print("\n--- Step 3: Image-to-video (base64 input) ---")

    # Read and encode the local image as a base64 data URI
    raw_bytes = Path(local_image_path).read_bytes()
    encoded = base64.b64encode(raw_bytes).decode("utf-8")
    data_uri = f"data:image/png;base64,{encoded}"

    logger.info(f"Base64 payload size: {len(data_uri) / 1024:.1f} KB")
    logger.info(f"Video prompt: '{VIDEO_PROMPT[:80]}...'")

    start_time = time.time()
    response = client.video.generate(
        prompt=VIDEO_PROMPT,
        model="grok-imagine-video",
        image_url=data_uri,
        duration=5,
        resolution="480p",
        timeout=timedelta(minutes=10),
        interval=timedelta(seconds=5),
    )
    elapsed = time.time() - start_time

    # Download video
    output_path = OUTPUT_DIR / "04_from_base64.mp4"
    video_data = requests.get(response.url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Video saved: {output_path} ({file_size_mb:.2f} MB)")
    print(f"  Generation time: {elapsed:.1f}s")
    logger.info(f"[Base64] Generated in {elapsed:.1f}s, saved: {output_path} ({file_size_mb:.2f} MB)")

    return {
        "method": "Base64",
        "gen_time_s": round(elapsed, 1),
        "file_size_mb": round(file_size_mb, 2),
        "path": str(output_path),
    }


def print_comparison_table(results):
    """Print a formatted comparison of URL vs base64 input methods."""
    print("\n" + "=" * 60)
    print("  Image-to-Video: URL vs Base64 Comparison")
    print("=" * 60)
    print(f"  {'Method':<10} {'Gen Time':>10} {'File Size':>12} {'Path'}")
    print(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*30}")

    for result in results:
        print(
            f"  {result['method']:<10} "
            f"{result['gen_time_s']:>8.1f}s "
            f"{result['file_size_mb']:>10.2f}MB "
            f"  {result['path']}"
        )
    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Image-to-Video Generation")
    print("=" * 60)

    if not os.environ.get("XAI_API_KEY"):
        logger.error("XAI_API_KEY not set.")
        sys.exit(1)

    client = Client()

    # Step 1: Generate source image
    image_url, local_image_path = generate_source_image(client)

    # Step 2: Image-to-video from URL
    result_url = image_to_video_from_url(client, image_url)

    # Step 3: Image-to-video from base64
    result_base64 = image_to_video_from_base64(client, local_image_path)

    # Step 4: Comparison
    print_comparison_table([result_url, result_base64])
