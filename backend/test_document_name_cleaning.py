"""
Test script for document name cleaning functionality.

This demonstrates how messy document names from various sources
(Google Calendar, file uploads, etc.) are cleaned into readable names.
"""

from app.services.document import DocumentService


def test_name_cleaning():
    """Test document name cleaning with real examples."""
    
    test_cases = [
        # Example 1: From screenshot - IK meeting with duplicates
        {
            "original": "IK_Disruptive_Ventures_möte_20231005_10-05__IK, Disruptive Ventures",
            "expected_pattern": "Meeting.*Oct.*2023"
        },
        # Example 2: From screenshot - Meeting with person names
        {
            "original": "Möte_2023-10-04_Serge_Guelnoji_Peo__2023-10-04__serge _ guelnoji _ peo",
            "expected_pattern": "Serge.*Oct.*2023"
        },
        # Example 3: From screenshot - Online partner meeting
        {
            "original": "Online_Partner_disruptiveventures_Gemini Enterprise SKU, Online Part",
            "expected_pattern": "Gemini Enterprise SKU"
        },
        # Example 4: From screenshot - Styrelsemöte (board meeting)
        {
            "original": "Pokalen_styrelsemöte_2023-11-15__2023-11-15__Styrelsen",
            "expected_pattern": "Pokalen.*Nov.*2023"
        },
        # Example 5: High-level plan document
        {
            "original": "High-Level Plan to AI-ify Disruptive Ventures",
            "expected_pattern": "High-Level Plan"
        },
        # Example 6: Team meeting
        {
            "original": "Veckomöte - Team Meeting (Marcus intro, AI-projekt, uppföljningar)",
            "expected_pattern": "Team Meeting"
        },
        # Additional test cases
        {
            "original": "2024-03-15_Acme_Corp_Pitch_Deck.pdf",
            "expected_pattern": "Acme.*Mar.*2024"
        },
        {
            "original": "Q4_Financial_Report_2023_Final_v2.xlsx",
            "expected_pattern": "Financial Report"
        },
    ]
    
    print("=" * 80)
    print("DOCUMENT NAME CLEANING TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        original = test_case["original"]
        cleaned = DocumentService.clean_document_name(original)
        
        print(f"Test {i}:")
        print(f"  Original: {original}")
        print(f"  Cleaned:  {cleaned}")
        
        # Also show full metadata
        metadata = DocumentService.parse_filename_metadata(original)
        if metadata:
            print(f"  Metadata: {metadata}")
        
        print()
        
        # Simple validation - check if it's different and shorter
        if len(cleaned) < len(original) and cleaned != original:
            passed += 1
            print("  ✓ PASS - Name was cleaned")
        else:
            failed += 1
            print("  ✗ FAIL - Name was not cleaned sufficiently")
        
        print("-" * 80)
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    print()
    
    # Show comparison table
    print("BEFORE vs AFTER COMPARISON:")
    print("=" * 80)
    print(f"{'ORIGINAL':<70} | {'CLEANED':<40}")
    print("-" * 80)
    for test_case in test_cases:
        original = test_case["original"][:67] + "..." if len(test_case["original"]) > 67 else test_case["original"]
        cleaned = DocumentService.clean_document_name(test_case["original"])
        cleaned_short = cleaned[:37] + "..." if len(cleaned) > 37 else cleaned
        print(f"{original:<70} | {cleaned_short:<40}")
    print("=" * 80)


def test_metadata_extraction():
    """Test metadata extraction from filenames."""
    
    test_filenames = [
        "Meeting_2024-03-15_Acme_Corp.pdf",
        "IK_Disruptive_Ventures_möte_20231005_10-05.ics",
        "Q1_2024_Financial_Report.xlsx",
        "Team_Standup_Notes_20240315.docx",
    ]
    
    print("\n" + "=" * 80)
    print("METADATA EXTRACTION TEST")
    print("=" * 80)
    print()
    
    for filename in test_filenames:
        metadata = DocumentService.parse_filename_metadata(filename)
        print(f"Filename: {filename}")
        print(f"Metadata:")
        for key, value in metadata.items():
            print(f"  - {key}: {value}")
        print()


if __name__ == "__main__":
    # Run tests
    test_name_cleaning()
    test_metadata_extraction()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nTo use in production:")
    print("1. When uploading a document, call DocumentService.parse_filename_metadata()")
    print("2. Extract 'cleaned_name' from metadata")
    print("3. Store it in the 'display_name' field in uploaded_documents table")
    print("4. Use display_name instead of filename in the UI")


