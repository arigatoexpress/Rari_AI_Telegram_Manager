#!/usr/bin/env python3
"""
AI Analytics CLI
===============
Enhanced command-line interface for AI-powered business development analytics
with comprehensive database management capabilities.

Available Commands:
- config: Show configuration status
- dashboard: Display analytics dashboard
- analyze: Run comprehensive AI analysis
- export: Export to Google Sheets
- report: Generate executive reports
- all: Run complete workflow
- db-status: Show database status and health
- db-import: Import Telegram data
- db-sync: Sync to Google Sheets
- db-backup: Create database backup
- db-export: Export data to files
- db-optimize: Optimize database performance
- db-maintenance: Run full maintenance
"""

import sys
import asyncio
import logging
import json
from pathlib import Path
from datetime import datetime
import click

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from ai_analytics_engine import AIAnalyticsEngine
from core.database_commands import db_commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analytics.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

async def run_config():
    """Show configuration status"""
    print_header("🔧 CONFIGURATION STATUS")
    
    try:
        engine = AIAnalyticsEngine()
        config = await engine.check_configuration()
        
        print_section("Core Configuration")
        
        # AI Configuration
        ai_status = "✅ Configured" if config.get('openai_configured') else "❌ Missing API Key"
        print(f"🤖 OpenAI API: {ai_status}")
        
        # Database Configuration
        db_status = "✅ Available" if config.get('database_available') else "❌ Not Found"
        print(f"💾 Database: {db_status}")
        
        # Google Sheets Configuration
        sheets_status = "✅ Configured" if config.get('google_sheets_configured') else "❌ Missing Service Account"
        print(f"📊 Google Sheets: {sheets_status}")
        
        # Get detailed database status
        print_section("Database Details")
        db_status_result = await db_commands.database_status()
        
        if db_status_result.get('success'):
            db_info = db_status_result['status']['database']
            print(f"📂 Database Path: {db_info['path']}")
            print(f"💾 Database Size: {db_info['size_mb']:.2f} MB")
            print(f"👥 Total Contacts: {db_info['tables']['contacts']}")
            print(f"🏢 Total Organizations: {db_info['tables']['organizations']}")
            print(f"💬 Total Interactions: {db_info['tables']['interactions']}")
            print(f"🎯 Total Leads: {db_info['tables']['leads']}")
            
            # Health assessment
            health = db_status_result['status']['health']
            health_emoji = {"excellent": "🟢", "good": "🟡", "fair": "🟠", "poor": "🔴"}.get(health['level'], "⚪")
            print(f"\n🏥 Database Health: {health_emoji} {health['level'].title()} (Score: {health['score']}/100)")
            
            if health['issues']:
                print("\n⚠️ Issues Found:")
                for issue in health['issues']:
                    print(f"   • {issue}")
            
            if health['recommendations']:
                print("\n💡 Recommendations:")
                for rec in health['recommendations']:
                    print(f"   • {rec}")
        
        # Sync Configuration
        if config.get('google_sheets_configured'):
            print_section("Sync Status")
            sync_info = db_status_result['status']['sync']
            sync_status = "✅ Connected" if sync_info['spreadsheet_connected'] else "❌ Not Connected"
            print(f"🔗 Spreadsheet: {sync_status}")
            if sync_info.get('spreadsheet_title'):
                print(f"📋 Spreadsheet: {sync_info['spreadsheet_title']}")
            print(f"⏳ Pending Syncs: {sync_info['pending_syncs']}")
            print(f"✅ Completed Syncs: {sync_info['completed_syncs']}")
            print(f"❌ Failed Syncs: {sync_info['failed_syncs']}")
        
        print_section("Next Steps")
        if not config.get('openai_configured'):
            print("1. Set up OpenAI API key in environment")
        if not config.get('google_sheets_configured'):
            print("1. Configure Google Sheets service account")
        if config.get('database_available') and not db_info['tables']['contacts']:
            print("1. Import Telegram data: python run_analytics.py db-import")
        print("2. Run analysis: python run_analytics.py analyze")
        print("3. Export to sheets: python run_analytics.py export")
        
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        logger.error(f"Configuration error: {e}")

async def run_dashboard():
    """Display analytics dashboard"""
    print_header("📊 ANALYTICS DASHBOARD")
    
    try:
        engine = AIAnalyticsEngine()
        
        # Get database status for metrics
        db_status_result = await db_commands.database_status()
        
        if not db_status_result.get('success'):
            print("❌ Could not load database metrics")
            return
        
        db_info = db_status_result['status']['database']
        
        print_section("Key Metrics")
        print(f"👥 Total Contacts: {db_info['tables']['contacts']:,}")
        print(f"🏢 Organizations: {db_info['tables']['organizations']:,}")
        print(f"🎯 Active Leads: {db_info['tables']['leads']:,}")
        print(f"💬 Interactions: {db_info['tables']['interactions']:,}")
        
        print_section("Pipeline Metrics")
        print(f"💰 Pipeline Value: ${db_info['metrics']['total_pipeline_value']:,.2f}")
        print(f"📈 Average Lead Score: {db_info['metrics']['avg_lead_score']:.1f}")
        print(f"🔥 Hot Leads: {db_info['metrics']['hot_leads']:,}")
        print(f"⏰ Follow-ups Needed: {db_info['metrics']['follow_ups_needed']:,}")
        
        print_section("Recent Activity")
        print(f"📅 Interactions (7 days): {db_info['recent_activity']['interactions_last_7_days']:,}")
        print(f"💬 Messages (7 days): {db_info['recent_activity']['messages_last_7_days']:,}")
        
        # Show available operations
        print_section("Available Operations")
        print("🔍 analyze     - Run AI analysis")
        print("📤 export      - Export to Google Sheets")
        print("📋 report      - Generate executive report")
        print("🔄 db-sync     - Sync database to sheets")
        print("💾 db-backup   - Create database backup")
        print("🔧 db-maintenance - Run full maintenance")
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        logger.error(f"Dashboard error: {e}")

async def run_analyze():
    """Run comprehensive AI analysis"""
    print_header("🤖 AI ANALYSIS")
    
    try:
        engine = AIAnalyticsEngine()
        
        print("🔄 Running comprehensive AI analysis...")
        print("   This may take a few minutes...")
        
        result = await engine.run_comprehensive_analysis()
        
        if result.get('success'):
            print("✅ Analysis completed successfully!")
            
            analysis = result.get('analysis', {})
            
            # Show key insights
            if 'key_insights' in analysis:
                print_section("🔍 Key Insights")
                for insight in analysis['key_insights'][:5]:
                    print(f"   • {insight}")
            
            # Show top opportunities
            if 'opportunities' in analysis:
                print_section("🎯 Top Opportunities")
                for opp in analysis['opportunities'][:3]:
                    print(f"   • {opp}")
            
            # Show recommendations
            if 'recommendations' in analysis:
                print_section("💡 Recommendations")
                for rec in analysis['recommendations'][:3]:
                    print(f"   • {rec}")
            
            print(f"\n📄 Full analysis saved to: {result.get('output_file', 'analysis.json')}")
            
        else:
            print(f"❌ Analysis failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        logger.error(f"Analysis error: {e}")

async def run_export():
    """Export to Google Sheets"""
    print_header("📤 GOOGLE SHEETS EXPORT")
    
    try:
        print("🔄 Exporting to Google Sheets...")
        
        result = await db_commands.sync_to_sheets(full_sync=True)
        
        if result.get('success'):
            print("✅ Export completed successfully!")
            print(f"📊 Records exported: {result.get('total_records', result.get('records_synced', 0)):,}")
            
            if 'tables_synced' in result:
                print_section("📋 Tables Exported")
                for table, table_result in result['tables_synced'].items():
                    if table_result.get('success'):
                        records = table_result.get('records_synced', 0)
                        print(f"   ✅ {table}: {records:,} records")
                    else:
                        print(f"   ❌ {table}: {table_result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Export failed: {result.get('error')}")
            if result.get('errors'):
                for error in result['errors']:
                    print(f"   🔸 {error}")
                    
    except Exception as e:
        print(f"❌ Export error: {e}")
        logger.error(f"Export error: {e}")

async def run_report():
    """Generate executive reports"""
    print_header("📋 EXECUTIVE REPORT")
    
    try:
        engine = AIAnalyticsEngine()
        
        print("🔄 Generating executive report...")
        
        result = await engine.generate_executive_report()
        
        if result.get('success'):
            print("✅ Report generated successfully!")
            
            # Show summary
            report = result.get('report', {})
            if 'executive_summary' in report:
                print_section("📋 Executive Summary")
                print(f"   {report['executive_summary']}")
            
            if 'key_metrics' in report:
                metrics = report['key_metrics']
                print_section("📊 Key Metrics")
                for metric, value in metrics.items():
                    if isinstance(value, (int, float)):
                        if 'value' in metric or 'pipeline' in metric:
                            print(f"   {metric}: ${value:,.2f}")
                        else:
                            print(f"   {metric}: {value:,}")
                    else:
                        print(f"   {metric}: {value}")
            
            print(f"\n📄 Full report saved to: {result.get('output_file', 'report.json')}")
            print(f"📄 Markdown report: {result.get('markdown_file', 'report.md')}")
            
        else:
            print(f"❌ Report generation failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Report error: {e}")
        logger.error(f"Report error: {e}")

async def run_all():
    """Run complete workflow"""
    print_header("🚀 COMPLETE WORKFLOW")
    
    print("Running complete AI analytics workflow...")
    print("This includes: Config → Dashboard → Analysis → Export → Report")
    
    # Run each component
    await run_config()
    await run_dashboard()
    await run_analyze()
    await run_export()
    await run_report()
    
    print_header("✅ WORKFLOW COMPLETED")
    print("All operations completed successfully!")
    print("Check the exports/ directory for generated files.")

# Database Management Commands

async def run_db_status():
    """Show database status and health"""
    print_header("💾 DATABASE STATUS")
    
    result = await db_commands.database_status()
    
    if result.get('success'):
        status = result['status']
        db_info = status['database']
        
        print_section("Database Information")
        print(f"📂 Path: {db_info['path']}")
        print(f"💾 Size: {db_info['size_mb']:.2f} MB")
        
        print_section("Table Counts")
        for table, count in db_info['tables'].items():
            print(f"   {table}: {count:,}")
        
        print_section("Health Assessment")
        health = status['health']
        health_emoji = {"excellent": "🟢", "good": "🟡", "fair": "🟠", "poor": "🔴"}.get(health['level'], "⚪")
        print(f"Status: {health_emoji} {health['level'].title()} (Score: {health['score']}/100)")
        
        if health['issues']:
            print("\n⚠️ Issues:")
            for issue in health['issues']:
                print(f"   • {issue}")
        
        if health['recommendations']:
            print("\n💡 Recommendations:")
            for rec in health['recommendations']:
                print(f"   • {rec}")
    else:
        print(f"❌ Error: {result.get('error')}")

async def run_db_import():
    """Import Telegram data"""
    print_header("📥 IMPORT TELEGRAM DATA")
    
    result = await db_commands.import_telegram_data()
    
    # Output is handled within the command
    if not result.get('success'):
        print(f"\n❌ Final result: {result.get('error')}")

async def run_db_sync():
    """Sync to Google Sheets"""
    print_header("🔄 SYNC TO GOOGLE SHEETS")
    
    result = await db_commands.sync_to_sheets()
    
    # Output is handled within the command
    if not result.get('success'):
        print(f"\n❌ Final result: {result.get('error')}")

async def run_db_backup():
    """Create database backup"""
    print_header("💾 DATABASE BACKUP")
    
    result = await db_commands.backup_database()
    
    # Output is handled within the command
    if not result.get('success'):
        print(f"\n❌ Final result: {result.get('error')}")

async def run_db_export():
    """Export data to files"""
    print_header("📤 EXPORT DATA")
    
    # Ask for format
    print("Available formats: csv, excel, json")
    format_choice = input("Enter format (default: csv): ").strip().lower() or "csv"
    
    if format_choice not in ['csv', 'excel', 'json']:
        print("❌ Invalid format. Using CSV.")
        format_choice = 'csv'
    
    result = await db_commands.export_data(format=format_choice)
    
    if result.get('success'):
        print(f"\n✅ Export completed: {result.get('total_files')} files exported")
        print(f"📂 Output directory: {result.get('output_directory')}")
    else:
        print(f"❌ Export failed: {result.get('error')}")

async def run_db_optimize():
    """Optimize database performance"""
    print_header("🔧 OPTIMIZE DATABASE")
    
    result = await db_commands.optimize_database()
    
    # Output is handled within the command
    if not result.get('success'):
        print(f"\n❌ Final result: {result.get('error')}")

async def run_db_maintenance():
    """Run full maintenance"""
    print_header("🔧 DATABASE MAINTENANCE")
    
    result = await db_commands.run_maintenance()
    
    if result.get('success'):
        print("\n✅ All maintenance tasks completed successfully!")
    else:
        print(f"\n❌ Maintenance failed: {result.get('error')}")

async def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print_header("🤖 AI ANALYTICS ENGINE")
        print("Available commands:")
        print("  config      - Show configuration status")
        print("  dashboard   - Display analytics dashboard")
        print("  analyze     - Run comprehensive AI analysis")
        print("  export      - Export to Google Sheets")
        print("  report      - Generate executive reports")
        print("  all         - Run complete workflow")
        print("\nDatabase Management:")
        print("  db-status   - Show database status and health")
        print("  db-import   - Import Telegram data")
        print("  db-sync     - Sync to Google Sheets")
        print("  db-backup   - Create database backup")
        print("  db-export   - Export data to files")
        print("  db-optimize - Optimize database performance")
        print("  db-maintenance - Run full maintenance")
        print("\nUsage: python run_analytics.py <command>")
        return
    
    command = sys.argv[1].lower()
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    try:
        if command == "config":
            await run_config()
        elif command == "dashboard":
            await run_dashboard()
        elif command == "analyze":
            await run_analyze()
        elif command == "export":
            await run_export()
        elif command == "report":
            await run_report()
        elif command == "all":
            await run_all()
        elif command == "db-status":
            await run_db_status()
        elif command == "db-import":
            await run_db_import()
        elif command == "db-sync":
            await run_db_sync()
        elif command == "db-backup":
            await run_db_backup()
        elif command == "db-export":
            await run_db_export()
        elif command == "db-optimize":
            await run_db_optimize()
        elif command == "db-maintenance":
            await run_db_maintenance()
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python run_analytics.py' to see available commands")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"CLI error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 