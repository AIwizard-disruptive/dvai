"""
Whisperflow integration client for DV VC Operating System.
Transcription service for meetings across all 4 wheels.
"""
from typing import Dict, Optional, Any
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)


class WhisperflowClient:
    """
    Whisperflow client for audio transcription.
    
    Use cases:
    - PEOPLE: Candidate interviews → extract feedback
    - DEALFLOW: Deal meetings → capture discussion points
    - BUILDING: Portfolio CEO check-ins → track commitments
    - ADMIN: Internal partner meetings → document decisions
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.whisperflow.com/v1"):
        """
        Initialize Whisperflow client.
        
        Args:
            api_key: Whisperflow API key
            base_url: API base URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def transcribe_audio(
        self,
        audio_url: str = None,
        audio_file: bytes = None,
        language: str = "en",
        speaker_diarization: bool = True,
        timestamps: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Start audio transcription.
        
        Args:
            audio_url: URL to audio file
            audio_file: Audio file as bytes (alternative to audio_url)
            language: Language code ('en', 'sv', etc.)
            speaker_diarization: Enable speaker separation
            timestamps: Include timestamps in transcript
            **kwargs: Additional Whisperflow parameters
        
        Returns:
            Transcription job data with id and status
        
        Example:
            result = await whisperflow.transcribe_audio(
                audio_url="https://storage.com/interview.mp3",
                language="en",
                speaker_diarization=True
            )
            job_id = result['id']
        """
        try:
            async with httpx.AsyncClient() as client:
                if audio_url:
                    # Submit URL for transcription
                    payload = {
                        "audio_url": audio_url,
                        "language": language,
                        "speaker_diarization": speaker_diarization,
                        "timestamps": timestamps,
                        **kwargs
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/transcribe",
                        headers=self.headers,
                        json=payload
                    )
                
                elif audio_file:
                    # Upload file for transcription
                    files = {"file": audio_file}
                    data = {
                        "language": language,
                        "speaker_diarization": speaker_diarization,
                        "timestamps": timestamps,
                        **kwargs
                    }
                    
                    response = await client.post(
                        f"{self.base_url}/transcribe/upload",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        files=files,
                        data=data
                    )
                
                else:
                    raise ValueError("Either audio_url or audio_file must be provided")
                
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Whisperflow API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error transcribing audio with Whisperflow: {str(e)}")
            raise
    
    async def get_transcription_status(self, transcription_id: str) -> Dict[str, Any]:
        """
        Check transcription job status.
        
        Args:
            transcription_id: Job ID from transcribe_audio
        
        Returns:
            Status data with state ('queued', 'processing', 'completed', 'failed')
        
        Example:
            status = await whisperflow.get_transcription_status(job_id)
            if status['state'] == 'completed':
                result = await whisperflow.get_transcription_result(job_id)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transcribe/{transcription_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error getting transcription status: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error checking Whisperflow status: {str(e)}")
            raise
    
    async def get_transcription_result(self, transcription_id: str) -> Dict[str, Any]:
        """
        Get completed transcription result.
        
        Args:
            transcription_id: Job ID
        
        Returns:
            Full transcription data with text, speakers, timestamps
        
        Example:
            result = await whisperflow.get_transcription_result(job_id)
            transcript_text = result['text']
            speakers = result['speakers']  # [{speaker: "Speaker 1", text: "...", start: 0.0, end: 5.2}]
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transcribe/{transcription_id}/result",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error getting transcription result: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving Whisperflow result: {str(e)}")
            raise
    
    async def wait_for_transcription(
        self,
        transcription_id: str,
        max_wait_seconds: int = 600,
        poll_interval_seconds: int = 5
    ) -> Dict[str, Any]:
        """
        Wait for transcription to complete (blocking).
        
        Args:
            transcription_id: Job ID
            max_wait_seconds: Maximum time to wait
            poll_interval_seconds: How often to check status
        
        Returns:
            Completed transcription result
        
        Raises:
            TimeoutError: If transcription doesn't complete in time
            ValueError: If transcription fails
        
        Example:
            # Submit and wait
            job = await whisperflow.transcribe_audio(audio_url=url)
            result = await whisperflow.wait_for_transcription(job['id'])
            transcript = result['text']
        """
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            status = await self.get_transcription_status(transcription_id)
            state = status.get('state')
            
            if state == 'completed':
                return await self.get_transcription_result(transcription_id)
            
            elif state == 'failed':
                error_msg = status.get('error', 'Unknown error')
                raise ValueError(f"Transcription failed: {error_msg}")
            
            elif state in ('queued', 'processing'):
                await asyncio.sleep(poll_interval_seconds)
                elapsed += poll_interval_seconds
            
            else:
                raise ValueError(f"Unknown transcription state: {state}")
        
        raise TimeoutError(f"Transcription did not complete within {max_wait_seconds} seconds")
    
    async def transcribe_and_wait(
        self,
        audio_url: str = None,
        audio_file: bytes = None,
        language: str = "en",
        speaker_diarization: bool = True,
        max_wait_seconds: int = 600,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method: transcribe and wait for result in one call.
        
        Args:
            audio_url: URL to audio file
            audio_file: Audio file bytes
            language: Language code
            speaker_diarization: Enable speaker separation
            max_wait_seconds: Max time to wait
            **kwargs: Additional Whisperflow parameters
        
        Returns:
            Completed transcription result
        
        Example:
            # Simple one-call transcription
            result = await whisperflow.transcribe_and_wait(
                audio_url="https://storage.com/meeting.mp3",
                language="en"
            )
            print(result['text'])
        """
        job = await self.transcribe_audio(
            audio_url=audio_url,
            audio_file=audio_file,
            language=language,
            speaker_diarization=speaker_diarization,
            **kwargs
        )
        
        transcription_id = job['id']
        return await self.wait_for_transcription(transcription_id, max_wait_seconds)
    
    async def list_transcriptions(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List all transcription jobs.
        
        Args:
            limit: Max number of results
            offset: Pagination offset
        
        Returns:
            List of transcription jobs
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transcribe",
                    headers=self.headers,
                    params={"limit": limit, "offset": offset}
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error listing transcriptions: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error listing Whisperflow transcriptions: {str(e)}")
            raise
    
    async def delete_transcription(self, transcription_id: str) -> bool:
        """
        Delete a transcription job.
        
        Args:
            transcription_id: Job ID to delete
        
        Returns:
            True if deleted successfully
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/transcribe/{transcription_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return True
        
        except httpx.HTTPStatusError as e:
            logger.error(f"Error deleting transcription: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error deleting Whisperflow transcription: {str(e)}")
            raise


# Helper functions for converting Whisperflow output to DV format

def whisperflow_to_dv_format(whisperflow_result: Dict) -> Dict:
    """
    Convert Whisperflow transcript format to DV internal format.
    
    Args:
        whisperflow_result: Result from get_transcription_result()
    
    Returns:
        Standardized format matching existing transcript_chunks table
    
    Example:
        dv_format = whisperflow_to_dv_format(whisperflow_result)
        # Can now be saved to transcript_chunks table
    """
    chunks = []
    
    for idx, segment in enumerate(whisperflow_result.get('segments', [])):
        chunks.append({
            "chunk_index": idx,
            "speaker_label": segment.get('speaker', 'Unknown'),
            "text": segment.get('text', ''),
            "start_time": segment.get('start', 0.0),
            "end_time": segment.get('end', 0.0),
            "confidence": segment.get('confidence', 1.0)
        })
    
    return {
        "full_text": whisperflow_result.get('text', ''),
        "chunks": chunks,
        "language": whisperflow_result.get('language', 'unknown'),
        "duration": whisperflow_result.get('duration', 0),
        "provider": "whisperflow"
    }
