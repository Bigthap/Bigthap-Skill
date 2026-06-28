# MaxPlus AI Technical Reference

Detailed parameters, benchmarks, and API payload structures for MaxPlus AI.

## 1. Latency Profile (TTFT)
Based on real-world probes, the Time-to-First-Token (TTFT) averages are:
- `gpt-5.4-mini`: **~0.4s** (Very fast, highly economical)
- `gpt-5.5`: **~1.1s** (Flagship performance, moderate cost)
- `claude-sonnet-4-6`: **~1.1s** (High quality Thai translation)
- `claude-opus-4-6`: **~1.8s** (Premium reasoning/quality)

## 2. Concurrency & Rate Limits
- **Text Queries**: Supports up to **8+ parallel concurrent requests** without transient failures on text-only tasks.
- **Multimodal (Images)**: Concurrent requests with large image payloads (e.g. 500KB+ per image) will hit immediate **503 (timeout)** or **429 (spend cap exceeded)**.
- **Rule of Thumb**: Keep `MAX_CONCURRENT_LLM` set to `2` or lower when sending images, and always compress images to `< 100KB` prior to transmission.

## 3. Usage & Billing API (/v1/usage)
Get detailed quota usage via:
`GET https://api.maxplus-ai.cc/v1/usage`

### Response JSON Schema
```json
{
  "current_time": "ISO-8601 Timestamp",
  "monthly": [
    {
      "month": "YYYY-MM",
      "used_usd": 1.246,
      "limit_usd": 10.0,
      "details": {
        "model-name": {
          "used_usd": 0.0006,
          "input_tokens": 1599,
          "output_tokens": 58,
          "requests": 19
        }
      }
    }
  ],
  "daily": [
    {
      "date": "YYYY-MM-DD",
      "used_usd": 1.246,
      "requests": 25
    }
  ]
}
```
