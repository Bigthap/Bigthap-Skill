---
name: maxplus-ai
description: Detailed guide to configure, route, call, and handle limitations of the MaxPlus AI proxy service. Use when integrating MaxPlus API keys (ccsk-...), configuring custom OpenAI/Anthropic api_base endpoints, or debugging 503/429 errors from MaxPlus.
---

# MaxPlus AI Integration & Reference Guide

This skill provides a reusable integration guide for connecting any application to the **MaxPlus AI Pay-as-you-go API Proxy Gateway**. It details authentication, routing protocols, payload limits, and billing monitoring.

---

## 1. API Authentication

All requests to the MaxPlus AI Gateway must include an API key (a 64-character hex string prefixed with `ccsk-` e.g., `ccsk-[a-f0-9]{64}`).
Attach it in the request headers in one of the following formats:
- **Authorization Header**: `Authorization: Bearer ccsk-...` (Standard for OpenAI SDKs & Claude Code)
- **Anthropic-style Header**: `x-api-key: ccsk-...` (Standard for Anthropic SDKs)

---

## 2. API Routing & Protocol Architecture

MaxPlus AI proxies requests to multiple downstream LLM endpoints. It splits routing protocols based on the model family. You **MUST** dynamically route your requests to the correct endpoint and provider type:

### A. Routing Mapping
| Model Family | Target Endpoint | Protocol Provider |
|---|---|---|
| **Claude Models** (e.g., `claude-sonnet-4-6`, `haiku`) | `https://api.maxplus-ai.cc` | Anthropic Messages (`/v1/messages`) |
| **GPT / DeepSeek Models** (e.g., `gpt-5.5`, `gpt-5.4-mini`) | `https://api.maxplus-ai.cc/v1` | OpenAI Chat Completions (`/v1/chat/completions`) |

### B. Python Routing Logic Example
```python
def get_maxplus_config(model_name: str) -> tuple[str, str]:
    """
    Returns (api_base, custom_llm_provider) for routing MaxPlus requests.
    """
    model = model_name.strip().lower()
    if model.startswith("claude") or "haiku" in model:
        # Route to Anthropic protocol gateway
        return "https://api.maxplus-ai.cc", "anthropic"
    else:
        # Route to OpenAI protocol gateway
        return "https://api.maxplus-ai.cc/v1", "openai"
```

### C. SDK Integration Guidelines

#### OpenAI SDK Integration
```python
from openai import OpenAI

client = OpenAI(
    api_key="ccsk-...",
    base_url="https://api.maxplus-ai.cc/v1"
)

response = client.chat.completions.create(
    model="gpt-5.5",
    messages=[{"role": "user", "content": "Hello"}]
)
```

#### Anthropic SDK Integration
```python
from anthropic import Anthropic

client = Anthropic(
    api_key="ccsk-...",
    base_url="https://api.maxplus-ai.cc"
)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello"}]
)
```

#### LiteLLM Integration Quirk
LiteLLM automatically overrides custom `api_base` parameters if the model string includes a prefix (e.g. `openai/claude-sonnet-4-6` forces connection to official OpenAI servers, causing 401 Authentication errors).
- **The Fix**: Strip prefixes, use the raw model name (e.g., `gpt-5.5` or `claude-sonnet-4-6`), pass the resolved `api_base`, and explicitly set `custom_llm_provider = "openai" | "anthropic"` in the `completion_kwargs` payload.

---

## 3. Strict Limits & Constraints (Troubleshooting 503 & 429)

### A. The Multimodal 503 Timeout Limit
- **Symptom**: Sending raw high-res images (e.g. 5MB+ JPEG/PNG scans) results in `503 Service Unavailable (timeout)` or `502 Bad Gateway` timeouts.
- **Cause**: MaxPlus AI Gateway has strict HTTP body upload limits and connection timeouts on its load balancer.
- **The Solution (Payload Compression)**: Downscale and compress all image payloads before Base64 encoding. Use the following algorithm:
  1. Load raw image bytes using a library like PIL/Pillow.
  2. Resize the image so its maximum dimension (width or height) is **800px**.
  3. Save the image as **JPEG** with a compressed quality setting of **60**.
  4. Convert the compressed bytes to Base64 for the API payload.
  - *This reduces image payloads from megabytes down to ~50-80KB*, preventing HTTP timeouts.

### B. Rate Limits & Concurrency Spikes
- **Symptom**: Batch API calls lead to `429 Key spend cap reached` or transient `503` errors.
- **The Solution**:
  1. Restrict active concurrent calls using a semaphore (e.g., limit concurrency to 2 on heavy pipelines).
  2. Implement an auto-retry loop with exponential backoff for `503` and `429` status codes:
```python
import asyncio
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        # Call completion API
        response = call_api()
        break
    except Exception as e:
        err_str = str(e)
        if ("503" in err_str or "429" in err_str) and attempt < max_retries - 1:
            wait_time = 2.0 * (attempt + 1)  # Exponential backoff: 2s, 4s...
            await asyncio.sleep(wait_time)
            continue
        raise e
```

---

## 4. Programmatic Credit & Billing Tracking

You can monitor balance and usage programmatically without visiting the dashboard.

### A. Credit Balance Query (`GET /v1/me`)
Retrieves key state and absolute USD balance:
- Endpoint: `https://api.maxplus-ai.cc/v1/me`
- Key Fields:
  - `credit_usd`: Remaining account credit.
  - `key.used_usd`: Total cost spent by this key.
  - `key.limit_usd`: Daily or lifetime spend limit (`null` if unlimited).
  - `key.limit_used_usd`: Current period spend accumulator.

### B. Usage Statistics Query (`GET /v1/usage`)
Retrieves detailed token counters and cache utilization:
- Endpoint: `https://api.maxplus-ai.cc/v1/usage`
- Key Fields:
  - `totals.total_cost`: Total USD spent.
  - `totals.request_count`: Total API hits.
  - `totals.cache_read_tokens`: Input tokens retrieved from Claude prompt caching (cost-saving indicator).
