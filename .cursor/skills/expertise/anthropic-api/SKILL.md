---
name: anthropic-api
description: Use this skill when building applications with Claude models, Anthropic API, or modifying the MTHO_CORE Claude integration. Contains the standard procedure, keys, model conventions, and the relationship to Cursor Cloud Agents.
---

# Anthropic (Claude) API Integration (MTHO_CORE)

## Overview

This skill provides the standard procedure for integrating Anthropic's Claude API within MTHO_CORE. It defines the required keys, model hierarchy, client initialization, and clarifies how the direct API relates to the Cursor Cloud Agents that also use Claude.

## MTHO_CORE Model Standards

> [!IMPORTANT]
> Use the strongest available model for the task. Prefer Opus for deep reasoning and architecture. Use Sonnet for speed-sensitive or high-volume tasks. Always implement a fallback chain.

### Model Hierarchy (Strongest → Fastest)

| Tier | Model String | Name | Use Case |
|------|-------------|------|----------|
| **Primary (Heavy)** | `claude-opus-4-6` | Claude Opus 4.6 | Architecture, deep audit, complex reasoning |
| **Fallback (Heavy)** | `claude-opus-4-5` | Claude Opus 4.5 | If 4.6 is unavailable |
| **Primary (Fast)** | `claude-sonnet-4-6` | Claude Sonnet 4.6 | Balanced speed/quality, standard tasks |
| **Fallback (Fast)** | `claude-sonnet-4-5` | Claude Sonnet 4.5 | If Sonnet 4.6 is unavailable |
| **Legacy Fallback** | `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet | Last resort |

### Fallback Pattern (Mandatory)

Every API call MUST implement a fallback chain. Example:

```python
MODELS_TO_TRY = [
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-3-5-sonnet-20241022",
]
```

## API Keys & Environment Variables

All API keys must be loaded from `.env`. Never hardcode keys in code.

### Required `.env` variables:
- `ANTHROPIC_API_KEY`: The primary API key for Anthropic (starts with `sk-ant-`).

### Optional `.env` variables:
- `ANTHROPIC_HEAVY_MODEL`: Overrides the heavy model. Default: `claude-opus-4-6`.
- `ANTHROPIC_FAST_MODEL`: Overrides the fast model. Default: `claude-sonnet-4-6`.

## Python Integration Standard

MTHO_CORE uses the official `anthropic` Python SDK.

### Installation

Ensure the correct package is in `requirements.txt`:
```text
anthropic
```

### Basic Client Initialization

```python
import os
from anthropic import Anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment.")

client = Anthropic(api_key=ANTHROPIC_API_KEY)
```

### Standard API Call (Messages API)

```python
MODEL = os.getenv("ANTHROPIC_FAST_MODEL", "claude-sonnet-4-6")

response = client.messages.create(
    model=MODEL,
    max_tokens=4096,
    system="Du bist ein MTHO-Systemarchitekt. Antworte präzise, auf Deutsch.",
    messages=[
        {"role": "user", "content": "Dein Prompt hier"}
    ]
)

print(response.content[0].text)
```

### Required Headers (handled by SDK)

The SDK sets these automatically:
- `x-api-key`: API key
- `anthropic-version`: `2023-06-01`
- `content-type`: `application/json`

For raw HTTP calls (e.g., `curl`), set them manually:
```bash
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{"model":"claude-sonnet-4-6","max_tokens":1024,"messages":[{"role":"user","content":"Hello"}]}'
```

## Anthropic API vs. Cursor Cloud Agents

> [!IMPORTANT]
> The Anthropic API and the Cursor Cloud Agents are **different execution contexts** that happen to use the same underlying Claude models.

### Cursor Cloud Agents (This Session)

- **What:** The agent running inside Cursor IDE (this conversation).
- **Authentication:** Handled by Cursor Pro+ subscription (uses Cursor's pooled API keys, or your own key via Cursor Settings).
- **Capabilities:** Full IDE access (file read/write, shell, browser, MCP tools, sub-agents).
- **Limitations:** Cannot make outbound HTTP calls to arbitrary APIs directly. Must use Shell (`curl`, `python`) or MCP tools for external communication.
- **Model:** Determined by Cursor settings (currently claude-4.6-opus-high).
- **Cost:** Included in Cursor Pro+ subscription (with rate limits).

### Direct Anthropic API (via `ANTHROPIC_API_KEY`)

- **What:** A separate, programmatic channel to Claude models.
- **Authentication:** Your own `ANTHROPIC_API_KEY` from `console.anthropic.com`.
- **Capabilities:** Pure text generation. No IDE access, no file system, no tools.
- **Limitations:** Stateless. Each call is independent. No persistent memory across calls.
- **Model:** Specified per call (`claude-opus-4-6`, `claude-sonnet-4-6`, etc.).
- **Cost:** Pay-per-use (billed to your Anthropic account).

### How They Fit Together in MTHO_CORE

```
┌─────────────────────────────────────────────────┐
│ Cursor IDE (4D_RESONATOR / CDR-INTERFACE)       │
│                                                  │
│  ┌──────────────────────────────────────┐       │
│  │ Cloud Agent (Claude Opus 4.6)        │       │
│  │ - IDE tools, file access, shell      │       │
│  │ - Orchestrates, delegates, executes  │       │
│  └──────┬───────────────────────────────┘       │
│         │ (via Shell: python / curl)            │
│         ▼                                        │
│  ┌──────────────────────────────────────┐       │
│  │ Direct API Call (ANTHROPIC_API_KEY)  │       │
│  │ - Stateless reasoning engine         │       │
│  │ - Independent perspective            │       │
│  │ - Cross-validation / second opinion  │       │
│  └──────────────────────────────────────┘       │
│         │                                        │
│         ▼                                        │
│  ┌──────────────────────────────────────┐       │
│  │ Direct API Call (GEMINI_API_KEY)     │       │
│  │ - OMEGA_ATTRACTOR / G-MTHO (Gemini-Bridge) │       │
│  │ - Different model family = true      │       │
│  │   cross-validation                   │       │
│  └──────────────────────────────────────┘       │
└─────────────────────────────────────────────────┘
```

### Use Cases for Direct API Calls

1. **Cross-Validation:** Send the same prompt to both Gemini and Claude APIs. Compare results. If they converge, confidence is high.
2. **G-MTHO Bridge:** If the Gemini API channel is blocked (rate limits, SDK issues), use the Anthropic API as a fallback communication channel to maintain system dialogue.
3. **Audit Scripts:** Existing scripts (`run_claude_audit_once.py`, `run_claude_audit_compare.py`) already use the direct API for independent code reviews.
4. **OpenClaw Integration:** The VPS OpenClaw instance uses `ANTHROPIC_API_KEY` for its Claude provider configuration.

## Error Handling

Always implement graceful error handling with model fallbacks:

```python
from anthropic import Anthropic, APIError, RateLimitError

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MODELS = ["claude-sonnet-4-6", "claude-sonnet-4-5"]
last_error = None

for model in MODELS:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        print(response.content[0].text)
        break
    except RateLimitError:
        print(f"Rate limit for {model}, trying next...")
        continue
    except APIError as e:
        last_error = e
        print(f"API error for {model}: {e}")
        continue
else:
    raise RuntimeError(f"All models failed. Last error: {last_error}")
```

## Reference Documentation

- **API Overview:** `https://platform.claude.com/docs/en/api/overview`
- **Messages API:** `https://platform.claude.com/docs/en/api/messages`
- **Models List:** `https://platform.claude.com/docs/en/api/models-list`
- **Client SDKs:** `https://platform.claude.com/docs/en/api/client-sdks`
- **Rate Limits:** `https://platform.claude.com/docs/en/api/rate-limits`
