#!/usr/bin/env python3
"""
Reformattera alla Google Docs:
- Ta bort metadata-header
- Konvertera Markdown till riktig Google Docs-formatering
- Proper bold, italic, headings
"""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

def markdown_to_html(text):
    """Convert Markdown to HTML for Google Docs."""
    
    # Remove metadata section at top
    text = re.sub(r'═+\nDOKUMENT METADATA\n═+.*?═+\n\n', '', text, flags=re.DOTALL)
    
    # Convert headings
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Convert bold and italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert lists
    text = re.sub(r'^\s*- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\g<0></ul>\n', text)
    
    # Convert numbered lists
    text = re.sub(r'^\s*\d+\. (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    
    # Convert paragraphs (lines not already tagged)
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line and not any(tag in line for tag in ['<h', '<li', '<ul', '</ul', '<strong', '<em']):
            if not line.startswith('<'):
                formatted_lines.append(f'<p>{line}</p>')
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    html = '\n'.join(formatted_lines)
    
    # Wrap in HTML document
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-bottom: 2px solid #95a5a6; padding-bottom: 5px; }}
        h3 {{ color: #555; margin-top: 20px; }}
        strong {{ font-weight: bold; }}
        em {{ font-style: italic; }}
        ul, ol {{ margin-left: 20px; }}
        li {{ margin-bottom: 8px; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
    
    return html_doc


def reformat_document(drive_service, doc_id, doc_name, parent_id):
    """Reformat a single document by creating new formatted version."""
    
    try:
        # Export current content as plain text
        content = drive_service.files().export(fileId=doc_id, mimeType='text/plain').execute()
        text_content = content.decode('utf-8')
        
        # Convert to HTML
        html_content = markdown_to_html(text_content)
        
        # Create new document name (add _formatted to avoid conflicts)
        new_name = f"{doc_name}_NEW"
        
        # Create new document with HTML content
        file_metadata = {
            'name': new_name,
            'parents': [parent_id],
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        media = MediaInMemoryUpload(
            html_content.encode('utf-8'),
            mimetype='text/html',
            resumable=True
        )
        
        new_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        # Delete old document
        try:
            drive_service.files().delete(fileId=doc_id).execute()
        except:
            pass  # If delete fails, keep both
        
        # Rename new document to original name
        drive_service.files().update(
            fileId=new_file['id'],
            body={'name': doc_name}
        ).execute()
        
        return True, new_file['webViewLink']
        
    except Exception as e:
        return False, str(e)


def main():
    """Main function to reformat all documents."""
    
    print("\n" + "="*80)
    print("🎨 REFORMATTING ALL DOCUMENTS")
    print("="*80)
    
    # Load credentials
    with open('/tmp/google_credentials.json') as f:
        creds_data = json.load(f)
    
    creds = Credentials(
        token=creds_data['access_token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret'],
        scopes=creds_data['scopes']
    )
    
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Get all Google Docs in the DV Dokumentation folder
    root_folder_id = '1kqoauSMDzr5c6QEAJum1-QY6HIsBnkCQ'
    
    print("\n📄 Finding all documents...")
    
    # Get all subfolders
    results = drive_service.files().list(
        q=f"'{root_folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields='files(id, name)',
        pageSize=100
    ).execute()
    
    folders = results.get('files', [])
    
    total_docs = 0
    success_count = 0
    failed_count = 0
    
    for folder in folders:
        print(f"\n📁 {folder['name']}")
        
        # Get all documents in folder (not subfolders, just direct docs)
        docs_result = drive_service.files().list(
            q=f"'{folder['id']}' in parents and mimeType='application/vnd.google-apps.document'",
            fields='files(id, name)',
            pageSize=100
        ).execute()
        
        docs = docs_result.get('files', [])
        
        # Also check subfolders
        subfolder_result = drive_service.files().list(
            q=f"'{folder['id']}' in parents and mimeType='application/vnd.google-apps.folder'",
            fields='files(id, name)',
            pageSize=100
        ).execute()
        
        subfolders = subfolder_result.get('files', [])
        
        for subfolder in subfolders:
            print(f"   📂 {subfolder['name']}")
            
            # Get documents in subfolder
            subdocs_result = drive_service.files().list(
                q=f"'{subfolder['id']}' in parents and mimeType='application/vnd.google-apps.document'",
                fields='files(id, name)',
                pageSize=100
            ).execute()
            
            subdocs = subdocs_result.get('files', [])
            
            for doc in subdocs:
                total_docs += 1
                print(f"      [{total_docs}] {doc['name']:<45}", end='', flush=True)
                
                success, result = reformat_document(drive_service, doc['id'], doc['name'], subfolder['id'])
                
                if success:
                    success_count += 1
                    print(" ✅")
                    # Small delay
                    import time
                    time.sleep(1)
                else:
                    failed_count += 1
                    print(f" ❌ {result[:20]}")
    
    print("\n" + "="*80)
    print("✅ REFORMATTING COMPLETE")
    print("="*80)
    print(f"\n📊 Results:")
    print(f"   ✓ Reformatted: {success_count}/{total_docs}")
    print(f"   ✗ Failed: {failed_count}")
    print(f"\n🔗 View: https://drive.google.com/drive/folders/{root_folder_id}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()

