"""Mistral transcription provider."""
import httpx
from typing import Optional
from app.config import settings
from app.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class MistralProvider(TranscriptionProvider):
    """Mistral API transcription provider."""
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        self.api_key = api_key or settings.mistral_api_key
        self.api_url = api_url or settings.mistral_api_url
        
        if not self.api_key:
            raise ValueError("Mistral API key not configured")
    
    @property
    def name(self) -> str:
        return "mistral"
    
    async def transcribe(
        self,
        file_url: str,
        language_hint: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio using Mistral API.
        
        Note: This is a placeholder implementation.
        Adjust based on actual Mistral API documentation.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "audio_url": file_url,
        }
        
        if language_hint:
            payload["language"] = language_hint
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.api_url}/audio/transcriptions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        
        # Parse Mistral response format
        # Adjust based on actual API response structure
        segments = []
        for seg in data.get("segments", []):
            segments.append(
                TranscriptionSegment(
                    start=seg.get("start", 0.0),
                    end=seg.get("end", 0.0),
                    text=seg.get("text", ""),
                    speaker=seg.get("speaker"),
                    confidence=seg.get("confidence"),
                )
            )
        
        return TranscriptionResult(
            language=data.get("language", language_hint or "en"),
            segments=segments,
            duration=data.get("duration"),
            model=data.get("model", "mistral-whisper"),
        )



