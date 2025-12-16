"""
PII Detection Service
GDPR Compliance - Tag all personal identifiable information
"""
import re
import uuid
from typing import List, Dict, Tuple
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

class PIIEntity(BaseModel):
    """Detected PII entity"""
    entity_type: str  # "person_name", "email", "phone", "address", "company", "financial"
    text: str  # Actual PII value
    redacted_text: str  # "[NAME]", "[EMAIL]", etc.
    start_char: int
    end_char: int
    confidence: float
    detection_method: str  # "regex", "ner", "manual"

class PIIDetectionService:
    """
    Detect and tag ALL PII in text
    
    GDPR Requirements:
    - Detect: names, emails, phones, addresses, companies
    - Tag for redaction
    - Create training-safe versions
    - Support deletion workflows
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def detect_pii(self, text: str) -> List[PIIEntity]:
        """
        Detect all PII in text
        
        Uses multiple methods:
        1. Regex for structured data (email, phone)
        2. NER for named entities (would use spaCy/transformers)
        3. Pattern matching for addresses
        """
        pii_entities = []
        
        # 1. Email detection (regex)
        pii_entities.extend(self._detect_emails(text))
        
        # 2. Phone number detection (regex)
        pii_entities.extend(self._detect_phones(text))
        
        # 3. Named entities (simplified - would use NER model)
        pii_entities.extend(self._detect_names(text))
        
        # 4. Company names (would use NER)
        pii_entities.extend(self._detect_companies(text))
        
        # 5. Addresses (pattern matching)
        pii_entities.extend(self._detect_addresses(text))
        
        # 6. Financial data (credit cards, SSN, etc.)
        pii_entities.extend(self._detect_financial(text))
        
        # Sort by position
        pii_entities.sort(key=lambda x: x.start_char)
        
        return pii_entities
    
    def _detect_emails(self, text: str) -> List[PIIEntity]:
        """Detect email addresses"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = []
        
        for match in re.finditer(pattern, text):
            emails.append(PIIEntity(
                entity_type="email",
                text=match.group(),
                redacted_text="[EMAIL]",
                start_char=match.start(),
                end_char=match.end(),
                confidence=1.0,
                detection_method="regex"
            ))
        
        return emails
    
    def _detect_phones(self, text: str) -> List[PIIEntity]:
        """Detect phone numbers"""
        # US phone patterns
        patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # 123-456-7890
            r'\(\d{3}\)\s?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
            r'\+1\s?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'  # +1 123-456-7890
        ]
        
        phones = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                phones.append(PIIEntity(
                    entity_type="phone",
                    text=match.group(),
                    redacted_text="[PHONE]",
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.95,
                    detection_method="regex"
                ))
        
        return phones
    
    def _detect_names(self, text: str) -> List[PIIEntity]:
        """
        Detect person names using NER
        
        In production, use spaCy or Hugging Face transformers:
        - spaCy: en_core_web_trf for person names
        - Confidence scores from model
        - Context-aware detection
        """
        # Simplified pattern matching (would use NER model)
        # This is a placeholder - MUST use proper NER in production
        names = []
        
        # Pattern: capitalized words that might be names
        # This is NOT production-ready, just illustrative
        pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b'
        
        for match in re.finditer(pattern, text):
            # In production: verify with NER model
            names.append(PIIEntity(
                entity_type="person_name",
                text=match.group(),
                redacted_text="[NAME]",
                start_char=match.start(),
                end_char=match.end(),
                confidence=0.70,  # Lower confidence - needs NER
                detection_method="pattern"  # Should be "ner" in production
            ))
        
        return names
    
    def _detect_companies(self, text: str) -> List[PIIEntity]:
        """Detect company names"""
        # Would use NER model for ORG entities
        companies = []
        # Placeholder - needs proper NER
        return companies
    
    def _detect_addresses(self, text: str) -> List[PIIEntity]:
        """Detect physical addresses"""
        # Pattern for addresses (simplified)
        addresses = []
        # Would need proper address parsing library
        return addresses
    
    def _detect_financial(self, text: str) -> List[PIIEntity]:
        """Detect financial data (credit cards, SSN, etc.)"""
        financial = []
        
        # SSN pattern: XXX-XX-XXXX
        ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
        for match in re.finditer(ssn_pattern, text):
            financial.append(PIIEntity(
                entity_type="financial_ssn",
                text=match.group(),
                redacted_text="[SSN]",
                start_char=match.start(),
                end_char=match.end(),
                confidence=1.0,
                detection_method="regex"
            ))
        
        # Credit card pattern (simplified)
        cc_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
        for match in re.finditer(cc_pattern, text):
            financial.append(PIIEntity(
                entity_type="financial_cc",
                text=match.group(),
                redacted_text="[CREDIT_CARD]",
                start_char=match.start(),
                end_char=match.end(),
                confidence=0.90,
                detection_method="regex"
            ))
        
        return financial
    
    def redact_pii(
        self,
        text: str,
        pii_entities: List[PIIEntity]
    ) -> str:
        """
        Redact PII from text for training-safe version
        
        Replaces actual PII with tokens: [NAME], [EMAIL], [PHONE]
        Preserves structure for model training
        """
        # Sort by position in reverse to avoid offset issues
        sorted_pii = sorted(pii_entities, key=lambda x: x.start_char, reverse=True)
        
        redacted = text
        for pii in sorted_pii:
            redacted = (
                redacted[:pii.start_char] +
                pii.redacted_text +
                redacted[pii.end_char:]
            )
        
        return redacted
    
    async def store_pii_tags(
        self,
        org_id: uuid.UUID,
        normalized_transcript_id: uuid.UUID,
        segment_sequence: int,
        pii_entities: List[PIIEntity]
    ):
        """Store PII tags in database"""
        for pii in pii_entities:
            query = """
            INSERT INTO pii_tags (
                id, org_id, normalized_transcript_id, segment_sequence,
                entity_type, text, redacted_text,
                start_char, end_char, confidence, detection_method,
                can_store, can_train
            ) VALUES (
                :id, :org_id, :normalized_transcript_id, :segment_sequence,
                :entity_type, :text, :redacted_text,
                :start_char, :end_char, :confidence, :detection_method,
                :can_store, :can_train
            )
            """
            
            # GDPR: Determine if can store/train based on entity type
            can_train = pii.entity_type not in [
                "financial_ssn", "financial_cc", "health"
            ]
            
            await self.db.execute(query, {
                "id": uuid.uuid4(),
                "org_id": org_id,
                "normalized_transcript_id": normalized_transcript_id,
                "segment_sequence": segment_sequence,
                "entity_type": pii.entity_type,
                "text": pii.text,  # Encrypted at rest
                "redacted_text": pii.redacted_text,
                "start_char": pii.start_char,
                "end_char": pii.end_char,
                "confidence": pii.confidence,
                "detection_method": pii.detection_method,
                "can_store": True,
                "can_train": can_train
            })
        
        await self.db.commit()




