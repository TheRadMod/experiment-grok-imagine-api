"""
07 - Video Extension

Demonstrates extending an existing video with new continuation content.
The extension picks up from the end of the source video and generates
additional footage based on the prompt.

Two extension lengths are tested:
  1. Short extension (5s) — moderate continuation
  2. Long extension (10s, max) — maximum continuation

API details (from docs/video_generation_api.md):
  - Endpoint: /v1/videos/extensions
  - SDK method: client.video.extend(prompt, model, video_url, ...)
  - `video_url` is required (not optional)
  - `duration` controls extension length only, not total output
  - Input video must be 2-15 seconds
  - Extension duration: 2-10 seconds
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
        logging.FileHandler(OUTPUT_DIR / "07_video_extension.log"),
    ],
)
logger = logging.getLogger(__name__)

# Source video prompt
SOURCE_PROMPT = (
    "A train traveling through a snowy mountain pass, "
    "steam billowing from the locomotive, pine trees lining the tracks"
)

# Extension prompts (describe what happens next)
EXTEND_PROMPT_SHORT = (
    "The train enters a tunnel carved through the mountain, "
    "darkness briefly envelops the scene before emerging into a sunlit valley"
)

EXTEND_PROMPT_LONG = (
    "The train crosses a tall bridge over a deep river gorge, "
    "the camera pulls back to reveal the vast mountain landscape, "
    "birds fly alongside the train"
)


def generate_source_video(client):
    """
    Generate a short source video to extend.

    Returns:
        Tuple of (video_url, local_file_path, generation_time, file_size_mb)
    """
    print("\n--- Step 1: Generating source video (5s) ---")
    logger.info(f"Source prompt: '{SOURCE_PROMPT[:80]}...'")

    start_time = time.time()
    response = client.video.generate(
        prompt=SOURCE_PROMPT,
        model="grok-imagine-video",
        duration=5,
        aspect_ratio="16:9",
        resolution="480p",
        timeout=timedelta(minutes=10),
        interval=timedelta(seconds=5),
    )
    elapsed = time.time() - start_time

    video_url = response.url

    # Download and save
    output_path = OUTPUT_DIR / "07_source.mp4"
    video_data = requests.get(video_url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Source video saved: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")
    logger.info(f"Source video: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")

    return video_url, output_path, elapsed, file_size_mb


def extend_video(client, label, video_url, prompt, duration):
    """
    Extend an existing video with continuation content.

    Args:
        client: xai-sdk Client instance
        label: Short label for filename and logs
        video_url: URL of the source video to extend
        prompt: Description of the continuation content
        duration: Extension length in seconds (2-10)

    Returns:
        Dict with generation stats
    """
    print(f"\n--- Extending video: {label} (duration={duration}s) ---")
    logger.info(f"[{label}] prompt='{prompt[:80]}...'")
    logger.info(f"[{label}] extension duration={duration}s")

    start_time = time.time()
    response = client.video.extend(
        prompt=prompt,
        model="grok-imagine-video",
        video_url=video_url,
        duration=duration,
        timeout=timedelta(minutes=10),
        interval=timedelta(seconds=5),
    )
    elapsed = time.time() - start_time

    # Download extended video
    output_path = OUTPUT_DIR / f"07_{label}.mp4"
    video_data = requests.get(response.url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Extended video saved: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")
    logger.info(f"[{label}] Generated in {elapsed:.1f}s, saved: {output_path} ({file_size_mb:.2f} MB)")

    return {
        "label": label,
        "ext_duration_s": duration,
        "gen_time_s": round(elapsed, 1),
        "file_size_mb": round(file_size_mb, 2),
        "path": str(output_path),
    }


def print_comparison_table(source_time, source_size, results):
    """Print a formatted comparison table."""
    print("\n" + "=" * 70)
    print("  Video Extension: Comparison Results")
    print("=" * 70)
    print(f"  {'Label':<20} {'Ext Dur':>8} {'Gen Time':>10} {'Size':>8}")
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*8}")
    print(f"  {'source (5s)':<20} {'—':>8} {source_time:>8.1f}s {source_size:>6.2f}MB")

    for result in results:
        print(
            f"  {result['label']:<20} "
            f"{result['ext_duration_s']:>7}s "
            f"{result['gen_time_s']:>8.1f}s "
            f"{result['file_size_mb']:>6.2f}MB"
        )
    print("=" * 70)


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Video Extension")
    print("=" * 60)

    if not os.environ.get("XAI_API_KEY"):
        logger.error("XAI_API_KEY not set.")
        sys.exit(1)

    client = Client()
    results = []

    # Step 1: Generate source video
    video_url, local_path, source_time, source_size = generate_source_video(client)

    # Step 2: Short extension (5s)
    result = extend_video(
        client, "extend_5s", video_url, EXTEND_PROMPT_SHORT, duration=5
    )
    results.append(result)

    # Step 3: Long extension (10s max)
    result = extend_video(
        client, "extend_10s", video_url, EXTEND_PROMPT_LONG, duration=10
    )
    results.append(result)

    # Step 4: Comparison
    print_comparison_table(source_time, source_size, results)
