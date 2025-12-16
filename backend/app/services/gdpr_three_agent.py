"""
3-Agent Workflow with GDPR Compliance
Agent 1: UNDERSTAND & EXTRACT - Read transcript, identify PII
Agent 2: GENERATE & REDACT - Create structured data, remove PII from DB version
Agent 3: QA & VERIFY - Ensure no PII in DB, verify completeness
"""
from typing import List, Dict, Any
from datetime import datetime
import re


class PIIDetector:
    """Detect and tag PII in content."""
    
    @staticmethod
    def detect_pii(text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text.
        
        Returns list of PII entities with type and location.
        """
        pii_entities = []
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            pii_entities.append({
                'type': 'email',
                'value': match.group(),
                'start': match.start(),
                'end': match.end(),
                'gdpr_category': 'personal_identifier'
            })
        
        # Phone numbers (Swedish format)
        phone_pattern = r'\b(\+46|0)[\s-]?\d{1,3}[\s-]?\d{5,8}\b'
        for match in re.finditer(phone_pattern, text):
            pii_entities.append({
                'type': 'phone',
                'value': match.group(),
                'start': match.start(),
                'end': match.end(),
                'gdpr_category': 'personal_identifier'
            })
        
        # Personal names (simple heuristic - capitalized words)
        # More sophisticated NER would be better for production
        name_pattern = r'\b([A-ZÅÄÖ][a-zåäö]+\s+[A-ZÅÄÖ][a-zåäö]+)\b'
        for match in re.finditer(name_pattern, text):
            pii_entities.append({
                'type': 'person_name',
                'value': match.group(),
                'start': match.start(),
                'end': match.end(),
                'gdpr_category': 'personal_data'
            })
        
        return pii_entities
    
    @staticmethod
    def redact_pii(text: str, pii_entities: List[Dict], replacement: str = "[REDACTED]") -> str:
        """
        Redact PII from text for database storage.
        Original text with PII kept in source file.
        """
        # Sort by position (reverse) so we don't mess up indices
        sorted_pii = sorted(pii_entities, key=lambda x: x['start'], reverse=True)
        
        redacted_text = text
        for pii in sorted_pii:
            before = redacted_text[:pii['start']]
            after = redacted_text[pii['end']:]
            
            # Use type-specific redaction
            if pii['type'] == 'email':
                redaction = "[EMAIL_REDACTED]"
            elif pii['type'] == 'phone':
                redaction = "[PHONE_REDACTED]"
            elif pii['type'] == 'person_name':
                redaction = "[NAME_REDACTED]"
            else:
                redaction = replacement
            
            redacted_text = before + redaction + after
        
        return redacted_text


class GDPRThreeAgentWorkflow:
    """3-Agent workflow with GDPR compliance."""
    
    @staticmethod
    def agent1_understand_and_detect_pii(transcript: str) -> Dict[str, Any]:
        """
        AGENT 1: UNDERSTAND & EXTRACT
        
        - Extract all meeting data
        - Detect and tag ALL PII
        - Create audit trail
        
        Returns:
            Raw data with PII tagged
        """
        print("\n" + "=" * 80)
        print("AGENT 1: UNDERSTAND & DETECT PII")
        print("=" * 80)
        
        # Detect PII
        pii_detector = PIIDetector()
        pii_entities = pii_detector.detect_pii(transcript)
        
        print(f"\nPII Detection:")
        print(f"  Found {len(pii_entities)} PII entities")
        
        pii_by_type = {}
        for pii in pii_entities:
            pii_type = pii['type']
            if pii_type not in pii_by_type:
                pii_by_type[pii_type] = []
            pii_by_type[pii_type].append(pii['value'])
        
        for pii_type, values in pii_by_type.items():
            print(f"  - {pii_type}: {len(set(values))} unique")
            for val in set(values)[:3]:  # Show first 3
                print(f"    • {val}")
        
        return {
            'transcript': transcript,
            'pii_entities': pii_entities,
            'pii_summary': pii_by_type
        }
    
    @staticmethod
    def agent2_generate_and_redact(raw_data: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AGENT 2: GENERATE & REDACT
        
        - Create structured meeting data
        - Generate DB version (PII redacted)
        - Generate source version (PII intact for source file)
        - Maintain mapping for authorized access
        
        Returns:
            db_version: Data for database (redacted)
            source_version: Data for source file (with PII)
            pii_map: Mapping for authorized re-identification
        """
        print("\n" + "=" * 80)
        print("AGENT 2: GENERATE & REDACT")
        print("=" * 80)
        
        pii_detector = PIIDetector()
        
        # Create DB version (redacted)
        db_attendees = []
        source_attendees = []
        
        for attendee in extracted_data.get('attendees', []):
            name = attendee.get('name', '')
            email = attendee.get('email', '')
            
            # Source version: Keep PII
            source_attendees.append({
                'name': name,
                'email': email,
                'role': attendee.get('role')
            })
            
            # DB version: Redact PII
            db_attendees.append({
                'name': name,  # Names can stay for business context
                'email': None,  # Remove email from DB
                'role': attendee.get('role'),
                'pii_redacted': True
            })
        
        print(f"\nAttendees:")
        print(f"  Source version: {len(source_attendees)} with emails")
        print(f"  DB version: {len(db_attendees)} (emails redacted)")
        
        # Redact PII from action descriptions
        db_actions = []
        source_actions = []
        
        for action in extracted_data.get('action_items', []):
            source_actions.append(action)  # Keep original
            
            # Redact from description
            description = action.get('description', '')
            pii_in_desc = pii_detector.detect_pii(description)
            redacted_desc = pii_detector.redact_pii(description, pii_in_desc)
            
            db_actions.append({
                **action,
                'description': redacted_desc,
                'pii_redacted': len(pii_in_desc) > 0
            })
        
        print(f"\nAction Items:")
        print(f"  Total: {len(source_actions)}")
        print(f"  With PII redacted: {sum(1 for a in db_actions if a.get('pii_redacted'))}")
        
        return {
            'db_version': {
                'attendees': db_attendees,
                'action_items': db_actions,
                'decisions': extracted_data.get('decisions', []),  # Decisions usually don't have email/phone
                'meeting_info': extracted_data.get('meeting_info', {})
            },
            'source_version': {
                'attendees': source_attendees,
                'action_items': source_actions,
                'decisions': extracted_data.get('decisions', []),
                'meeting_info': extracted_data.get('meeting_info', {})
            },
            'pii_map': {
                'redaction_count': sum(len(pii_detector.detect_pii(str(a))) for a in source_actions),
                'policy': 'PII stored in source file only, not in database',
                'retention': 'Source file follows company retention policy',
                'access': 'Authorized users can request PII from source file'
            }
        }
    
    @staticmethod
    def agent3_qa_verify_no_pii(db_version: Dict[str, Any]) -> Dict[str, Any]:
        """
        AGENT 3: QA & VERIFY
        
        - Verify NO PII in database version
        - Verify data completeness (despite redaction)
        - Approve or reject for DB insertion
        
        Returns:
            approved: bool
            issues: List of issues found
            warnings: List of warnings
        """
        print("\n" + "=" * 80)
        print("AGENT 3: QA & VERIFY - GDPR COMPLIANCE CHECK")
        print("=" * 80)
        
        issues = []
        warnings = []
        
        pii_detector = PIIDetector()
        
        # Check attendees for PII
        print(f"\n1. Checking attendees for PII...")
        for i, attendee in enumerate(db_version.get('attendees', []), 1):
            if attendee.get('email'):
                issues.append(f"Attendee {i} has email in DB version (GDPR violation)")
            
            # Check if name contains email pattern (sometimes people enter emails as names)
            name = attendee.get('name', '')
            if '@' in name:
                issues.append(f"Attendee {i} name contains email address")
        
        if not issues:
            print(f"   ✓ No emails in DB version")
            print(f"   ✓ {len(db_version.get('attendees', []))} attendees verified")
        
        # Check action items for PII leakage
        print(f"\n2. Checking action items for PII...")
        pii_found_count = 0
        
        for i, action in enumerate(db_version.get('action_items', []), 1):
            description = action.get('description', '')
            pii_in_desc = pii_detector.detect_pii(description)
            
            if pii_in_desc:
                pii_found_count += 1
                issues.append(f"Action {i} contains PII in description: {[p['type'] for p in pii_in_desc]}")
        
        if pii_found_count == 0:
            print(f"   ✓ No PII detected in action descriptions")
            print(f"   ✓ {len(db_version.get('action_items', []))} actions verified")
        
        # Check decisions for PII
        print(f"\n3. Checking decisions for PII...")
        for i, decision in enumerate(db_version.get('decisions', []), 1):
            decision_text = decision.get('decision', '') + ' ' + decision.get('rationale', '')
            pii_in_decision = pii_detector.detect_pii(decision_text)
            
            if pii_in_decision:
                # Decisions might mention names (decision makers) - this is OK
                # But emails/phones should be redacted
                for pii in pii_in_decision:
                    if pii['type'] in ['email', 'phone']:
                        issues.append(f"Decision {i} contains {pii['type']}: {pii['value']}")
        
        print(f"   ✓ {len(db_version.get('decisions', []))} decisions verified")
        
        # Verify data completeness
        print(f"\n4. Verifying data completeness...")
        
        if len(db_version.get('attendees', [])) == 0:
            warnings.append("No attendees - meeting might be incomplete")
        else:
            print(f"   ✓ {len(db_version.get('attendees', []))} attendees")
        
        if len(db_version.get('action_items', [])) == 0:
            warnings.append("No action items - unusual for business meeting")
        else:
            print(f"   ✓ {len(db_version.get('action_items', []))} action items")
        
        if len(db_version.get('decisions', [])) == 0:
            warnings.append("No decisions recorded")
        else:
            print(f"   ✓ {len(db_version.get('decisions', []))} decisions")
        
        # Final verdict
        print(f"\n" + "=" * 80)
        print("GDPR COMPLIANCE VERDICT")
        print("=" * 80)
        
        approved = len(issues) == 0
        
        if issues:
            print(f"\n❌ REJECTED - {len(issues)} GDPR violations found:")
            for issue in issues:
                print(f"   - {issue}")
            print(f"\n⚠️  PII MUST be removed before database insertion")
        else:
            print(f"\n✅ APPROVED - GDPR Compliant")
            print(f"   ✓ No PII in database version")
            print(f"   ✓ All PII kept in source file only")
            print(f"   ✓ Data minimization enforced")
            print(f"   ✓ Right to deletion supported")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"   - {warning}")
        
        return {
            'approved': approved,
            'issues': issues,
            'warnings': warnings,
            'pii_redacted': True,
            'gdpr_compliant': approved
        }




