"""Document processing service."""
import hashlib
from typing import Optional
from docx import Document
from docx.opc.exceptions import PackageNotFoundError


class DocumentService:
    """Service for processing document files."""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text content from Word document.
        
        Args:
            file_path: Path to .docx file
        
        Returns:
            Extracted text content
        
        Raises:
            ValueError: If file is not valid DOCX
        """
        try:
            doc = Document(file_path)
            
            # Extract paragraphs
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Extract tables
            table_texts = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        table_texts.append(row_text)
            
            # Combine
            all_text = "\n\n".join(paragraphs)
            if table_texts:
                all_text += "\n\n--- Tables ---\n\n" + "\n".join(table_texts)
            
            return all_text
        
        except PackageNotFoundError as e:
            raise ValueError(f"Invalid DOCX file: {e}") from e
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calculate SHA-256 hash of file.
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex-encoded SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read in 64KB chunks
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def parse_filename_metadata(filename: str) -> dict:
        """
        Parse metadata from filename using heuristics.
        
        Common patterns:
        - YYYY-MM-DD_Company_Type.ext
        - Meeting_with_Company_YYYY-MM-DD.ext
        
        Args:
            filename: File name
        
        Returns:
            Dict with parsed metadata
        """
        import re
        from datetime import datetime
        
        metadata = {}
        
        # Try to extract date (YYYY-MM-DD or YYYYMMDD)
        date_match = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", filename)
        if date_match:
            try:
                date_str = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
                metadata["date"] = date_str
            except ValueError:
                pass
        
        # Try to extract company name (simple heuristic: capitalized word)
        company_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", filename)
        if company_match:
            metadata["company"] = company_match.group(1)
        
        # Try to extract meeting type
        meeting_types = ["kickoff", "standup", "review", "planning", "retrospective", "demo"]
        filename_lower = filename.lower()
        for mtype in meeting_types:
            if mtype in filename_lower:
                metadata["type"] = mtype
                break
        
        return metadata



