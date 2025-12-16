"""Simple upload endpoint that works without database connection."""
import uuid
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from pydantic import BaseModel

from app.config import settings
from supabase import create_client

router = APIRouter()


class UploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    message: str


@router.post("/artifacts/upload-simple", response_model=UploadResponse)
async def upload_simple(
    file: UploadFile = File(...),
    request: Request = None,
):
    """
    Simple upload that uses Supabase client instead of direct database.
    Works even when DATABASE_URL password is wrong.
    """
    try:
        # Get token from header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            # Allow upload without auth for testing
            user_id = "anonymous"
            org_id = str(uuid.uuid4())
        else:
            # Get user from token
            token = auth_header.replace("Bearer ", "")
            supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
            
            try:
                user_response = supabase.auth.get_user(token)
                if user_response.user:
                    user_id = user_response.user.id
                    
                    # Get user's org
                    org_response = supabase.table('org_memberships').select('org_id').eq('user_id', user_id).limit(1).execute()
                    if org_response.data:
                        org_id = org_response.data[0]['org_id']
                    else:
                        org_id = str(uuid.uuid4())
                else:
                    user_id = "anonymous"
                    org_id = str(uuid.uuid4())
            except Exception as e:
                print(f"Auth error: {e}")
                user_id = "anonymous"
                org_id = str(uuid.uuid4())
        
        # Determine file type
        filename = file.filename
        if filename.endswith((".docx", ".doc")):
            file_type = "docx"
        elif filename.endswith((".mp3", ".wav", ".m4a", ".ogg")):
            file_type = "audio"
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported: .docx, .doc, .mp3, .wav, .m4a, .ogg",
            )
        
        # Save file locally
        artifact_id = uuid.uuid4()
        os.makedirs(f"/tmp/artifacts/{artifact_id}", exist_ok=True)
        file_path = f"/tmp/artifacts/{artifact_id}/{filename}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        file_size = os.path.getsize(file_path)
        
        # Create artifact record in Supabase using service role
        try:
            admin_supabase = create_client(
                settings.supabase_url,
                settings.supabase_service_role_key
            )
            
            # First, ensure the org exists
            org_check = admin_supabase.table('orgs').select('id').eq('id', org_id).execute()
            if not org_check.data:
                # Create the org if it doesn't exist
                admin_supabase.table('orgs').insert({
                    'id': org_id,
                    'name': 'Default Organization',
                    'settings': {}
                }).execute()
                print(f"Created org: {org_id}")
            
            artifact_data = {
                'id': str(artifact_id),
                'org_id': org_id,
                'filename': filename,
                'file_type': file_type,
                'file_size': file_size,
                'storage_path': f"orgs/{org_id}/artifacts/{artifact_id}/{filename}",
                'transcription_status': 'pending'
            }
            
            admin_supabase.table('artifacts').insert(artifact_data).execute()
            
            # Trigger immediate processing for this specific file
            processing_status = "pending"
            try:
                # Process in background thread to not block response
                import threading
                def process_in_background():
                    import subprocess
                    file_path = f"/tmp/artifacts/{artifact_id}/{filename}"
                    
                    # Parse and save to database
                    result = subprocess.run([
                        sys.executable,
                        "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend/parse_and_save.py",
                        file_path
                    ], capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        print(f"✅ Parsed: {filename}")
                        
                        # Get meeting ID from artifact
                        artifact_check = admin_supabase.table('artifacts').select('meeting_id').eq('id', str(artifact_id)).execute()
                        if artifact_check.data and artifact_check.data[0].get('meeting_id'):
                            meeting_id = artifact_check.data[0]['meeting_id']
                            print(f"✅ Meeting created: {meeting_id[:8]}...")
                            
                            # Run enhanced distribution with meeting_id as argument
                            print(f"🚀 Generating Drive folder & Linear project...")
                            result = subprocess.run([
                                sys.executable,
                                "/Users/marcus/Library/Mobile Documents/com~apple~CloudDocs/Documents/Cursor-projects/Disruptive Ventures/DV Legacy/dv/backend/sync_with_drive_links.py",
                                meeting_id  # Pass as command line argument
                            ], capture_output=True, text=True, timeout=180)
                            
                            if 'ENHANCED SYNC COMPLETE' in result.stdout:
                                print(f"✅ Drive & Linear generated for {filename}!")
                            else:
                                print(f"⚠ Generation completed with warnings")
                                print(f"   {result.stdout[-200:]}")
                    else:
                        print(f"⚠ Parsing failed for {filename}: {result.stderr[:200]}")
                
                thread = threading.Thread(target=process_in_background)
                thread.daemon = True
                thread.start()
                processing_status = "processing"
                print(f"🚀 Auto-processing triggered for: {filename}")
            except Exception as e:
                print(f"Processing queue error: {e}")
                processing_status = "manual"
            
            return {
                "id": str(artifact_id),
                "filename": filename,
                "file_type": file_type,
                "status": "uploaded",
                "message": f"File uploaded successfully. Processing {processing_status}."
            }
            
        except Exception as e:
            # Even if database insert fails, file is saved
            print(f"Database insert error: {e}")
            return {
                "id": str(artifact_id),
                "filename": filename,
                "file_type": file_type,
                "status": "uploaded",
                "message": f"File saved locally. Database unavailable but file is ready for processing."
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

