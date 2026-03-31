"""
05 - Reference-Image-Guided Video Generation

Demonstrates using reference images to guide video style and content.
Unlike image-to-video (script 04), reference images do NOT become the first
frame — they influence the overall look, style, and content of the generated
video.

Three tests are run:
  1. Single reference image — one style guide
  2. Multiple reference images with <IMAGE_1>, <IMAGE_2> placeholders
  3. Control — same prompt with no reference images (baseline for comparison)

API details (from docs/video_generation_api.md):
  - Parameter: `reference_image_urls` (list of URLs or base64 data URIs)
  - Guides style/content without locking first frame
  - Prompt can use <IMAGE_1>, <IMAGE_2> placeholders to reference specific images
  - Cannot combine with `image_url` (400 error)
"""

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
        logging.FileHandler(OUTPUT_DIR / "05_reference_images.log"),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompts for generating reference images
# ---------------------------------------------------------------------------
REF_IMAGE_PROMPT_1 = (
    "A vivid watercolor painting of a sunset over rolling hills, "
    "warm orange and purple palette, loose brushstrokes, artistic style"
)

REF_IMAGE_PROMPT_2 = (
    "A Japanese ukiyo-e woodblock print of ocean waves, "
    "deep blue and white, traditional art style, detailed linework"
)

# Video prompt used across all tests (same prompt to isolate reference effect)
VIDEO_PROMPT_SINGLE = (
    "A bird soaring over a mountain landscape at golden hour, "
    "cinematic camera movement, style matching <IMAGE_1>"
)

VIDEO_PROMPT_MULTI = (
    "A bird soaring over a mountain landscape at golden hour, "
    "the sky painted in the style of <IMAGE_1>, "
    "the terrain rendered in the style of <IMAGE_2>"
)

VIDEO_PROMPT_CONTROL = (
    "A bird soaring over a mountain landscape at golden hour, "
    "cinematic camera movement"
)


def generate_reference_images(client):
    """
    Generate two reference images to use as style guides.

    Returns:
        List of tuples: [(image_url, local_path), ...]
    """
    print("\n--- Step 1: Generating reference images ---")
    results = []

    for i, (prompt, label) in enumerate(
        [
            (REF_IMAGE_PROMPT_1, "watercolor_sunset"),
            (REF_IMAGE_PROMPT_2, "ukiyoe_waves"),
        ],
        start=1,
    ):
        logger.info(f"Generating ref image {i}: '{prompt[:60]}...'")
        start_time = time.time()

        response = client.image.sample(
            prompt=prompt,
            model="grok-imagine-image",
            aspect_ratio="16:9",
        )

        elapsed = time.time() - start_time
        image_url = response.url

        # Save locally
        output_path = OUTPUT_DIR / f"05_ref_{label}.png"
        image_data = requests.get(image_url, timeout=60)
        image_data.raise_for_status()
        output_path.write_bytes(image_data.content)

        file_size_kb = len(image_data.content) / 1024
        print(f"  Ref image {i} ({label}): {output_path} ({file_size_kb:.1f} KB, {elapsed:.1f}s)")
        logger.info(f"Ref {i} saved: {output_path} ({file_size_kb:.1f} KB, {elapsed:.1f}s)")

        results.append((image_url, output_path))

    return results


def generate_video(client, label, prompt, reference_image_urls=None):
    """
    Generate a video with optional reference images.

    Args:
        client: xai-sdk Client instance
        label: Short label for filename and logs
        prompt: Text description for the video
        reference_image_urls: Optional list of image URLs for style guidance

    Returns:
        Dict with generation stats
    """
    print(f"\n--- Generating video: {label} ---")
    logger.info(f"[{label}] prompt='{prompt[:80]}...'")

    if reference_image_urls:
        logger.info(f"[{label}] reference_image_urls: {len(reference_image_urls)} image(s)")
    else:
        logger.info(f"[{label}] No reference images (control)")

    start_time = time.time()

    kwargs = {
        "prompt": prompt,
        "model": "grok-imagine-video",
        "duration": 5,
        "aspect_ratio": "16:9",
        "resolution": "480p",
        "timeout": timedelta(minutes=10),
        "interval": timedelta(seconds=5),
    }
    if reference_image_urls:
        kwargs["reference_image_urls"] = reference_image_urls

    response = client.video.generate(**kwargs)
    elapsed = time.time() - start_time

    # Download video
    output_path = OUTPUT_DIR / f"05_{label}.mp4"
    video_data = requests.get(response.url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Video saved: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")
    logger.info(f"[{label}] Generated in {elapsed:.1f}s, saved: {output_path} ({file_size_mb:.2f} MB)")

    return {
        "label": label,
        "ref_count": len(reference_image_urls) if reference_image_urls else 0,
        "gen_time_s": round(elapsed, 1),
        "file_size_mb": round(file_size_mb, 2),
        "path": str(output_path),
    }


def print_comparison_table(results):
    """Print a formatted comparison of all generated video variants."""
    print("\n" + "=" * 70)
    print("  Reference Images: Comparison Results")
    print("=" * 70)
    print(f"  {'Label':<25} {'Refs':>5} {'Gen Time':>10} {'Size':>8}")
    print(f"  {'-'*25} {'-'*5} {'-'*10} {'-'*8}")

    for result in results:
        print(
            f"  {result['label']:<25} "
            f"{result['ref_count']:>5} "
            f"{result['gen_time_s']:>8.1f}s "
            f"{result['file_size_mb']:>6.2f}MB"
        )
    print("=" * 70)


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Reference-Image-Guided Video")
    print("=" * 60)

    if not os.environ.get("XAI_API_KEY"):
        logger.error("XAI_API_KEY not set.")
        sys.exit(1)

    client = Client()
    results = []

    # Step 1: Generate two reference images
    ref_images = generate_reference_images(client)
    ref_url_1 = ref_images[0][0]
    ref_url_2 = ref_images[1][0]

    # Step 2: Single reference image
    result = generate_video(
        client,
        label="single_ref",
        prompt=VIDEO_PROMPT_SINGLE,
        reference_image_urls=[ref_url_1],
    )
    results.append(result)

    # Step 3: Multiple reference images with placeholders
    result = generate_video(
        client,
        label="multi_ref",
        prompt=VIDEO_PROMPT_MULTI,
        reference_image_urls=[ref_url_1, ref_url_2],
    )
    results.append(result)

    # Step 4: Control — no reference images
    result = generate_video(
        client,
        label="no_ref_control",
        prompt=VIDEO_PROMPT_CONTROL,
    )
    results.append(result)

    # Step 5: Comparison
    print_comparison_table(results)
