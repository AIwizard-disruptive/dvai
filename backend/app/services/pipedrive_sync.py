"""
Pipedrive Sync Service
======================
Syncs pipeline stages and deals from Pipedrive to local database.
"""

from typing import List, Dict, Optional
from datetime import datetime
from supabase import Client
from app.integrations.pipedrive_client import PipedriveClient
from cryptography.fernet import Fernet
import os


class PipedriveSyncService:
    """Service for syncing Pipedrive data to local database."""
    
    def __init__(self, supabase: Client, encryption_key: str):
        """
        Initialize sync service.
        
        Args:
            supabase: Supabase client
            encryption_key: Encryption key for decrypting API tokens
        """
        self.supabase = supabase
        self.encryption_key = encryption_key
        self.fernet = Fernet(encryption_key.encode()) if encryption_key else None
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt an encrypted API token."""
        if not self.fernet or not encrypted_token:
            return ""
        try:
            return self.fernet.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            print(f"Error decrypting token: {e}")
            return ""
    
    async def sync_pipeline_stages(self, portfolio_company_id: str) -> Dict:
        """
        Sync pipeline stages from Pipedrive for a specific portfolio company.
        
        Args:
            portfolio_company_id: UUID of the portfolio company
        
        Returns:
            Dict with sync results
        """
        try:
            # Get portfolio company's Pipedrive integration
            integration = self.supabase.table('portfolio_company_integrations') \
                .select('*') \
                .eq('portfolio_company_id', portfolio_company_id) \
                .eq('integration_type', 'pipedrive') \
                .eq('is_active', True) \
                .single() \
                .execute()
            
            if not integration.data:
                return {
                    'success': False,
                    'error': 'No active Pipedrive integration found for this company'
                }
            
            # Decrypt API token
            encrypted_token = integration.data.get('api_token_encrypted', '')
            api_token = self.decrypt_token(encrypted_token)
            
            if not api_token:
                return {
                    'success': False,
                    'error': 'Could not decrypt Pipedrive API token'
                }
            
            # Initialize Pipedrive client
            company_domain = integration.data.get('company_domain', '')
            pipedrive = PipedriveClient(api_token=api_token, company_domain=company_domain)
            
            # Fetch stages from Pipedrive
            stages = await pipedrive.get_stages()
            
            if not stages:
                return {
                    'success': False,
                    'error': 'No stages returned from Pipedrive'
                }
            
            print(f"✅ Fetched {len(stages)} stages from Pipedrive")
            
            # Deactivate existing stages from Pipedrive (we'll reactivate synced ones)
            self.supabase.table('pipeline_stages') \
                .update({'is_active': False}) \
                .eq('portfolio_company_id', portfolio_company_id) \
                .eq('source_system', 'pipedrive') \
                .execute()
            
            synced_stages = []
            
            # Upsert each stage
            for stage in stages:
                stage_id = str(stage.get('id', ''))
                stage_name = stage.get('name', 'Untitled Stage')
                stage_order = stage.get('order_nr', 0)
                pipeline_id = stage.get('pipeline_id')
                
                # Map Pipedrive stage properties to our stage_type
                stage_type = self._determine_stage_type(stage_name, stage_order, len(stages))
                
                # Determine if this is a closed status
                is_closed = stage.get('rotten_flag', False) or 'won' in stage_name.lower() or 'lost' in stage_name.lower() or 'closed' in stage_name.lower()
                
                stage_data = {
                    'portfolio_company_id': portfolio_company_id,
                    'external_stage_id': stage_id,
                    'stage_name': stage_name,
                    'stage_order': stage_order,
                    'stage_type': stage_type,
                    'is_active': True,
                    'is_closed_status': is_closed,
                    'source_system': 'pipedrive',
                    'synced_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                }
                
                # Try to update existing, or insert new
                existing = self.supabase.table('pipeline_stages') \
                    .select('id') \
                    .eq('portfolio_company_id', portfolio_company_id) \
                    .eq('external_stage_id', stage_id) \
                    .eq('source_system', 'pipedrive') \
                    .execute()
                
                if existing.data:
                    # Update existing
                    self.supabase.table('pipeline_stages') \
                        .update(stage_data) \
                        .eq('id', existing.data[0]['id']) \
                        .execute()
                else:
                    # Insert new
                    self.supabase.table('pipeline_stages') \
                        .insert(stage_data) \
                        .execute()
                
                synced_stages.append(stage_name)
            
            # Update last sync time on integration
            self.supabase.table('portfolio_company_integrations') \
                .update({
                    'last_sync_at': datetime.utcnow().isoformat(),
                    'last_sync_status': 'success',
                    'sync_error': None
                }) \
                .eq('id', integration.data['id']) \
                .execute()
            
            return {
                'success': True,
                'stages_synced': len(synced_stages),
                'stage_names': synced_stages
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error syncing pipeline stages: {error_msg}")
            
            # Update integration sync status
            try:
                self.supabase.table('portfolio_company_integrations') \
                    .update({
                        'last_sync_at': datetime.utcnow().isoformat(),
                        'last_sync_status': 'failed',
                        'sync_error': error_msg
                    }) \
                    .eq('portfolio_company_id', portfolio_company_id) \
                    .eq('integration_type', 'pipedrive') \
                    .execute()
            except:
                pass
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def _determine_stage_type(self, stage_name: str, order: int, total_stages: int) -> str:
        """
        Determine standardized stage type from Pipedrive stage name.
        
        Returns one of: 'backlog', 'todo', 'in_progress', 'review', 'done', 'won', 'lost'
        """
        name_lower = stage_name.lower()
        
        # Check for explicit keywords
        if any(word in name_lower for word in ['backlog', 'pipeline', 'prospect']):
            return 'backlog'
        elif any(word in name_lower for word in ['qualified', 'new', 'incoming', 'lead']):
            return 'todo'
        elif any(word in name_lower for word in ['contact', 'meeting', 'demo', 'proposal', 'negotiation']):
            return 'in_progress'
        elif any(word in name_lower for word in ['review', 'decision', 'final']):
            return 'review'
        elif 'won' in name_lower or 'closed won' in name_lower or 'success' in name_lower:
            return 'won'
        elif 'lost' in name_lower or 'closed lost' in name_lower or 'rejected' in name_lower:
            return 'lost'
        elif 'done' in name_lower or 'complete' in name_lower:
            return 'done'
        else:
            # Default based on position
            if order == 0:
                return 'backlog'
            elif order < total_stages * 0.3:
                return 'todo'
            elif order < total_stages * 0.7:
                return 'in_progress'
            else:
                return 'review'
    
    async def get_pipeline_stages(self, portfolio_company_id: str) -> List[Dict]:
        """
        Get pipeline stages for a portfolio company.
        
        Args:
            portfolio_company_id: UUID of the portfolio company
        
        Returns:
            List of pipeline stages ordered by stage_order
        """
        result = self.supabase.table('pipeline_stages') \
            .select('*') \
            .eq('portfolio_company_id', portfolio_company_id) \
            .eq('is_active', True) \
            .order('stage_order') \
            .execute()
        
        return result.data if result.data else []
