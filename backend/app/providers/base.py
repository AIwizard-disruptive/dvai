"""Base transcription provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio."""
    start: float  # seconds
    end: float  # seconds
    text: str
    speaker: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    language: str
    segments: list[TranscriptionSegment]
    duration: Optional[float] = None
    model: Optional[str] = None


class TranscriptionProvider(ABC):
    """Abstract base class for transcription providers."""
    
    @abstractmethod
    async def transcribe(
        self,
        file_url: str,
        language_hint: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio file.
        
        Args:
            file_url: URL to audio file (can be signed URL)
            language_hint: Optional language hint (ISO 639-1 code)
        
        Returns:
            TranscriptionResult with segments
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    def supports_speaker_diarization(self) -> bool:
        """Whether provider supports speaker diarization."""
        return False




