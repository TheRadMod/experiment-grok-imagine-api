# Grok Imagine Video Generation & Editing API Documentation

Source: https://docs.x.ai/developers/model-capabilities/video/generation
Fetched: 2026-03-30

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/videos/generations` | POST | Generate or edit videos |
| `/v1/videos/extensions` | POST | Extend existing videos |
| `/v1/videos/{request_id}` | GET | Poll generation status |

## Authentication

```
Authorization: Bearer $XAI_API_KEY
```

## Model

- Model name: `grok-imagine-video`

## Request Parameters

### Core Generation Parameters

| Parameter | Type | Values | Notes |
|-----------|------|--------|-------|
| `model` | string | `grok-imagine-video` | Required |
| `prompt` | string | Any text description | Required |
| `duration` | integer | 1-15 seconds | Controls video length |
| `aspect_ratio` | string | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3` | Default: `16:9` |
| `resolution` | string | `480p`, `720p` | Default: `480p` |

### Image/Video Input Parameters

- `image` (URL or base64) — Still image for image-to-video (becomes first frame)
- `reference_images` (array) — Multiple reference images to guide style/content (does NOT lock first frame)
- `video_url` — Source video for editing or extension operations

### Advanced Parameters (SDK)

- `timeout` (Python SDK) — Max wait; defaults to 10 minutes
- `interval` (Python SDK) — Polling frequency; defaults to 100ms
- `pollTimeoutMs`, `pollIntervalMs` (AI SDK) — JavaScript equivalents

## Video Generation Modes

### 1. Text-to-Video
Prompt only. No image or video input.

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "Your prompt here",
    "duration": 10,
    "aspect_ratio": "16:9",
    "resolution": "720p"
  }'
```

### 2. Image-to-Video
Prompt + `image`. Source image becomes first frame.

Image format: public HTTPS URL or base64-encoded data URI.

### 3. Reference Images
Prompt + `reference_images`. Guides style/content without locking first frame.

Prompt can reference images using `<IMAGE_1>`, `<IMAGE_2>` placeholders.

**IMPORTANT:** Cannot combine `image` and `reference_images` in a single request (400 error).

### 4. Video Editing
Prompt + `video_url`. Preserves unchanged content while applying modifications.

Constraints:
- Does NOT support custom `duration` — retains original length (max 8.7 seconds)
- Does NOT support custom `aspect_ratio` — matches input video
- Does NOT support custom `resolution` — capped at 720p

### 5. Video Extension
Endpoint: `/v1/videos/extensions`

`video_url` + prompt describing continuation content.

Constraints:
- `duration` parameter controls extension length only, not total output
- Input video must be 2-15 seconds
- Extension duration range: 2-10 seconds

## Response Format

### Initial Response (on request submission)
```json
{"request_id": "d97415a1-5796-b7ec-379f-4e6819e08fdf"}
```

### Status Polling Response
```json
{
  "status": "done",
  "video": {
    "url": "https://vidgen.x.ai/.../video.mp4",
    "duration": 8,
    "respect_moderation": true
  },
  "model": "grok-imagine-video"
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `pending` | Processing in progress |
| `done` | Video ready for download |
| `expired` | Request timeout (typically 24 hours) |
| `failed` | Generation encountered an error |

## Python SDK Examples

```python
import os
import xai_sdk

client = xai_sdk.Client(api_key=os.getenv("XAI_API_KEY"))

# Text-to-video
response = client.video.generate(
    prompt="Description here",
    model="grok-imagine-video",
    duration=10,
    aspect_ratio="16:9",
    resolution="720p",
)
print(response.url)
```

SDK abstracts polling automatically through `generate()` and `extend()` methods.
Customize polling with `timeout` and `interval` parameters using timedelta objects.

### Async / Concurrent Operations

Use `AsyncClient` with `asyncio.gather()` for parallel requests.

## Error Handling

- `VideoGenerationError` — includes `code` and `message` attributes
- `TimeoutError` — raised when generation exceeds timeout

## Processing Time

Varies based on:
- Prompt complexity
- Video length (longer = more time)
- Resolution (720p slower than 480p)
- Operation type (editing adds overhead)

Typical: up to several minutes.

## Pricing

- Standard: ~$0.05 per second of generated video
- Batch (50% discount): ~$0.025 per second
- $4.20 per minute of generated video (including audio)
