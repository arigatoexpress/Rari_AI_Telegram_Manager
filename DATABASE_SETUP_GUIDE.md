# Local Database & Google Sheets Sync Setup Guide

## Overview

Your system now has a robust **local database as the primary source of truth** with comprehensive Google Sheets synchronization capabilities. This setup provides data redundancy, offline capabilities, and professional reporting.

## 🏗️ Architecture

```
Local SQLite Database (Primary Source of Truth)
    ↓
Enhanced Data Management Layer
    ↓
Sync Manager
    ↓
Google Sheets (Secondary/Reporting)
```

## 📊 Database Schema

### Core Tables
- **`contacts`** - All business contacts with lead scoring and status
- **`organizations`** - Companies and organizations  
- **`interactions`** - All communication interactions
- **`leads`** - Active business opportunities
- **`messages`** - Imported Telegram message history
- **`chat_groups`** - Telegram group information
- **`analytics_snapshots`** - Historical analytics data
- **`sync_tracking`** - Sync status monitoring

## 🚀 Quick Start

### 1. Database Status Check
```bash
python run_analytics.py db-status
```
Shows database health, table counts, and sync status.

### 2. Import Telegram Data
```bash
python run_analytics.py db-import
```
Imports messages and creates contacts automatically.

### 3. Sync to Google Sheets
```bash
python run_analytics.py db-sync
```
Syncs all data to Google Sheets with formatted worksheets.

### 4. Create Backup
```bash
python run_analytics.py db-backup
```
Creates local database backup and Google Sheets backup.

## 🔧 Database Management Commands

### Data Operations
- `db-status` - Database health and statistics
- `db-import` - Import Telegram data
- `db-export` - Export to CSV/Excel/JSON
- `db-sync` - Sync to Google Sheets (incremental)
- `db-backup` - Create comprehensive backups

### Maintenance
- `db-optimize` - Vacuum and optimize database
- `db-maintenance` - Full maintenance workflow

## 📊 Google Sheets Integration

### Worksheets Created
1. **📊 Dashboard Overview** - Key metrics and KPIs
2. **Contacts & Leads** - All contact information with lead scores
3. **Organizations** - Company database
4. **Interactions & Messages** - Communication history
5. **Lead Opportunities** - Active deals and pipeline
6. **Telegram Messages** - Raw message data
7. **Chat Groups** - Group analytics

### Sync Features
- **Incremental Sync** - Only syncs changed records
- **Conflict Resolution** - Handles data conflicts gracefully
- **Error Tracking** - Monitors and retries failed syncs
- **Format Preservation** - Professional formatting maintained

## 🔄 Data Flow

### Import Process
1. **Source Data** (Telegram DB) → **Local Database**
2. **Message Processing** → **Contact Creation**
3. **Interaction Logging** → **Lead Scoring**
4. **Auto-sync** → **Google Sheets**

### Sync Process
1. **Change Detection** → **Sync Queue**
2. **Batch Processing** → **Google Sheets API**
3. **Status Tracking** → **Error Handling**
4. **Completion Logging** → **Health Monitoring**

## 📈 Analytics & Reports

### Available Metrics
- Total contacts and organizations
- Pipeline value and lead scores
- Hot leads and follow-up requirements
- Recent activity trends
- Sync performance monitoring

### Report Generation
```bash
python run_analytics.py report
```
Generates executive reports with AI insights.

## 🛠️ Configuration

### Environment Variables
```bash
# Database (uses local SQLite by default)
DATABASE_PATH=data/local_bd_database.db

# Google Sheets (optional but recommended)
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id

# AI Analysis (optional)
OPENAI_API_KEY=your-openai-key
```

### Database Configuration
- **Location**: `data/local_bd_database.db`
- **Backup Location**: `backups/`
- **Auto-backup**: Enabled during maintenance
- **Optimization**: Automatic during maintenance

## 🏥 Health Monitoring

### Health Scores
- **🟢 Excellent (90-100)** - All systems optimal
- **🟡 Good (75-89)** - Minor issues
- **🟠 Fair (50-74)** - Attention needed  
- **🔴 Poor (<50)** - Immediate action required

### Common Issues & Solutions

#### No Contacts in Database
```bash
python run_analytics.py db-import
```

#### Failed Syncs
```bash
python run_analytics.py db-sync
```

#### Database Performance
```bash
python run_analytics.py db-optimize
```

#### General Maintenance
```bash
python run_analytics.py db-maintenance
```

## 💾 Backup Strategy

### Automated Backups
- **Database files** - Copied with timestamps
- **Google Sheets** - Full spreadsheet duplication
- **Metadata** - Sync status and health data

### Manual Backup
```bash
python run_analytics.py db-backup
```

### Restore Process
1. Stop all processes
2. Replace database file from backup
3. Verify data integrity
4. Resume operations

## 🔧 Advanced Usage

### Custom Data Import
```python
from core.local_database_manager import get_local_db_manager

db = await get_local_db_manager()
# Custom import logic here
```

### Direct Database Access
```python
import sqlite3
conn = sqlite3.connect('data/local_bd_database.db')
# Direct SQL operations
```

### Sync Customization
```python
from core.sheets_sync_manager import get_sheets_sync_manager

sync = get_sheets_sync_manager()
# Custom sync operations
```

## 📊 Analytics Dashboard

The system creates a comprehensive analytics dashboard showing:

- **Contact Metrics**: Total contacts, lead scores, conversion rates
- **Pipeline Analytics**: Deal values, probability assessments, stage distribution  
- **Activity Tracking**: Recent interactions, follow-up requirements
- **Health Monitoring**: System status, sync performance, data quality

## 🔄 Workflow Integration

### Daily Operations
1. Check dashboard: `python run_analytics.py dashboard`
2. Review status: `python run_analytics.py db-status`
3. Sync data: `python run_analytics.py db-sync`

### Weekly Maintenance
1. Run maintenance: `python run_analytics.py db-maintenance`
2. Generate reports: `python run_analytics.py report`
3. Review analytics: `python run_analytics.py analyze`

### Monthly Reviews
1. Create backups: `python run_analytics.py db-backup`
2. Export data: `python run_analytics.py db-export`
3. Optimize performance: `python run_analytics.py db-optimize`

## 🎯 Next Steps

1. **Set up Google Sheets** - Configure service account and spreadsheet
2. **Import your data** - Run `db-import` to populate the database
3. **Start syncing** - Use `db-sync` to populate Google Sheets
4. **Monitor health** - Regular `db-status` checks
5. **Generate insights** - Use `analyze` and `report` commands

## 🆘 Troubleshooting

### Common Commands for Issues

```bash
# Check overall system health
python run_analytics.py config

# Diagnose database issues  
python run_analytics.py db-status

# Fix common problems
python run_analytics.py db-maintenance

# Reset sync state (if needed)
python run_analytics.py db-sync --full

# Get help
python run_analytics.py
```

### Contact Support
- Check logs in `logs/` directory
- Review error messages in terminal output
- Use `db-status` for diagnostic information

## 📈 Success Metrics

Your system is working optimally when you see:
- ✅ Regular successful syncs to Google Sheets
- ✅ Growing contact and interaction counts
- ✅ High health scores (90+)
- ✅ Professional reports being generated
- ✅ Actionable insights from AI analysis

---

*This system transforms your Telegram data into a professional business development platform with local reliability and cloud accessibility.* 