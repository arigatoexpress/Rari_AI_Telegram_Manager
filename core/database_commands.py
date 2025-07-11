#!/usr/bin/env python3
"""
Database Management Commands
===========================
Command handlers for database operations including:
- Data import from various sources
- Backup and restore operations  
- Database maintenance
- Sync management
- Migration utilities
"""

import logging
import asyncio
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import click

from .local_database_manager import LocalDatabaseManager, get_local_db_manager
from .sheets_sync_manager import SheetsyncManager, get_sheets_sync_manager

logger = logging.getLogger(__name__)

class DatabaseCommands:
    """Database management command handlers"""
    
    def __init__(self):
        self.db_manager = None
        self.sync_manager = None
    
    async def _init_managers(self):
        """Initialize database and sync managers"""
        if not self.db_manager:
            self.db_manager = await get_local_db_manager()
        if not self.sync_manager:
            self.sync_manager = get_sheets_sync_manager()
    
    async def database_status(self) -> Dict[str, Any]:
        """Get comprehensive database status"""
        try:
            await self._init_managers()
            
            # Get database statistics
            stats = await self.db_manager.get_database_stats()
            
            # Get sync status
            sync_status = self.sync_manager.get_sync_status()
            
            status = {
                "database": {
                    "path": str(self.db_manager.db_path),
                    "size_mb": stats.get('database_size_mb', 0),
                    "tables": {
                        "contacts": stats.get('total_contacts', 0),
                        "organizations": stats.get('total_organizations', 0),
                        "interactions": stats.get('total_interactions', 0),
                        "leads": stats.get('total_leads', 0),
                        "messages": stats.get('total_messages', 0),
                        "chat_groups": stats.get('total_chat_groups', 0)
                    },
                    "metrics": {
                        "avg_lead_score": stats.get('avg_lead_score', 0),
                        "total_pipeline_value": stats.get('total_pipeline_value', 0),
                        "hot_leads": stats.get('hot_leads', 0),
                        "follow_ups_needed": stats.get('follow_ups_needed', 0)
                    },
                    "recent_activity": {
                        "interactions_last_7_days": stats.get('interactions_last_7_days', 0),
                        "messages_last_7_days": stats.get('messages_last_7_days', 0)
                    }
                },
                "sync": {
                    "google_sheets_configured": sync_status.get('google_sheets_configured', False),
                    "spreadsheet_connected": sync_status.get('spreadsheet_connected', False),
                    "spreadsheet_title": sync_status.get('spreadsheet_title'),
                    "pending_syncs": stats.get('sync_pending', 0),
                    "completed_syncs": stats.get('sync_completed', 0),
                    "failed_syncs": stats.get('sync_failed', 0)
                },
                "health": self._assess_database_health(stats)
            }
            
            return {"success": True, "status": status}
            
        except Exception as e:
            logger.error(f"❌ Error getting database status: {e}")
            return {"success": False, "error": str(e)}
    
    def _assess_database_health(self, stats: Dict) -> Dict[str, Any]:
        """Assess overall database health"""
        health = {
            "score": 100,
            "issues": [],
            "recommendations": []
        }
        
        # Check for data completeness
        if stats.get('total_contacts', 0) == 0:
            health["score"] -= 30
            health["issues"].append("No contacts in database")
            health["recommendations"].append("Import Telegram data or add contacts manually")
        
        if stats.get('total_interactions', 0) == 0:
            health["score"] -= 20
            health["issues"].append("No interactions recorded")
            health["recommendations"].append("Import message history or log interactions")
        
        # Check sync health
        failed_syncs = stats.get('sync_failed', 0)
        if failed_syncs > 0:
            health["score"] -= min(30, failed_syncs * 5)
            health["issues"].append(f"{failed_syncs} failed syncs")
            health["recommendations"].append("Review and retry failed syncs")
        
        # Check follow-up management
        follow_ups_needed = stats.get('follow_ups_needed', 0)
        if follow_ups_needed > 10:
            health["score"] -= 10
            health["issues"].append(f"{follow_ups_needed} contacts need follow-up")
            health["recommendations"].append("Schedule follow-ups for overdue contacts")
        
        # Database size check
        db_size = stats.get('database_size_mb', 0)
        if db_size > 500:  # 500MB threshold
            health["score"] -= 5
            health["issues"].append("Large database size")
            health["recommendations"].append("Consider archiving old data")
        
        # Determine health level
        if health["score"] >= 90:
            health["level"] = "excellent"
        elif health["score"] >= 75:
            health["level"] = "good"
        elif health["score"] >= 50:
            health["level"] = "fair"
        else:
            health["level"] = "poor"
        
        return health
    
    async def import_telegram_data(self, source_path: str = None) -> Dict[str, Any]:
        """Import data from Telegram database"""
        try:
            await self._init_managers()
            
            print("🔄 Starting Telegram data import...")
            
            result = await self.db_manager.import_telegram_data(source_path)
            
            if result.get("success"):
                stats = result.get("stats", {})
                print("✅ Telegram import completed successfully!")
                print(f"   📥 Messages imported: {stats.get('messages_imported', 0)}")
                print(f"   👥 Contacts created: {stats.get('contacts_created', 0)}")
                print(f"   💬 Interactions created: {stats.get('interactions_created', 0)}")
                
                # Automatically sync to Google Sheets if configured
                if self.sync_manager.get_sync_status().get('google_sheets_configured'):
                    print("\n🔄 Syncing imported data to Google Sheets...")
                    sync_result = await self.sync_manager.incremental_sync(self.db_manager)
                    if sync_result.get("success"):
                        print(f"✅ Synced {sync_result.get('records_synced', 0)} records to Google Sheets")
                    else:
                        print(f"⚠️ Sync failed: {sync_result.get('error')}")
                
            else:
                print(f"❌ Import failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Telegram import error: {e}")
            return {"success": False, "error": str(e)}
    
    async def backup_database(self, backup_path: str = None) -> Dict[str, Any]:
        """Create database backup"""
        try:
            await self._init_managers()
            
            print("💾 Creating database backup...")
            
            backup_file = await self.db_manager.backup_database(backup_path)
            
            print(f"✅ Database backup created: {backup_file}")
            
            # Also create Google Sheets backup if configured
            if self.sync_manager.get_sync_status().get('google_sheets_configured'):
                print("🔄 Creating Google Sheets backup...")
                backup_result = await self.sync_manager.create_backup_sync()
                
                if backup_result.get("success"):
                    print(f"✅ Google Sheets backup created: {backup_result.get('backup_title')}")
                    print(f"   📊 Backup Spreadsheet ID: {backup_result.get('backup_spreadsheet_id')}")
                else:
                    print(f"⚠️ Google Sheets backup failed: {backup_result.get('error')}")
            
            return {
                "success": True,
                "local_backup": backup_file,
                "sheets_backup": backup_result if 'backup_result' in locals() else None
            }
            
        except Exception as e:
            logger.error(f"❌ Backup error: {e}")
            return {"success": False, "error": str(e)}
    
    async def sync_to_sheets(self, full_sync: bool = False) -> Dict[str, Any]:
        """Sync database to Google Sheets"""
        try:
            await self._init_managers()
            
            if not self.sync_manager.get_sync_status().get('google_sheets_configured'):
                return {"success": False, "error": "Google Sheets not configured"}
            
            if full_sync:
                print("🔄 Starting full sync to Google Sheets...")
                result = await self.sync_manager.full_sync(self.db_manager)
            else:
                print("🔄 Starting incremental sync to Google Sheets...")
                result = await self.sync_manager.incremental_sync(self.db_manager)
            
            if result.get("success"):
                print("✅ Sync completed successfully!")
                print(f"   📊 Records synced: {result.get('records_synced', result.get('total_records', 0))}")
                
                if 'tables_synced' in result:
                    print("   📋 Tables synced:")
                    for table, table_result in result['tables_synced'].items():
                        if table_result.get('success'):
                            print(f"      ✅ {table}: {table_result.get('records_synced', 0)} records")
                        else:
                            print(f"      ❌ {table}: {table_result.get('error', 'Unknown error')}")
                
            else:
                print(f"❌ Sync failed: {result.get('error')}")
                if result.get('errors'):
                    for error in result['errors']:
                        print(f"   🔸 {error}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Sync error: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance"""
        try:
            await self._init_managers()
            
            print("🔧 Optimizing database...")
            
            # Get stats before optimization
            stats_before = await self.db_manager.get_database_stats()
            size_before = stats_before.get('database_size_mb', 0)
            
            # Vacuum database
            await self.db_manager.vacuum_database()
            
            # Get stats after optimization
            stats_after = await self.db_manager.get_database_stats()
            size_after = stats_after.get('database_size_mb', 0)
            
            size_saved = size_before - size_after
            
            print("✅ Database optimization completed!")
            print(f"   💾 Size before: {size_before:.2f} MB")
            print(f"   💾 Size after: {size_after:.2f} MB")
            print(f"   💾 Space saved: {size_saved:.2f} MB")
            
            return {
                "success": True,
                "size_before_mb": size_before,
                "size_after_mb": size_after,
                "space_saved_mb": size_saved
            }
            
        except Exception as e:
            logger.error(f"❌ Optimization error: {e}")
            return {"success": False, "error": str(e)}
    
    async def export_data(self, format: str = "csv", output_dir: str = "exports") -> Dict[str, Any]:
        """Export database data to files"""
        try:
            await self._init_managers()
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            print(f"📤 Exporting database to {format.upper()} format...")
            
            # Get all data
            dataframes = await self.db_manager.export_to_dataframes()
            
            if not dataframes:
                return {"success": False, "error": "No data to export"}
            
            exported_files = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for table_name, df in dataframes.items():
                if df.empty:
                    continue
                
                filename = f"{table_name}_{timestamp}.{format}"
                file_path = output_path / filename
                
                if format.lower() == "csv":
                    df.to_csv(file_path, index=False)
                elif format.lower() == "excel":
                    df.to_excel(file_path, index=False)
                elif format.lower() == "json":
                    df.to_json(file_path, orient='records', indent=2)
                else:
                    return {"success": False, "error": f"Unsupported format: {format}"}
                
                exported_files.append(str(file_path))
                print(f"   ✅ {table_name}: {len(df)} records → {filename}")
            
            print(f"✅ Export completed! Files saved to: {output_path}")
            
            return {
                "success": True,
                "exported_files": exported_files,
                "output_directory": str(output_path),
                "total_files": len(exported_files)
            }
            
        except Exception as e:
            logger.error(f"❌ Export error: {e}")
            return {"success": False, "error": str(e)}
    
    async def import_csv_data(self, csv_file: str, table_name: str) -> Dict[str, Any]:
        """Import data from CSV file"""
        try:
            await self._init_managers()
            
            csv_path = Path(csv_file)
            if not csv_path.exists():
                return {"success": False, "error": f"CSV file not found: {csv_file}"}
            
            print(f"📥 Importing CSV data to {table_name} table...")
            
            # Read CSV
            df = pd.read_csv(csv_path)
            
            if df.empty:
                return {"success": False, "error": "CSV file is empty"}
            
            print(f"   📄 Found {len(df)} records in CSV")
            
            # Import based on table type
            imported_count = 0
            
            if table_name == "contacts":
                for _, row in df.iterrows():
                    # Convert row to Contact object and add to database
                    # This would need proper validation and mapping
                    pass  # Implementation depends on CSV structure
            
            # Mark all imports for sync
            print(f"✅ Imported {imported_count} records from CSV")
            
            return {
                "success": True,
                "records_imported": imported_count,
                "source_file": str(csv_path)
            }
            
        except Exception as e:
            logger.error(f"❌ CSV import error: {e}")
            return {"success": False, "error": str(e)}
    
    async def manage_contacts(self, action: str, **kwargs) -> Dict[str, Any]:
        """Manage contacts (add, update, search, delete)"""
        try:
            await self._init_managers()
            
            if action == "search":
                query = kwargs.get('query', '')
                filters = kwargs.get('filters', {})
                limit = kwargs.get('limit', 50)
                
                contacts = await self.db_manager.search_contacts(query, filters, limit)
                
                print(f"🔍 Found {len(contacts)} contacts")
                for contact in contacts[:10]:  # Show first 10
                    name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                    username = contact.get('username', '')
                    score = contact.get('lead_score', 0)
                    print(f"   👤 {name} (@{username}) - Score: {score}")
                
                if len(contacts) > 10:
                    print(f"   ... and {len(contacts) - 10} more")
                
                return {"success": True, "contacts": contacts, "count": len(contacts)}
            
            elif action == "add":
                # Add new contact
                contact_data = kwargs.get('contact_data', {})
                # Implementation for adding contact
                pass
            
            elif action == "update":
                # Update existing contact
                contact_id = kwargs.get('contact_id')
                updates = kwargs.get('updates', {})
                # Implementation for updating contact
                pass
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"❌ Contact management error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_maintenance(self) -> Dict[str, Any]:
        """Run comprehensive database maintenance"""
        try:
            await self._init_managers()
            
            print("🔧 Running database maintenance...")
            
            maintenance_results = {}
            
            # 1. Create backup
            print("\n1️⃣ Creating backup...")
            backup_result = await self.backup_database()
            maintenance_results['backup'] = backup_result
            
            # 2. Optimize database
            print("\n2️⃣ Optimizing database...")
            optimize_result = await self.optimize_database()
            maintenance_results['optimization'] = optimize_result
            
            # 3. Sync pending changes
            print("\n3️⃣ Syncing pending changes...")
            sync_result = await self.sync_to_sheets(full_sync=False)
            maintenance_results['sync'] = sync_result
            
            # 4. Health check
            print("\n4️⃣ Running health check...")
            status_result = await self.database_status()
            maintenance_results['health_check'] = status_result
            
            print("\n✅ Maintenance completed!")
            
            return {
                "success": True,
                "maintenance_results": maintenance_results,
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Maintenance error: {e}")
            return {"success": False, "error": str(e)}

# Create global instance
db_commands = DatabaseCommands() 