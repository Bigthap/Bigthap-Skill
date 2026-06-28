import asyncio
import httpx
import json
import os
import sys

API_KEY = os.getenv("MAXPLUS_API_KEY", "")
BASE = "https://api.maxplus-ai.cc"

if not API_KEY:
    print("❌ Please set MAXPLUS_API_KEY environment variable.")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

async def run_diagnostics():
    print(f"Testing MaxPlus AI Connection...")
    async with httpx.AsyncClient(timeout=10) as client:
        # Test 1: Account
        try:
            r = await client.get(f"{BASE}/v1/me", headers=HEADERS)
            if r.status_code == 200:
                data = r.json()
                print(f"  ✅ Account Key is Valid!")
                print(f"  💰 Credit Remaining: ${data.get('credit_usd'):.4f} USD")
            else:
                print(f"  ❌ Invalid API Key: {r.status_code} - {r.text}")
                return
        except Exception as e:
            print(f"  ❌ Network error on /v1/me: {e}")
            return

        # Test 2: GPT-5.4-mini (OpenAI endpoint)
        try:
            payload = {
                "model": "gpt-5.4-mini",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Ping"}]
            }
            r = await client.post(f"{BASE}/v1/chat/completions", headers=HEADERS, json=payload)
            if r.status_code == 200:
                print(f"  ✅ OpenAI completions endpoint working (gpt-5.4-mini)")
            else:
                print(f"  ❌ OpenAI completions failed: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"  ❌ Error on completions endpoint: {e}")

        # Test 3: Claude (Anthropic endpoint)
        try:
            payload = {
                "model": "claude-sonnet-4-6",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Ping"}]
            }
            r = await client.post(f"{BASE}/v1/messages", headers=HEADERS, json=payload)
            if r.status_code == 200:
                print(f"  ✅ Anthropic messages endpoint working (claude-sonnet-4-6)")
            else:
                print(f"  ❌ Anthropic messages failed: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"  ❌ Error on messages endpoint: {e}")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
