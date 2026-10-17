
import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.schemas import AssistantChatRequest, AssistantChatResponse

router = APIRouter(prefix="/assistant", tags=["assistant"])
logger = logging.getLogger(__name__)

GEMINI_INTERACTIONS_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
)


def _extract_reply(payload: Any) -> str:
    if not isinstance(payload, dict):
        raise ValueError("Invalid Gemini response")

    if payload.get("status") != "completed":
        raise ValueError(
            f"Gemini interaction status: {payload.get('status')}"
        )

    steps = payload.get("steps")
    if not isinstance(steps, list):
        raise ValueError("Missing interaction steps")

    text_parts = [
        block["text"]
        for step in steps
        if isinstance(step, dict)
        and step.get("type") == "model_output"
        for block in (
            step.get("content")
            if isinstance(step.get("content"), list)
            else []
        )
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]

    reply = "".join(text_parts).strip()
    if not reply:
        raise ValueError("Gemini response did not contain text")

    return reply


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(data: AssistantChatRequest) -> AssistantChatResponse:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI assistant is not configured",
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GEMINI_INTERACTIONS_URL,
                headers={
                    "x-goog-api-key": settings.gemini_api_key,
                },
                json={
                    "model": settings.gemini_model,
                    "input": data.message,
                    "system_instruction": (
                        "You are a helpful assistant for a boat booking "
                        "service. Answer clearly and concisely. Do not "
                        "claim to know boat availability, booking status, "
                        "or prices unless that information is provided."
                    ),
                },
            )

            response.raise_for_status()
            reply = _extract_reply(response.json())

    except httpx.HTTPStatusError as error:
        logger.error(
            "Gemini returned HTTP %s: %s",
            error.response.status_code,
            error.response.text[:1000],
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI assistant request failed",
        ) from None

    except httpx.RequestError as error:
        logger.error(
            "Gemini connection error: %s: %s",
            type(error).__name__,
            str(error),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI assistant is temporarily unavailable",
        ) from None

    except ValueError:
        logger.exception("Gemini returned an invalid response")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI assistant returned an invalid response",
        ) from None

    return AssistantChatResponse(reply=reply)
