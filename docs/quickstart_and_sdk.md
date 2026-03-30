# xAI API Quickstart & Python SDK Reference

Sources:
- https://docs.x.ai/developers/quickstart
- https://github.com/xai-org/xai-sdk-python
Fetched: 2026-03-30

## Prerequisites

- Create account at https://accounts.x.ai/sign-up
- Load account with credits
- Generate API key at https://console.x.ai/team/default/api-keys

## Base URL

```
https://api.x.ai/v1
```

## Authentication

Set environment variable:
```bash
export XAI_API_KEY="your_api_key"
```

Or use `.env` file:
```
XAI_API_KEY=your_api_key
```

The SDK automatically reads from `XAI_API_KEY` environment variable.

## Python SDK Installation

```bash
pip install xai-sdk
# or with uv:
uv add xai-sdk
```

**Requirements:** Python 3.10 or higher

## Client Initialization

```python
from xai_sdk import Client, AsyncClient

# Auto-reads XAI_API_KEY from environment
sync_client = Client()
async_client = AsyncClient()

# Or explicit key:
client = Client(api_key="your_key")
```

## Configuration Options

- **Timeout**: Default 15 minutes (900 seconds)
  ```python
  client = Client(timeout=300)  # 5 minutes
  ```
- **Retries**: Enabled by default for UNAVAILABLE errors with exponential backoff
  ```python
  client = Client(channel_options=[("grpc.enable_retries", 0)])  # disable
  ```

## Available SDK Modules

### Chat
```python
from xai_sdk.chat import user, system

chat = client.chat.create(model="grok-4")
chat.append(system("System prompt"))
chat.append(user("User message"))
response = chat.sample()
print(response.content)
```

### Image Generation
Via `client.images` module.

### Video Generation
Via `client.video` module:
- `client.video.generate()` — text-to-video, image-to-video
- `client.video.extend()` — video extension

### Other Capabilities
- Function calling (tool use)
- Image understanding (vision)
- Structured outputs (Pydantic models)
- Reasoning models
- Deferred chat (long-running, polling)
- Tokenization
- Model information (pricing, token limits)

## Telemetry (Optional)

OpenTelemetry support:
```bash
pip install xai-sdk[telemetry-http]
```

Disable with: `XAI_SDK_DISABLE_TRACING=1`

## Important Notes

- SDK is gRPC-based
- Both sync and async clients available
- OpenAI SDK compatible (with base_url override) for chat and image generation
- OpenAI SDK NOT compatible for image editing (multipart/form-data vs JSON)
- Video URLs are ephemeral — download promptly
- Content subject to moderation policies

## Environment Variable

API key is stored as `XAI_API_KEY`. The SDK auto-detects this — no manual
mapping needed.
