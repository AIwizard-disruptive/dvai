"""Tests for DOCX extraction."""
import pytest
from app.services.document import DocumentService


def test_parse_filename_metadata():
    """Test filename metadata parsing."""
    doc_service = DocumentService()
    
    # Test date extraction
    metadata = doc_service.parse_filename_metadata("2025-12-10_Meeting_Notes.docx")
    assert "date" in metadata
    assert metadata["date"] == "2025-12-10"
    
    # Test company extraction
    metadata = doc_service.parse_filename_metadata("Acme_Corp_Meeting.docx")
    assert "company" in metadata
    
    # Test meeting type extraction
    metadata = doc_service.parse_filename_metadata("standup_2025-12-10.docx")
    assert metadata.get("type") == "standup"


def test_calculate_file_hash():
    """Test file hash calculation."""
    import tempfile
    import os
    
    doc_service = DocumentService()
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        temp_path = f.name
    
    try:
        hash1 = doc_service.calculate_file_hash(temp_path)
        assert len(hash1) == 64  # SHA-256 hex length
        
        # Same file should produce same hash
        hash2 = doc_service.calculate_file_hash(temp_path)
        assert hash1 == hash2
    finally:
        os.unlink(temp_path)


@pytest.mark.skip(reason="Requires actual DOCX file")
def test_extract_text_from_docx():
    """Test DOCX text extraction."""
    doc_service = DocumentService()
    
    # This would require a test DOCX file
    # text = doc_service.extract_text_from_docx("test.docx")
    # assert len(text) > 0
    pass



