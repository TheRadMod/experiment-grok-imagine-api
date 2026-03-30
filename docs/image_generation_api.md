# Grok Imagine Image Generation & Editing API Documentation

Source: https://docs.x.ai/developers/model-capabilities/images/generation
Fetched: 2026-03-30

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /v1/images/generations` | POST | Generate images from text |
| `POST /v1/images/edits` | POST | Edit existing images |

## Model

- Standard: `grok-imagine-image`
- Pro: `grok-imagine-image-pro` (higher quality, higher cost)

## Request Parameters

| Parameter | Type | Values | Notes |
|-----------|------|--------|-------|
| `model` | string | `grok-imagine-image` or `grok-imagine-image-pro` | Required |
| `prompt` | string | Text description | Required |
| `n` | integer | 1-10 | Number of images per request |
| `aspect_ratio` | string | `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `3:2`, `2:3`, `2:1`, `1:2`, `19.5:9`, `9:19.5`, `20:9`, `9:20`, `auto` | Output dimensions |
| `resolution` | string | `1k`, `2k` | Output quality/size |
| `response_format` | string | `url` (default), `b64_json` | Return format |
| `image_url` | string | Public URL or base64 data URI | For editing existing images |

## Request Examples

### Text-to-Image
```json
{
  "model": "grok-imagine-image",
  "prompt": "Your text description",
  "aspect_ratio": "16:9",
  "n": 1
}
```

### Image Editing
Provide source image via `image_url` parameter plus editing prompt.

**IMPORTANT:** The OpenAI SDK's `images.edit()` method is NOT supported (uses
multipart/form-data, xAI requires application/json). Use xAI SDK, Vercel AI
SDK, or direct HTTP requests instead.

### Multi-Turn Editing
Chain outputs to inputs for iterative refinement.

### Multi-Image Editing
Up to 5 source images with customizable output aspect ratio.

## Response Format

Default returns object with `url` property (temporary image link).
Base64 mode returns `b64_json` with encoded image data.

## Supported Use Cases

- Single image generation from text
- Batch generation (up to 10 images per request)
- Image editing with natural language
- Multi-turn editing (iterative refinement)
- Style transfer
- Concurrent requests using AsyncClient
- Multi-image editing (up to 5 source images)

## Limitations

- Maximum 10 images per single request
- Generated URLs expire — download promptly
- Content moderation applies
- Image editing charges for both input and output images

## SDK Compatibility

- xAI SDK (recommended)
- OpenAI SDK (with base_url override) — generation only, NOT editing
- Vercel AI SDK
- Direct HTTP requests

## Pricing

- Standard (`grok-imagine-image`): $0.02 per image
- Pro (`grok-imagine-image-pro`): $0.07 per image
- Batch discount (50%): $0.01 / $0.035 respectively
