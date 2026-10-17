from types import SimpleNamespace

from app.routers import assistant


def test_assistant_chat_returns_gemini_reply(client, monkeypatch):
    request_data = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "Hello from Gemini."}],
                    }
                ]
            }

    class FakeAsyncClient:
        def __init__(self, *, timeout):
            assert timeout == 30.0

        async def __aenter__(self):
            return self

        async def __aexit__(self, _exc_type, _exc_value, _traceback):
            assert _exc_type is None
            assert _exc_value is None
            assert _traceback is None
            return None

        async def post(self, url, *, headers, json):
            request_data.update(url=url, headers=headers, json=json)
            return FakeResponse()

    monkeypatch.setattr(
        assistant,
        "get_settings",
        lambda: SimpleNamespace(gemini_api_key="test-api-key", gemini_model="gemini-3.8-flash"),
    )
    monkeypatch.setattr(assistant.httpx, "AsyncClient", FakeAsyncClient)

    response = client.post("/api/assistant/chat", json={"message": "  Need help booking.  "})

    assert response.status_code == 200
    assert response.json() == {"reply": "Hello from Gemini."}
    assert request_data["url"] == assistant.GEMINI_INTERACTIONS_URL
    assert request_data["headers"] == {"x-goog-api-key": "test-api-key"}
    assert request_data["json"]["model"] == "gemini-3.8-flash"
    assert request_data["json"]["input"] == "Need help booking."


def test_assistant_chat_requires_gemini_api_key(client, monkeypatch):
    monkeypatch.setattr(
        assistant,
        "get_settings",
        lambda: SimpleNamespace(gemini_api_key=None, gemini_model="gemini-3.8-flash"),
    )

    response = client.post("/api/assistant/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert response.json()["detail"] == "AI assistant is not configured"


def test_assistant_chat_rejects_blank_message(client):
    response = client.post("/api/assistant/chat", json={"message": "   "})

    assert response.status_code == 422
