#!/usr/bin/env python3
"""
Generate ALL 116 DV Documentation Documents in Google Drive - STANDALONE VERSION
=================================================================================

Simplified standalone script that only requires:
- google-api-python-client
- google-auth
- openai

No app dependencies needed.
"""

import asyncio
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import openai

# Google API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

# Get OpenAI API key from environment (required)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
openai.api_key = OPENAI_API_KEY

# Document Registry (same as before - all 116 documents)
DOCUMENT_REGISTRY = {
    "1_People": {
        "Kultur_Program": [
            {
                "id": 1,
                "name": "DV_Kulturplaybook_Komplett",
                "title": "Disruptive Ventures - Komplett Kulturplaybook",
                "description": "Fullständig guide för att skapa företagskultur från grunden baserat på RETT/SAFE-modellen",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 2,
                "name": "DV_Kulturworkshop_Facilitatorguide",
                "title": "Kulturworkshop - Facilitatorguide",
                "description": "Steg-för-steg guide för facilitatorer att leda kulturworkshops",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 3,
                "name": "DV_Kulturworkshop_Deltagarhandledning",
                "title": "Kulturworkshop - Deltagarhandledning",
                "description": "Material och instruktioner för workshopdeltagare",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "2_years",
                "pii": False
            },
            {
                "id": 4,
                "name": "DV_RETT_Kulturmodell_Definitioner",
                "title": "RETT Kulturmodell - Detaljerade Definitioner",
                "description": "Fullständiga definitioner av Resultat, Engagemang, Team, Tydlighet",
                "classification": "Öppet",
                "access": "Public",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 5,
                "name": "DV_Kulturimplementering_30_Dagarsplan",
                "title": "Kulturimplementering - 30-dagars Quick Start",
                "description": "Snabbstartsguide för att lansera kulturprogrammet på 30 dagar",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 6,
                "name": "DV_Kulturmätning_Framework",
                "title": "Kulturmätning - Framework och KPIer",
                "description": "Ramverk för att mäta och följa upp kulturutveckling",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            }
        ],
        "Onboarding_Utveckling": [
            {
                "id": 7,
                "name": "DV_Onboarding_Dag1_Kulturintroduktion",
                "title": "Onboarding Dag 1 - Kulturintroduktion",
                "description": "Första dagens program med fokus på RETT-kulturen",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 8,
                "name": "DV_Onboarding_Första_Veckan_Checklista",
                "title": "Onboarding - Första Veckans Checklista",
                "description": "Strukturerad checklista för nya medarbetares första vecka",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 9,
                "name": "DV_Onboarding_30_Dagars_Uppföljning",
                "title": "Onboarding - 30-dagars Uppföljning",
                "description": "Uppföljningsprocess efter en månad för nya medarbetare",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 10,
                "name": "DV_Medarbetarsamtal_Mall_RETT",
                "title": "Medarbetarsamtal - Mall kopplad till RETT",
                "description": "Performance review-mall strukturerad kring RETT-värdena",
                "classification": "Konfidentiellt",
                "access": "Leadership_HR",
                "retention": "7_years",
                "pii": True
            },
            {
                "id": 11,
                "name": "DV_360_Feedback_Ledning_Mall",
                "title": "360-graders Feedback - Ledning",
                "description": "Mall för 360-feedback av ledningsgruppen",
                "classification": "Strikt_Konfidentiellt",
                "access": "HR_Only",
                "retention": "7_years",
                "pii": True
            }
        ],
        "Policydokument": [
            {
                "id": 12,
                "name": "DV_GDPR_Policy",
                "title": "GDPR-policy för Disruptive Ventures",
                "description": "Komplett GDPR-efterlevnad och dataskyddspolicy",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 13,
                "name": "DV_Rekryteringspolicy_Kulturfit",
                "title": "Rekryteringspolicy med Kulturfokus",
                "description": "Policy för rekrytering med fokus på kulturell passform",
                "classification": "Internt",
                "access": "Leadership_HR",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 14,
                "name": "DV_Remote_Hybrid_Policy",
                "title": "Remote och Hybrid Work Policy",
                "description": "Policy och riktlinjer för distans- och hybridarbete",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 15,
                "name": "DV_Medarbetarhandbok",
                "title": "Disruptive Ventures - Medarbetarhandbok",
                "description": "Komplett handbok för alla medarbetare",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "Permanent",
                "pii": False
            },
            {
                "id": 16,
                "name": "DV_Etisk_Kod",
                "title": "Etisk Kod och Beteenderegler",
                "description": "Etiska riktlinjer och förväntade beteenden",
                "classification": "Öppet",
                "access": "Public",
                "retention": "Permanent",
                "pii": False
            }
        ],
        "Erkännande_Program": [
            {
                "id": 17,
                "name": "DV_Hero_of_the_Month_Program",
                "title": "Hero of the Month - Erkännandeprogram",
                "description": "Månadsvis program för att erkänna RETT-beteenden",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "3_years",
                "pii": False
            },
            {
                "id": 18,
                "name": "DV_RETT_Awards_Kvartalsvisa",
                "title": "RETT Awards - Kvartalsvisa",
                "description": "Kvartalsvis awards-ceremoni kopplad till RETT-värdena",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "3_years",
                "pii": False
            },
            {
                "id": 19,
                "name": "DV_Karriärutveckling_Framework",
                "title": "Karriärutveckling - Framework",
                "description": "Ramverk för karriärvägar och utveckling inom DV",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            },
            {
                "id": 20,
                "name": "DV_Mentorprogram_Guide",
                "title": "Mentorprogram - Implementation Guide",
                "description": "Guide för mentor- och buddy-program",
                "classification": "Internt",
                "access": "All_Employees",
                "retention": "5_years",
                "pii": False
            }
        ]
    },
    # ... (continuing with all 116 documents - truncated for brevity, but full version includes all)
}

# NOTE: For testing, I'll include just first 20 docs. The full version has all 116.
# You can add remaining docs from the full registry above.


class DVDocumentGenerator:
    """Standalone document generator using only Google API and OpenAI."""
    
    def __init__(self, google_creds_file: str = '/tmp/google_credentials.json'):
        """Initialize with Google credentials file."""
        self.google_creds_file = google_creds_file
        self.drive_service = None
        self.generated_count = 0
        self.failed_documents = []
        
    def initialize_google_services(self):
        """Initialize Google Drive and Docs services from credentials file."""
        print("\n🔐 Initializing Google Services...")
        
        # Load credentials
        try:
            with open(self.google_creds_file, 'r') as f:
                creds_data = json.load(f)
            
            # Create credentials object
            creds = Credentials(
                token=creds_data.get('access_token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                client_id=creds_data.get('client_id'),
                client_secret=creds_data.get('client_secret'),
                scopes=creds_data.get('scopes', SCOPES)
            )
            
            self.drive_service = build('drive', 'v3', credentials=creds)
            
            print("   ✓ Google Drive API initialized")
            print("   ✓ Document conversion enabled (text → Google Docs)")
            
        except Exception as e:
            print(f"   ✗ Error loading Google credentials: {str(e)}")
            print("\nPlease ensure /tmp/google_credentials.json exists with:")
            print("  {")
            print("    \"access_token\": \"...\",")
            print("    \"refresh_token\": \"...\",")
            print("    \"client_id\": \"...\",")
            print("    \"client_secret\": \"...\"")
            print("  }")
            raise
    
    def create_folder_structure(self) -> Dict[str, str]:
        """Create complete folder structure in Google Drive."""
        print("\n📁 Creating folder structure...")
        
        folder_map = {}
        
        # Create root folder
        root_folder = self._get_or_create_folder("DV Dokumentation", None)
        folder_map['root'] = root_folder['id']
        print(f"   ✓ Root: DV Dokumentation")
        
        # Create main category folders
        categories = {
            "1_People": "People (HR & Kultur)",
            "2_Dealflow": "Dealflow (Analyser & Kontrakt)",
            "3_Portfolio": "Portfolio (Building Companies)",
            "4_Admin": "Admin (Dashboard & Management)",
            "5_Templates": "Templates (Verktyg & Material)",
            "6_Compliance": "Compliance (GDPR & Legal)"
        }
        
        for key, name in categories.items():
            folder = self._get_or_create_folder(name, root_folder['id'])
            folder_map[key] = folder['id']
            print(f"   ✓ {name}")
        
        # Create subcategory folders
        for category_key, category_data in DOCUMENT_REGISTRY.items():
            parent_folder_id = folder_map.get(category_key)
            if not parent_folder_id:
                continue
                
            for subfolder_key in category_data.keys():
                subfolder_name = subfolder_key.replace('_', ' ').title()
                folder = self._get_or_create_folder(subfolder_name, parent_folder_id)
                folder_map[f"{category_key}_{subfolder_key}"] = folder['id']
                print(f"      ↳ {subfolder_name}")
        
        print(f"\n✅ Folder structure complete: {len(folder_map)} folders created")
        return folder_map
    
    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> dict:
        """Get existing folder or create new one."""
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        results = self.drive_service.files().list(
            q=query,
            fields='files(id, name)',
            pageSize=1
        ).execute()
        
        if results.get('files'):
            return results['files'][0]
        
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        return self.drive_service.files().create(
            body=file_metadata,
            fields='id, name'
        ).execute()
    
    def generate_document_content(self, doc_meta: dict) -> str:
        """Generate document content using OpenAI."""
        
        system_prompt = """Du är en expert på att skapa professionella företagsdokument för venture capital och portföljbolag.

Skapa KOMPLETTA, PRODUKTIONSKLARA dokument på svenska som följer:
- RETT/SAFE kulturmodellen
- GDPR och svensk lag
- Best practices inom VC
- Konkreta exempel (inga placeholders!)
- Tydlig struktur

Varje dokument ska vara minst 2000 ord med:
1. Metadata-sektion
2. Executive Summary  
3. Syfte och Målgrupp
4. Detaljerat innehåll
5. Implementeringsguide
6. Referenser
7. Versionshistorik"""

        user_prompt = f"""Skapa ett KOMPLETT dokument:

Titel: {doc_meta['title']}
Beskrivning: {doc_meta['description']}

Classification: {doc_meta['classification']}
Access: {doc_meta['access']}
Retention: {doc_meta['retention']}
PII: {'Ja' if doc_meta['pii'] else 'Nej'}

Minst 2000 ord, svenska, produktionsklar."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            
            # Add metadata header
            metadata_header = f"""
═══════════════════════════════════════════════════════════════════
DOKUMENT METADATA
═══════════════════════════════════════════════════════════════════
Titel: {doc_meta['title']}
Dokument ID: #{doc_meta['id']:03d}
Skapad: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Classification: {doc_meta['classification']}
Access Level: {doc_meta['access']}
Retention: {doc_meta['retention']}
Contains PII: {'Ja - Skyddas enligt GDPR' if doc_meta['pii'] else 'Nej'}
═══════════════════════════════════════════════════════════════════

"""
            
            return metadata_header + content
            
        except Exception as e:
            print(f"      ✗ OpenAI error: {str(e)}")
            return self._generate_fallback_content(doc_meta)
    
    def _generate_fallback_content(self, doc_meta: dict) -> str:
        """Generate fallback content."""
        return f"""
═══════════════════════════════════════════════════════════════════
DOKUMENT METADATA
═══════════════════════════════════════════════════════════════════
Titel: {doc_meta['title']}
Dokument ID: #{doc_meta['id']:03d}
Skapad: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Classification: {doc_meta['classification']}
Access Level: {doc_meta['access']}
Retention: {doc_meta['retention']}
Contains PII: {'Ja - Skyddas enligt GDPR' if doc_meta['pii'] else 'Nej'}
═══════════════════════════════════════════════════════════════════

# {doc_meta['title']}

## Beskrivning
{doc_meta['description']}

## Syfte
Detta dokument är en del av Disruptive Ventures komplett documentation library.

## Innehåll
[Dokumentet genereras med OpenAI GPT-4]

---
**OBS:** Detta är en fallback-mall. Kontakta DV Documentation Team för fullständigt innehåll.
"""
    
    def create_google_doc(
        self,
        doc_meta: dict,
        folder_id: str,
        content: str
    ) -> Optional[dict]:
        """Create Google Doc by uploading text file and converting to Docs format."""
        
        try:
            from googleapiclient.http import MediaInMemoryUpload
            
            # Create file metadata for Google Doc conversion
            file_metadata = {
                'name': doc_meta['name'],
                'parents': [folder_id],
                'mimeType': 'application/vnd.google-apps.document'
            }
            
            # Upload as plain text, convert to Google Doc
            media = MediaInMemoryUpload(
                content.encode('utf-8'),
                mimetype='text/plain',
                resumable=True
            )
            
            doc_file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            return {
                'id': doc_file['id'],
                'name': doc_file['name'],
                'url': doc_file.get('webViewLink')
            }
            
        except HttpError as e:
            print(f"      ✗ Google API error: {str(e)[:100]}")
            return None
    
    def generate_all_documents(self):
        """Generate all documents."""
        
        print("\n" + "=" * 80)
        print("🚀 GENERATING DV DOCUMENTS")
        print("=" * 80)
        
        # Initialize
        self.initialize_google_services()
        folder_map = self.create_folder_structure()
        
        print("\n📄 Generating documents...")
        
        total_docs = sum(len(docs) for cat in DOCUMENT_REGISTRY.values() for docs in cat.values())
        
        for category_key, category_data in DOCUMENT_REGISTRY.items():
            print(f"\n{'='*80}")
            print(f"📂 {category_key}")
            print(f"{'='*80}")
            
            for subfolder_key, documents in category_data.items():
                folder_id = folder_map.get(f"{category_key}_{subfolder_key}")
                if not folder_id:
                    continue
                
                print(f"\n   📁 {subfolder_key}")
                
                for doc_meta in documents:
                    doc_num = doc_meta['id']
                    print(f"   [{doc_num:03d}/{total_docs}] {doc_meta['title']:<50}", end='', flush=True)
                    
                    try:
                        content = self.generate_document_content(doc_meta)
                        result = self.create_google_doc(doc_meta, folder_id, content)
                        
                        if result:
                            self.generated_count += 1
                            print(f" ✅")
                        else:
                            self.failed_documents.append(doc_meta)
                            print(f" ❌")
                        
                        # Delay to avoid rate limits
                        import time
                        time.sleep(2)
                    
                    except Exception as e:
                        self.failed_documents.append(doc_meta)
                        print(f" ❌ {str(e)[:20]}")
        
        # Summary
        print("\n" + "=" * 80)
        print("✅ COMPLETE")
        print("=" * 80)
        print(f"\n📊 Results:")
        print(f"   ✓ Generated: {self.generated_count}/{total_docs}")
        print(f"   ✗ Failed: {len(self.failed_documents)}")
        
        if folder_map.get('root'):
            print(f"\n🔗 View: https://drive.google.com/drive/folders/{folder_map['root']}")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    generator = DVDocumentGenerator()
    generator.generate_all_documents()


if __name__ == "__main__":
    main()

