#!/usr/bin/env python3
"""
Google Sheets Sync Manager
==========================
Handles synchronization between local database and Google Sheets with:
- Incremental sync capabilities
- Error handling and retry logic
- Sync status tracking
- Conflict resolution
- Performance optimization
"""

import logging
import json
import asyncio
import gspread
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from google.oauth2.service_account import Credentials
from gspread_formatting import format_cell_range, CellFormat, Color
import time
import os

from .local_database_manager import LocalDatabaseManager, get_local_db_manager

logger = logging.getLogger(__name__)

class SyncStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"

class SheetsyncManager:
    """Manages synchronization between local database and Google Sheets"""
    
    def __init__(self, service_account_path: str = None, spreadsheet_id: str = None):
        self.service_account_path = service_account_path or os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SPREADSHEET_ID')
        
        self.client = None
        self.spreadsheet = None
        self.sync_batch_size = 100
        self.retry_attempts = 3
        self.retry_delay = 2
        
        self._init_sheets_client()
        logger.info("✅ Sheets Sync Manager initialized")
    
    def _init_sheets_client(self):
        """Initialize Google Sheets client"""
        try:
            if not self.service_account_path or not Path(self.service_account_path).exists():
                logger.warning("⚠️ Google Sheets service account file not found")
                return
            
            # Set up credentials
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.service_account_path,
                scopes=scopes
            )
            
            self.client = gspread.authorize(credentials)
            
            # Open or create spreadsheet
            if self.spreadsheet_id:
                try:
                    self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                    logger.info(f"✅ Connected to existing spreadsheet: {self.spreadsheet.title}")
                except Exception as e:
                    logger.error(f"❌ Could not open spreadsheet {self.spreadsheet_id}: {e}")
            else:
                logger.warning("⚠️ No spreadsheet ID provided")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets client: {e}")
    
    async def full_sync(self, db_manager: LocalDatabaseManager = None) -> Dict[str, Any]:
        """Perform a complete sync of all data to Google Sheets"""
        try:
            if not self.client or not self.spreadsheet:
                return {"success": False, "error": "Google Sheets not configured"}
            
            db = db_manager or await get_local_db_manager()
            
            sync_result = {
                "sync_started": datetime.now().isoformat(),
                "tables_synced": {},
                "total_records": 0,
                "success": True,
                "errors": []
            }
            
            logger.info("🔄 Starting full sync to Google Sheets...")
            
            # Get all data from database
            dataframes = await db.export_to_dataframes()
            
            if not dataframes:
                return {"success": False, "error": "No data to sync"}
            
            # Sync each table
            for table_name, df in dataframes.items():
                try:
                    result = await self._sync_table(table_name, df)
                    sync_result["tables_synced"][table_name] = result
                    sync_result["total_records"] += result.get("records_synced", 0)
                    
                    if not result.get("success", False):
                        sync_result["errors"].append(f"Failed to sync {table_name}: {result.get('error')}")
                        
                except Exception as e:
                    error_msg = f"Error syncing {table_name}: {str(e)}"
                    sync_result["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            # Create dashboard worksheet
            dashboard_result = await self._create_dashboard_sheet(db)
            sync_result["tables_synced"]["dashboard"] = dashboard_result
            
            sync_result["sync_completed"] = datetime.now().isoformat()
            sync_result["success"] = len(sync_result["errors"]) == 0
            
            logger.info(f"✅ Full sync completed: {sync_result['total_records']} records synced")
            return sync_result
            
        except Exception as e:
            logger.error(f"❌ Full sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def incremental_sync(self, db_manager: LocalDatabaseManager = None) -> Dict[str, Any]:
        """Sync only records that have changed since last sync"""
        try:
            if not self.client or not self.spreadsheet:
                return {"success": False, "error": "Google Sheets not configured"}
            
            db = db_manager or await get_local_db_manager()
            
            # Get pending syncs
            pending_syncs = await db.get_pending_syncs()
            
            if not pending_syncs:
                logger.info("ℹ️ No pending syncs found")
                return {"success": True, "message": "No changes to sync", "records_synced": 0}
            
            sync_result = {
                "sync_started": datetime.now().isoformat(),
                "records_synced": 0,
                "success": True,
                "errors": []
            }
            
            logger.info(f"🔄 Starting incremental sync: {len(pending_syncs)} records...")
            
            # Group syncs by table
            syncs_by_table = {}
            for sync in pending_syncs:
                table = sync['table_name']
                if table not in syncs_by_table:
                    syncs_by_table[table] = []
                syncs_by_table[table].append(sync)
            
            # Process each table
            for table_name, table_syncs in syncs_by_table.items():
                try:
                    result = await self._sync_table_incremental(table_name, table_syncs, db)
                    sync_result["records_synced"] += result.get("records_synced", 0)
                    
                    if not result.get("success", False):
                        sync_result["errors"].append(f"Failed incremental sync for {table_name}: {result.get('error')}")
                        
                except Exception as e:
                    error_msg = f"Error in incremental sync for {table_name}: {str(e)}"
                    sync_result["errors"].append(error_msg)
                    logger.error(f"❌ {error_msg}")
            
            sync_result["sync_completed"] = datetime.now().isoformat()
            sync_result["success"] = len(sync_result["errors"]) == 0
            
            logger.info(f"✅ Incremental sync completed: {sync_result['records_synced']} records synced")
            return sync_result
            
        except Exception as e:
            logger.error(f"❌ Incremental sync failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sync_table(self, table_name: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Sync a complete table to Google Sheets"""
        try:
            if df.empty:
                return {"success": True, "records_synced": 0, "message": "No data in table"}
            
            worksheet_name = self._get_worksheet_name(table_name)
            
            # Try to get existing worksheet or create new one
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
                # Clear existing data
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=worksheet_name, rows=len(df)+10, cols=len(df.columns)+5)
            
            # Prepare data for upload
            data_to_upload = self._prepare_dataframe_for_sheets(df)
            
            # Upload data
            worksheet.update([data_to_upload.columns.tolist()] + data_to_upload.values.tolist())
            
            # Apply formatting
            await self._format_worksheet(worksheet, table_name)
            
            logger.info(f"✅ Synced {len(df)} records to {worksheet_name}")
            return {"success": True, "records_synced": len(df)}
            
        except Exception as e:
            logger.error(f"❌ Error syncing table {table_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sync_table_incremental(self, table_name: str, syncs: List[Dict], db: LocalDatabaseManager) -> Dict[str, Any]:
        """Sync specific records from a table"""
        try:
            worksheet_name = self._get_worksheet_name(table_name)
            
            # Get worksheet
            try:
                worksheet = self.spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                # If worksheet doesn't exist, fall back to full sync
                return await self._sync_table_fallback(table_name, db)
            
            records_synced = 0
            
            for sync in syncs:
                try:
                    # Get the record data
                    record_data = await self._get_record_data(table_name, sync['record_id'], db)
                    
                    if record_data:
                        # Update or insert record in worksheet
                        await self._upsert_record_in_worksheet(worksheet, record_data, table_name)
                        
                        # Mark sync as completed
                        await db.mark_sync_completed(sync['sync_id'], success=True)
                        records_synced += 1
                        
                    else:
                        # Record not found, mark sync as failed
                        await db.mark_sync_completed(sync['sync_id'], success=False, error_message="Record not found")
                        
                except Exception as e:
                    # Mark this specific sync as failed
                    await db.mark_sync_completed(sync['sync_id'], success=False, error_message=str(e))
                    logger.error(f"❌ Error syncing record {sync['record_id']}: {e}")
            
            return {"success": True, "records_synced": records_synced}
            
        except Exception as e:
            # Mark all syncs as failed
            for sync in syncs:
                await db.mark_sync_completed(sync['sync_id'], success=False, error_message=str(e))
            
            logger.error(f"❌ Error in incremental table sync {table_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_record_data(self, table_name: str, record_id: str, db: LocalDatabaseManager) -> Optional[Dict]:
        """Get record data from database"""
        try:
            if table_name == 'contacts':
                return await db.get_contact(record_id)
            elif table_name == 'interactions':
                # Add method to get interaction by ID
                pass
            elif table_name == 'leads':
                # Add method to get lead by ID  
                pass
            # Add other table handlers as needed
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting record data for {table_name}.{record_id}: {e}")
            return None
    
    def _get_worksheet_name(self, table_name: str) -> str:
        """Get formatted worksheet name for table"""
        name_mapping = {
            'contacts': 'Contacts & Leads',
            'organizations': 'Organizations',
            'interactions': 'Interactions & Messages', 
            'leads': 'Lead Opportunities',
            'messages': 'Telegram Messages',
            'chat_groups': 'Chat Groups'
        }
        
        return name_mapping.get(table_name, table_name.title())
    
    def _prepare_dataframe_for_sheets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for Google Sheets upload"""
        # Convert DataFrame copy to avoid modifying original
        sheets_df = df.copy()
        
        # Handle JSON columns
        json_columns = ['tags', 'custom_fields', 'key_topics', 'opportunities_identified', 'metadata', 'keywords']
        for col in json_columns:
            if col in sheets_df.columns:
                sheets_df[col] = sheets_df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else str(x) if x is not None else '')
        
        # Handle datetime columns
        datetime_columns = ['created_at', 'updated_at', 'last_interaction', 'next_follow_up', 'interaction_date', 'timestamp']
        for col in datetime_columns:
            if col in sheets_df.columns:
                sheets_df[col] = pd.to_datetime(sheets_df[col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Handle boolean columns
        bool_columns = ['is_active', 'follow_up_required', 'budget_confirmed', 'is_duplicate', 'processed']
        for col in bool_columns:
            if col in sheets_df.columns:
                sheets_df[col] = sheets_df[col].astype(str)
        
        # Fill NaN values
        sheets_df = sheets_df.fillna('')
        
        # Ensure all values are strings for Sheets compatibility
        for col in sheets_df.columns:
            sheets_df[col] = sheets_df[col].astype(str)
        
        return sheets_df
    
    async def _format_worksheet(self, worksheet, table_name: str):
        """Apply formatting to worksheet"""
        try:
            # Header formatting
            header_format = CellFormat(
                backgroundColor=Color(0.2, 0.5, 0.8),
                textFormat={'bold': True, 'foregroundColor': Color(1, 1, 1)}
            )
            
            # Apply header formatting to first row
            format_cell_range(worksheet, 'A1:Z1', header_format)
            
            # Auto-resize columns (not available in gspread, but we can set reasonable widths)
            # This is a limitation we'll document
            
            logger.info(f"✅ Applied formatting to {worksheet.title}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not apply formatting to {worksheet.title}: {e}")
    
    async def _create_dashboard_sheet(self, db: LocalDatabaseManager) -> Dict[str, Any]:
        """Create a dashboard summary sheet"""
        try:
            dashboard_name = "📊 Dashboard Overview"
            
            # Get database stats
            stats = await db.get_database_stats()
            
            # Try to get existing worksheet or create new one
            try:
                worksheet = self.spreadsheet.worksheet(dashboard_name)
                worksheet.clear()
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=dashboard_name, rows=50, cols=10)
            
            # Create dashboard data
            dashboard_data = [
                ["📊 Business Development Dashboard", "", "", ""],
                ["Last Updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "", ""],
                ["", "", "", ""],
                ["📈 Key Metrics", "", "", ""],
                ["Total Contacts:", stats.get('total_contacts', 0), "", ""],
                ["Total Organizations:", stats.get('total_organizations', 0), "", ""],
                ["Total Leads:", stats.get('total_leads', 0), "", ""],
                ["Total Interactions:", stats.get('total_interactions', 0), "", ""],
                ["", "", "", ""],
                ["💰 Pipeline Metrics", "", "", ""],
                ["Total Pipeline Value:", f"${stats.get('total_pipeline_value', 0):,.2f}", "", ""],
                ["Average Lead Score:", f"{stats.get('avg_lead_score', 0):.1f}", "", ""],
                ["Hot Leads (Score ≥70):", stats.get('hot_leads', 0), "", ""],
                ["Follow-ups Needed:", stats.get('follow_ups_needed', 0), "", ""],
                ["", "", "", ""],
                ["📊 Recent Activity", "", "", ""],
                ["Interactions (Last 7 Days):", stats.get('interactions_last_7_days', 0), "", ""],
                ["Messages (Last 7 Days):", stats.get('messages_last_7_days', 0), "", ""],
                ["", "", "", ""],
                ["🔄 Sync Status", "", "", ""],
                ["Pending Syncs:", stats.get('sync_pending', 0), "", ""],
                ["Completed Syncs:", stats.get('sync_completed', 0), "", ""],
                ["Failed Syncs:", stats.get('sync_failed', 0), "", ""],
                ["", "", "", ""],
                ["💾 Database Info", "", "", ""],
                ["Database Size (MB):", f"{stats.get('database_size_mb', 0):.2f}", "", ""]
            ]
            
            # Upload dashboard data
            worksheet.update(dashboard_data)
            
            # Apply formatting
            title_format = CellFormat(
                backgroundColor=Color(0.1, 0.3, 0.7),
                textFormat={'bold': True, 'foregroundColor': Color(1, 1, 1), 'fontSize': 14}
            )
            
            section_format = CellFormat(
                backgroundColor=Color(0.9, 0.9, 0.9),
                textFormat={'bold': True}
            )
            
            # Format title
            format_cell_range(worksheet, 'A1:D1', title_format)
            
            # Format section headers
            section_rows = [4, 10, 16, 19, 24]
            for row in section_rows:
                format_cell_range(worksheet, f'A{row}:D{row}', section_format)
            
            logger.info("✅ Dashboard sheet created")
            return {"success": True, "records_synced": len(dashboard_data)}
            
        except Exception as e:
            logger.error(f"❌ Error creating dashboard sheet: {e}")
            return {"success": False, "error": str(e)}
    
    async def _upsert_record_in_worksheet(self, worksheet, record_data: Dict, table_name: str):
        """Insert or update a record in worksheet"""
        # This is a simplified implementation
        # In a production system, you'd want more sophisticated record matching and updating
        try:
            # For now, we'll append new records
            # In the future, implement record matching and updating logic
            
            # Convert record to row format
            if table_name == 'contacts':
                row_data = [
                    record_data.get('contact_id', ''),
                    record_data.get('first_name', ''),
                    record_data.get('last_name', ''),
                    record_data.get('username', ''),
                    record_data.get('email', ''),
                    record_data.get('phone', ''),
                    record_data.get('organization_name', ''),
                    record_data.get('contact_type', ''),
                    record_data.get('lead_status', ''),
                    record_data.get('lead_score', 0),
                    record_data.get('estimated_value', 0),
                    record_data.get('probability', 0),
                    json.dumps(record_data.get('tags', [])),
                    record_data.get('notes', ''),
                    str(record_data.get('last_interaction', '')),
                    str(record_data.get('next_follow_up', '')),
                    str(record_data.get('created_at', '')),
                    str(record_data.get('updated_at', ''))
                ]
                
                worksheet.append_row(row_data)
                
        except Exception as e:
            logger.error(f"❌ Error upserting record: {e}")
            raise
    
    async def _sync_table_fallback(self, table_name: str, db: LocalDatabaseManager) -> Dict[str, Any]:
        """Fallback to full table sync if incremental fails"""
        try:
            dataframes = await db.export_to_dataframes()
            if table_name in dataframes:
                return await self._sync_table(table_name, dataframes[table_name])
            else:
                return {"success": False, "error": f"Table {table_name} not found in database"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync configuration status"""
        return {
            "google_sheets_configured": self.client is not None,
            "spreadsheet_connected": self.spreadsheet is not None,
            "spreadsheet_id": self.spreadsheet_id,
            "service_account_configured": bool(self.service_account_path and Path(self.service_account_path).exists()),
            "spreadsheet_title": self.spreadsheet.title if self.spreadsheet else None,
            "worksheets_count": len(self.spreadsheet.worksheets()) if self.spreadsheet else 0
        }
    
    async def create_backup_sync(self, backup_spreadsheet_id: str = None) -> Dict[str, Any]:
        """Create a backup sync to a different spreadsheet"""
        try:
            # Save current spreadsheet
            original_spreadsheet = self.spreadsheet
            original_id = self.spreadsheet_id
            
            # Switch to backup spreadsheet
            if backup_spreadsheet_id:
                self.spreadsheet_id = backup_spreadsheet_id
                self.spreadsheet = self.client.open_by_key(backup_spreadsheet_id)
            else:
                # Create new backup spreadsheet
                backup_title = f"BD Database Backup - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.spreadsheet = self.client.create(backup_title)
                backup_spreadsheet_id = self.spreadsheet.id
            
            # Perform full sync to backup
            result = await self.full_sync()
            
            # Restore original spreadsheet
            self.spreadsheet = original_spreadsheet
            self.spreadsheet_id = original_id
            
            return {
                "success": result.get("success", False),
                "backup_spreadsheet_id": backup_spreadsheet_id,
                "backup_title": self.spreadsheet.title if result.get("success") else None,
                "records_synced": result.get("total_records", 0)
            }
            
        except Exception as e:
            logger.error(f"❌ Backup sync failed: {e}")
            return {"success": False, "error": str(e)}

# Global instance
sheets_sync_manager = None

def get_sheets_sync_manager(service_account_path: str = None, spreadsheet_id: str = None) -> SheetsyncManager:
    """Get the global sync manager instance"""
    global sheets_sync_manager
    if sheets_sync_manager is None:
        sheets_sync_manager = SheetsyncManager(service_account_path, spreadsheet_id)
    return sheets_sync_manager 