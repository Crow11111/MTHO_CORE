---
name: gemini-api-dev
description: Use this skill when building applications with Gemini models, Gemini API, or modifying the ATLAS_CORE Google AI integration. Contains the standard procedure, keys, and model conventions for ATLAS_CORE.
---

# Gemini API Integration (ATLAS_CORE)

## Overview

This skill provides the standard procedure for integrating Google's Gemini API within the ATLAS_CORE project. It defines the required keys, the specific model versions to use, and how to instantiate the client properly according to the project's architecture.

## ATLAS_CORE Model Standards

> [!IMPORTANT]
> **Never** use Gemini 1.5, 2.0 Flash, or any older models. The system exclusively uses Pro models.

Always use these exact model strings:

- **Primary / Standard Model:** `gemini-3.1-pro-preview` (Gemini 3.1 Pro)
  - Used for Dev-Agent, Heavy Reasoning, WhatsApp, Brio Image Analysis.
- **Fallback Model:** `gemini-3-pro-preview` (Gemini 3 Pro)
  - Used if 3.1 Pro is unavailable.

## API Keys & Environment Variables

All API keys and model configurations must be loaded from the `.env` file. Do not hardcode keys or models in the code.

### Required `.env` variables:
- `GEMINI_API_KEY`: The primary API key for Google AI / Gemini API.
- `GEMINI_DEV_AGENT_MODEL`: (Optional) Overrides the Dev-Agent model. Default: `gemini-3.1-pro-preview`.
- `GEMINI_HEAVY_MODEL`: (Optional) Overrides the Heavy Reasoning model. Default: `gemini-3.1-pro-preview`.
- `BRIO_VISION_MODEL`: (Optional) Overrides the Brio Image Analysis model. Default: `gemini-3.1-pro-preview`.

## Python Integration Standard

ATLAS_CORE uses the new official `google-genai` SDK (not the deprecated `google-generativeai` package).

### Installation
Ensure the correct package is in `requirements.txt`:
```text
google-genai
```

### Basic Client Initialization
When writing or modifying API integration code in ATLAS_CORE (e.g., in `src/ai/`), use the following pattern:

```python
import os
from google import genai

# Load key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment.")

# Initialize the client
client = genai.Client(api_key=GEMINI_API_KEY)

# Determine the model based on the component's purpose
# Example for Dev-Agent:
MODEL_NAME = os.getenv("GEMINI_DEV_AGENT_MODEL", "gemini-3.1-pro-preview")

# Call the API
response = client.models.generate_content(
    model=MODEL_NAME,
    contents="Your prompt here"
)
print(response.text)
```

## System Prompts & Context

When calling Gemini for ATLAS components, always ensure that:
1. You pass the system prompt (instruction) appropriately.
2. You pass any contextual information before the user content.
3. You handle potential exceptions from the API gracefully (e.g., `genai.errors.APIError`).

## Reference Documentation
For advanced Gemini API features (Function Calling, Structured Outputs, Multimodal inputs), refer to the official documentation:
- **llms.txt URL**: `https://ai.google.dev/gemini-api/docs/llms.txt`
- **Models Spec**: `https://ai.google.dev/gemini-api/docs/models.md.txt`
