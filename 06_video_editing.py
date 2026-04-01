"""
06 - Video Editing with Natural Language

Demonstrates editing an existing video using natural language prompts.
The API preserves unchanged content while applying the described modifications.

Two edit types are tested on the same source video:
  1. Style edit — transform the visual style (e.g., watercolor painting)
  2. Content edit — add new elements (e.g., snow falling)

API details (from docs/video_generation_api.md):
  - Uses `client.video.generate()` with `video_url` parameter
  - No separate edit() method — editing is a mode of generate()
  - Constraints: retains original duration (max 8.7s input),
    aspect ratio, and resolution — no custom overrides allowed
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
        logging.FileHandler(OUTPUT_DIR / "06_video_editing.log"),
    ],
)
logger = logging.getLogger(__name__)

# Source video prompt
SOURCE_PROMPT = (
    "A calm lake surrounded by autumn trees, golden and red leaves, "
    "a wooden dock extending into the water, late afternoon sunlight"
)

# Edit prompts
STYLE_EDIT_PROMPT = (
    "Transform the scene into a watercolor painting style, "
    "soft brushstrokes, pastel colors, dreamy atmosphere"
)

CONTENT_EDIT_PROMPT = (
    "Add gentle snow falling across the scene, "
    "frost forming on the dock, breath-visible cold air"
)


def generate_source_video(client):
    """
    Generate a short source video to be used as editing input.

    Returns:
        Tuple of (video_url, local_file_path, generation_time)
    """
    print("\n--- Step 1: Generating source video ---")
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

    # Download and save locally
    output_path = OUTPUT_DIR / "06_source.mp4"
    video_data = requests.get(video_url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Source video saved: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")
    logger.info(f"Source video: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")

    return video_url, output_path, elapsed


def edit_video(client, label, video_url, edit_prompt):
    """
    Edit an existing video using a natural language prompt.

    Args:
        client: xai-sdk Client instance
        label: Short label for filename and logs
        video_url: URL of the source video to edit
        edit_prompt: Natural language description of the edit

    Returns:
        Dict with generation stats
    """
    print(f"\n--- Editing video: {label} ---")
    logger.info(f"[{label}] edit_prompt='{edit_prompt[:80]}...'")
    logger.info(f"[{label}] video_url={video_url[:80]}...")

    start_time = time.time()
    response = client.video.generate(
        prompt=edit_prompt,
        model="grok-imagine-video",
        video_url=video_url,
        timeout=timedelta(minutes=10),
        interval=timedelta(seconds=5),
    )
    elapsed = time.time() - start_time

    # Download edited video
    output_path = OUTPUT_DIR / f"06_{label}.mp4"
    video_data = requests.get(response.url, timeout=120)
    video_data.raise_for_status()
    output_path.write_bytes(video_data.content)

    file_size_mb = len(video_data.content) / (1024 * 1024)
    print(f"  Edited video saved: {output_path} ({file_size_mb:.2f} MB, {elapsed:.1f}s)")
    logger.info(f"[{label}] Generated in {elapsed:.1f}s, saved: {output_path} ({file_size_mb:.2f} MB)")

    return {
        "label": label,
        "gen_time_s": round(elapsed, 1),
        "file_size_mb": round(file_size_mb, 2),
        "path": str(output_path),
    }


def print_comparison_table(source_time, source_size, results):
    """Print a formatted comparison table."""
    print("\n" + "=" * 65)
    print("  Video Editing: Comparison Results")
    print("=" * 65)
    print(f"  {'Label':<20} {'Gen Time':>10} {'Size':>8}")
    print(f"  {'-'*20} {'-'*10} {'-'*8}")
    print(f"  {'source (original)':<20} {source_time:>8.1f}s {source_size:>6.2f}MB")

    for result in results:
        print(
            f"  {result['label']:<20} "
            f"{result['gen_time_s']:>8.1f}s "
            f"{result['file_size_mb']:>6.2f}MB"
        )
    print("=" * 65)


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Video Editing")
    print("=" * 60)

    if not os.environ.get("XAI_API_KEY"):
        logger.error("XAI_API_KEY not set.")
        sys.exit(1)

    client = Client()
    results = []

    # Step 1: Generate source video
    video_url, local_path, source_time = generate_source_video(client)
    source_size = local_path.stat().st_size / (1024 * 1024)

    # Step 2: Style edit
    result = edit_video(client, "style_edit", video_url, STYLE_EDIT_PROMPT)
    results.append(result)

    # Step 3: Content edit
    result = edit_video(client, "content_edit", video_url, CONTENT_EDIT_PROMPT)
    results.append(result)

    # Step 4: Comparison
    print_comparison_table(source_time, source_size, results)
