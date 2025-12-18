"""Provider factory."""
from typing import Optional
from app.config import settings
from app.providers.base import TranscriptionProvider
from app.providers.klang import KlangProvider
from app.providers.mistral import MistralProvider
from app.providers.openai_provider import OpenAIProvider


def get_transcription_provider(
    provider_name: Optional[str] = None,
) -> TranscriptionProvider:
    """
    Get transcription provider by name.
    
    Args:
        provider_name: Provider name (klang, mistral, openai).
                      Defaults to DEFAULT_TRANSCRIPTION_PROVIDER from config.
    
    Returns:
        TranscriptionProvider instance
    
    Raises:
        ValueError: If provider not found or not configured
    """
    name = provider_name or settings.default_transcription_provider
    
    providers = {
        "klang": KlangProvider,
        "mistral": MistralProvider,
        "openai": OpenAIProvider,
    }
    
    provider_class = providers.get(name.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown transcription provider: {name}. "
            f"Available: {', '.join(providers.keys())}"
        )
    
    try:
        return provider_class()
    except ValueError as e:
        raise ValueError(f"Provider {name} not configured: {e}") from e





