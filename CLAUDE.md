# Grok Imagine API - Experimental Project

## Overview

This experiment explores the Grok Imagine API from xAI — a unified API for
generating and editing videos, images, and audio. The goal is to learn all
capabilities of the API (text-to-video, image-to-video, video editing,
video extension, image generation, image editing) to become proficient for
later use in larger projects.

## Auto-Mode

This is an auto-mode experiment. Claude should continue executing without
asking for permissions at each step. Build, run, verify, and move on. Only
stop to ask if something fails or if a genuine design decision needs input.

## Technology Version

- Technology: Grok Imagine API (xAI)
- Model (video): `grok-imagine-video` (Grok Imagine 1.0)
- Model (image): `grok-imagine-image` / `grok-imagine-image-pro`
- Python SDK: `xai-sdk` (latest via PyPI, requires Python 3.10+)
- Base URL: `https://api.x.ai/v1`
- Version check date: 2026-03-30
- Note: Future sessions should check if newer model versions or SDK updates
  are available. The Grok Imagine 1.0 was announced Feb 2, 2026.

## Documentation Sources

IMPORTANT: All scripts in this experiment MUST be based on the fetched
documentation stored in the docs/ folder, NOT on general training knowledge.
This ensures accuracy for the specific version.

- Official API docs: https://docs.x.ai/developers/model-capabilities/video/generation
- Image generation docs: https://docs.x.ai/developers/model-capabilities/images/generation
- Video guide: https://docs.x.ai/docs/guides/video-generation
- Quickstart: https://docs.x.ai/developers/quickstart
- Python SDK: https://github.com/xai-org/xai-sdk-python
- API announcement: https://x.ai/news/grok-imagine-api

- docs/ folder contents:
  - `video_generation_api.md` — Video generation, editing, extension endpoints and parameters
  - `image_generation_api.md` — Image generation and editing endpoints and parameters
  - `quickstart_and_sdk.md` — Authentication, SDK installation, client setup

## Key Concepts

1. **Asynchronous generation** — All generation is async (submit job, poll for result). SDK abstracts this.
2. **Multi-modal generation** — Single API family handles video, image, and audio.
3. **Generation modes** — Text-to-video, image-to-video, reference-image-guided, video editing, video extension.
4. **Native audio** — Videos include synchronized audio (dialogue, SFX, ambience) in a single pass.
5. **Iterative editing** — Both images and videos can be edited with natural language prompts.

## Capabilities to Explore

1. Basic SDK setup and authentication
2. Text-to-video generation (various durations, aspect ratios, resolutions)
3. Image-to-video generation (animate a still image)
4. Reference-image-guided video generation (style/content guidance)
5. Video editing (modify existing video with natural language)
6. Video extension (extend video with new content)
7. Text-to-image generation (single and batch)
8. Image editing (natural language edits on existing images)
9. Multi-turn image editing (iterative refinement)
10. Async/concurrent generation (parallel requests)
11. Error handling and edge cases
12. Combining capabilities (image gen → image-to-video pipeline)

## Script Conventions

- Language: Python
- Naming: `NN_descriptive_name.py` (numbered for progression)
- Each script: Self-contained, runnable independently with `uv run python NN_name.py`
- Logging: `print()` for user-facing output + `logging` module with file handler for detailed logs
- Output: Terminal output for feedback + saved artifacts (videos as .mp4, images as .png) to `output/` directory
- Docstring: Each script starts with a module docstring explaining the concept
- Main guard: All scripts use `if __name__ == "__main__"`
- run_all script: No
- API key: Read from `GROK_IMAGINE_API_KEY` environment variable, mapped to SDK's expected format
- Dependencies managed via `requirements.txt`

## Progression Plan

1. `01_setup_and_auth.py` — Verify SDK installation, authenticate, list available models
2. `02_text_to_video.py` — Generate a video from a text prompt (basic text-to-video)
3. `03_video_params.py` — Explore duration, aspect ratio, and resolution parameters
4. `04_image_to_video.py` — Animate a still image into a video
5. `05_reference_images.py` — Use reference images to guide video style/content
6. `06_video_editing.py` — Edit an existing video with natural language prompts
7. `07_video_extension.py` — Extend a video with new continuation content
8. `08_text_to_image.py` — Generate images from text (single and batch)
9. `09_image_editing.py` — Edit existing images with natural language
10. `10_multi_turn_editing.py` — Iterative image refinement across multiple edits
11. `11_async_concurrent.py` — Parallel generation using AsyncClient
12. `12_pipeline.py` — Combined workflow: generate image → animate to video → extend

## Prerequisites

- Python 3.10+
- xAI SDK: `uv add xai-sdk`
- API key set as environment variable: `export GROK_IMAGINE_API_KEY="your_key"`
- xAI account with credits loaded: https://console.x.ai
- Install dependencies: `uv pip install -r requirements.txt`

## Integration Notes

- The async patterns from script 11 establish how to integrate video generation
  into web apps (submit job, return to user, notify on completion)
- The pipeline from script 12 demonstrates composable workflows for content
  creation tools
- Video editing (script 06) is directly applicable to building video
  post-processing features
- Image generation + image-to-video chaining enables "describe → visualize → animate"
  workflows in creative tools
- Batch image generation (script 08) is useful for generating thumbnails,
  social media assets, or style variations at scale

## GitHub Repository
<!-- Fill in after gh repo create -->

## Learnings
<!-- Updated as scripts are built and run. Record insights NOT obvious from docs. -->

## Status
- Created: 2026-03-30
- Status: Learning
