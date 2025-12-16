"""Tests for transcription provider adapters."""
import pytest
from app.providers.base import TranscriptionProvider, TranscriptionResult
from app.providers.factory import get_transcription_provider


def test_transcription_provider_interface():
    """Test that all providers implement the interface."""
    from app.providers.klang import KlangProvider
    from app.providers.mistral import MistralProvider
    from app.providers.openai_provider import OpenAIProvider
    
    # All providers should inherit from TranscriptionProvider
    assert issubclass(KlangProvider, TranscriptionProvider)
    assert issubclass(MistralProvider, TranscriptionProvider)
    assert issubclass(OpenAIProvider, TranscriptionProvider)


def test_provider_names():
    """Test provider name properties."""
    from app.providers.klang import KlangProvider
    from app.providers.mistral import MistralProvider
    from app.providers.openai_provider import OpenAIProvider
    
    # Skip if API keys not configured
    try:
        klang = KlangProvider(api_key="test")
        assert klang.name == "klang"
    except ValueError:
        pytest.skip("Klang API key not configured")
    
    try:
        mistral = MistralProvider(api_key="test")
        assert mistral.name == "mistral"
    except ValueError:
        pytest.skip("Mistral API key not configured")
    
    try:
        openai = OpenAIProvider(api_key="test")
        assert openai.name == "openai"
    except ValueError:
        pytest.skip("OpenAI API key not configured")


def test_provider_factory():
    """Test provider factory."""
    # Should raise error for unknown provider
    with pytest.raises(ValueError, match="Unknown transcription provider"):
        get_transcription_provider("unknown")


@pytest.mark.asyncio
@pytest.mark.skip(reason="Requires API keys and mocking")
async def test_transcription_contract():
    """Test transcription result contract."""
    # This would test that all providers return consistent results
    # Requires mocking or test API keys
    pass




