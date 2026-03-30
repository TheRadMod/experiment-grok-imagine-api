"""
01 - Setup and Authentication

Verifies that the xAI SDK is installed correctly, authenticates using the
XAI_API_KEY environment variable, and retrieves available model information.

This is the foundational script — if this works, the SDK and credentials
are properly configured for all subsequent scripts.

Uses the REST API directly (via requests) for model listing, and verifies
the xai-sdk Client initializes. Subsequent scripts will use xai-sdk for
video and image generation.
"""

import os
import sys
import logging
from pathlib import Path

import requests

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
        logging.FileHandler(LOG_DIR / "01_setup_and_auth.log"),
    ],
)
logger = logging.getLogger(__name__)

BASE_URL = "https://api.x.ai/v1"


def check_api_key():
    """Check that the XAI_API_KEY environment variable is set."""
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        logger.error("XAI_API_KEY environment variable is not set.")
        logger.error("Set it with: export XAI_API_KEY='your_key'")
        sys.exit(1)

    # Show first/last 4 chars for verification without exposing the full key
    masked_key = f"{api_key[:4]}...{api_key[-4:]}"
    logger.info(f"API key found: {masked_key}")
    return api_key


def check_sdk_version():
    """Log the installed xai-sdk version."""
    try:
        import importlib.metadata

        sdk_version = importlib.metadata.version("xai-sdk")
        logger.info(f"xai-sdk version: {sdk_version}")
        return sdk_version
    except importlib.metadata.PackageNotFoundError:
        logger.error("xai-sdk is not installed. Install with: uv add xai-sdk")
        sys.exit(1)


def verify_sdk_client():
    """Verify the xai-sdk Client can be instantiated without errors."""
    try:
        from xai_sdk import Client

        client = Client()
        logger.info("xai-sdk Client instantiated successfully.")
        return client
    except Exception as error:
        logger.error(f"Failed to instantiate xai-sdk Client: {error}")
        return None


def list_models(api_key):
    """Retrieve and display available models from the xAI REST API."""
    logger.info("Fetching available models via REST API...")

    response = requests.get(
        f"{BASE_URL}/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    models = data.get("data", [])
    imagine_models = []
    other_models = []

    for model in models:
        model_id = model.get("id", "unknown")
        if "imagine" in model_id.lower():
            imagine_models.append(model_id)
        else:
            other_models.append(model_id)

    logger.info(f"Total models available: {len(imagine_models) + len(other_models)}")

    print("\n--- Grok Imagine Models ---")
    if imagine_models:
        for model_id in sorted(imagine_models):
            print(f"  * {model_id}")
    else:
        print("  (none found — check API access)")

    print(f"\n--- Other Models ({len(other_models)}) ---")
    for model_id in sorted(other_models):
        print(f"  * {model_id}")

    return imagine_models


def test_api_connectivity(api_key):
    """
    Make a minimal chat request to verify end-to-end API connectivity.
    Confirms the API key has valid permissions.
    """
    logger.info("Testing API connectivity with a minimal chat request...")

    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "grok-3-mini-fast",
            "messages": [{"role": "user", "content": "Say 'hello' in one word."}],
            "max_tokens": 10,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    reply = data["choices"][0]["message"]["content"].strip()
    logger.info(f"API response: '{reply}'")
    logger.info("Connectivity test PASSED.")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("  Grok Imagine API — Setup & Authentication Check")
    print("=" * 60)

    # Step 1: Check API key is set
    api_key = check_api_key()

    # Step 2: Check SDK version
    check_sdk_version()

    # Step 3: Verify xai-sdk Client instantiation
    verify_sdk_client()

    # Step 4: List available models (find Imagine models)
    imagine_models = list_models(api_key)

    # Step 5: Test basic API connectivity
    test_api_connectivity(api_key)

    print("\n" + "=" * 60)
    print("  Setup complete. Ready for video/image generation scripts.")
    print("=" * 60)
