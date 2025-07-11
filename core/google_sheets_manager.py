#!/usr/bin/env python3
"""
Google Sheets Manager - Mock Implementation
===========================================
Mock implementation for Google Sheets management
"""

class GoogleSheetsManager:
    """Mock Google Sheets Manager"""
    
    def __init__(self, service_account_file=None, sheet_id=None):
        self.service_account_file = service_account_file
        self.sheet_id = sheet_id
        self.worksheet = None
    
    async def setup_bd_pipeline(self):
        """Setup BD pipeline"""
        return {"status": "success", "message": "BD pipeline setup complete"}
    
    async def sync_contact(self, contact_data):
        """Sync contact to sheets"""
        return {"status": "success", "message": "Contact synced"}
    
    async def get_dashboard_url(self):
        """Get dashboard URL"""
        return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}"
    
    async def get_analytics(self):
        """Get analytics"""
        return {
            "total_contacts": 0,
            "active_deals": 0,
            "conversion_rate": 0.0,
            "last_updated": "Mock data"
        } 