"""OpenAI transcription provider."""
import tempfile
from typing import Optional
import httpx
from openai import AsyncOpenAI
from app.config import settings
from app.providers.base import (
    TranscriptionProvider,
    TranscriptionResult,
    TranscriptionSegment,
)


class OpenAIProvider(TranscriptionProvider):
    """OpenAI Whisper transcription provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    @property
    def name(self) -> str:
        return "openai"
    
    async def transcribe(
        self,
        file_url: str,
        language_hint: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio using OpenAI Whisper API.
        
        Note: OpenAI requires file upload, so we download and re-upload.
        """
        # Download audio file
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url, timeout=300.0)
            response.raise_for_status()
            audio_data = response.content
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_file.write(audio_data)
            tmp_file_path = tmp_file.name
        
        try:
            # Transcribe with timestamps
            with open(tmp_file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    language=language_hint,
                )
            
            # Parse segments
            segments = []
            if hasattr(transcription, "segments") and transcription.segments:
                for seg in transcription.segments:
                    segments.append(
                        TranscriptionSegment(
                            start=seg.get("start", 0.0),
                            end=seg.get("end", 0.0),
                            text=seg.get("text", ""),
                            speaker=None,  # OpenAI doesn't provide diarization
                            confidence=seg.get("avg_logprob"),
                        )
                    )
            else:
                # Fallback if no segments
                segments.append(
                    TranscriptionSegment(
                        start=0.0,
                        end=0.0,
                        text=transcription.text,
                        speaker=None,
                        confidence=None,
                    )
                )
            
            return TranscriptionResult(
                language=getattr(transcription, "language", language_hint or "en"),
                segments=segments,
                duration=getattr(transcription, "duration", None),
                model="whisper-1",
            )
        
        finally:
            # Clean up temp file
            import os
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)





