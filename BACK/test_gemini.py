
import asyncio
import httpx

from app.config import get_settings


async def test():
    settings = get_settings()

    url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    headers = {
        "x-goog-api-key": settings.gemini_api_key,
    }

    payload = {
        "model": settings.gemini_model,
        "input": "Reply with Hello",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

            print("HTTP status:", response.status_code)
            print("Response:", response.text[:1500])

    except httpx.RequestError as error:
        print("Connection error:", type(error).__name__)
        print("Details:", str(error))


if __name__ == "__main__":
    asyncio.run(test())
