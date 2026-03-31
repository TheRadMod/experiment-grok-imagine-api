"""
03 - Video Parameter Exploration

Explores the effect of different video generation parameters:
  - Duration: 3s, 10s, 15s (max)
  - Aspect ratio: 16:9, 9:16 (vertical), 1:1 (square)
  - Resolution: 480p vs 720p

Uses the same prompt across all variants to isolate the effect of each
parameter. Logs timing and file sizes for comparison.

API constraints (from docs/video_generation_api.md):
  - Duration: 1-15 seconds
  - Aspect ratios: 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3
  - Resolutions: 480p, 720p
"""

import os
import sys
import logging
import time
from pathlib import Path
from datetime import timedelta

import requests
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
        logging.FileHandler(LOG_DIR / "03_video_params.log"),
    ],
)
logger = logging.getLogger(__name__)

# Same prompt for all variants so we can compare parameter effects
BASE_PROMPT = (
    "A cozy coffee shop interior, steam rising from a ceramic mug, "
    "rain streaking down the window outside, soft ambient lighting"
)


def generate_and_save(client, label, prompt, duration, aspect_ratio, resolution):
    """
    Generate a video with specific parameters and save to disk.

    Args:
        client: xai-sdk Client instance
        label: Short label for the variant (used in filename and logs)
        prompt: Text description
        duration: Video length in seconds
        aspect_ratio: e.g. "16:9", "9:16", "1:1"
        resolution: "480p" or "720p"

    Returns:
        Dict with generation stats (time, file size, path)
    """
    print(f"\n--- Generating: {label} ---")
    logger.info(f"[{label}] prompt='{prompt[:60]}...'")
    logger.info(f"[{label}] duration={duration}s, aspect_ratio={aspect_ratio}, resolution={resolution}")

    start_time = time.time()

    response = client.video.generate(
        prompt=prompt,
        model="grok-imagine-video",
        duration=duration,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        timeout=timedelta(minutes=15),
        interval=timedelta(seconds=5),
    )

    elapsed = time.time() - start_time
    logger.info(f"[{label}] Generated in {elapsed:.1f}s")

    # Download
    output_path = LOG_DIR / f"03_{label}.mp4"
    video_data = requests.get(response.url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    logger.info(f"[{label}] Saved: {output_path} ({file_size_mb:.2f} MB)")

    return {
        "label": label,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "resolution": resolution,
        "gen_time_s": round(elapsed, 1),
        "file_size_mb": round(file_size_mb, 2),
        "path": str(output_path),
    }


def print_comparison_table(results):
    """Print a formatted comparison table of all generated variants."""
    print("\n" + "=" * 80)
    print("  Parameter Comparison Results")
    print("=" * 80)
    print(f"  {'Label':<25} {'Duration':>8} {'Aspect':>8} {'Res':>6} {'Gen Time':>10} {'Size':>8}")
    print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*6} {'-'*10} {'-'*8}")

    for result in results:
        print(
            f"  {result['label']:<25} "
            f"{result['duration']:>7}s "
            f"{result['aspect_ratio']:>8} "
            f"{result['resolution']:>6} "
            f"{result['gen_time_s']:>8.1f}s "
            f"{result['file_size_mb']:>6.2f}MB"
        )
    print("=" * 80)


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Video Parameter Exploration")
    print("=" * 60)

    if not os.environ.get("XAI_API_KEY"):
        logger.error("XAI_API_KEY not set.")
        sys.exit(1)

    client = Client()
    results = []

    # -----------------------------------------------------------------------
    # Test 1: Duration variants (at 480p, 16:9)
    # -----------------------------------------------------------------------
    for duration in [3, 10, 15]:
        result = generate_and_save(
            client,
            label=f"duration_{duration}s",
            prompt=BASE_PROMPT,
            duration=duration,
            aspect_ratio="16:9",
            resolution="480p",
        )
        results.append(result)

    # -----------------------------------------------------------------------
    # Test 2: Aspect ratio variants (at 480p, 5s)
    # -----------------------------------------------------------------------
    for aspect_ratio in ["9:16", "1:1"]:
        label = f"aspect_{aspect_ratio.replace(':', 'x')}"
        result = generate_and_save(
            client,
            label=label,
            prompt=BASE_PROMPT,
            duration=5,
            aspect_ratio=aspect_ratio,
            resolution="480p",
        )
        results.append(result)

    # -----------------------------------------------------------------------
    # Test 3: Resolution comparison (5s, 16:9)
    # -----------------------------------------------------------------------
    result = generate_and_save(
        client,
        label="resolution_720p",
        prompt=BASE_PROMPT,
        duration=5,
        aspect_ratio="16:9",
        resolution="720p",
    )
    results.append(result)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print_comparison_table(results)
