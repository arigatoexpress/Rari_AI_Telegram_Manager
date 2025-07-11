#!/usr/bin/env python3
"""
Telegram BD Intelligence - Main Application
===========================================
Unified entry point for the Telegram Business Development Intelligence System.

Features:
🧠 AI-Powered Analysis - ChatGPT conversation analysis and insights
📊 Lead Management - CRM, scoring, and pipeline tracking  
📱 Telegram Integration - Extract and analyze chat history
📈 Google Sheets - Professional dashboards and reporting
⚡ High Performance - Async processing with smart caching

Usage:
    python main.py                    # Interactive mode
    python main.py --help            # Show all commands
    python main.py dashboard          # Show analytics dashboard
    python main.py analyze           # Run AI analysis  
    python main.py export            # Export to Google Sheets
    python main.py bot               # Start Telegram bot
"""

import sys
import asyncio
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    print("\n" + "=" * 70)
    print("🚀 TELEGRAM BD INTELLIGENCE SYSTEM")
    print("=" * 70)
    print("🧠 AI-Powered Business Development & Lead Analysis")
    print("📊 Advanced Analytics • 📱 Telegram Integration • 📈 Google Sheets")
    print("=" * 70)

def show_main_menu():
    """Show interactive menu"""
    print("\n📋 Available Commands:")
    print("\n🔍 Analytics & Insights:")
    print("  dashboard    - Real-time analytics dashboard")
    print("  analyze      - Run comprehensive AI analysis")
    print("  report       - Generate executive reports")
    
    print("\n📊 Data Management:")
    print("  import       - Import Telegram data")
    print("  export       - Export to Google Sheets")
    print("  backup       - Create data backup")
    print("  status       - Show system status")
    
    print("\n🤖 Interactive Modes:")
    print("  bot          - Start Telegram bot interface")
    print("  interactive  - Interactive CLI mode")
    
    print("\n⚙️ Setup & Configuration:")
    print("  setup        - Initial system setup")
    print("  config       - Show configuration")
    print("  health       - System health check")
    
    print("\n💡 Quick Start:")
    print("  python main.py setup      # First-time setup")
    print("  python main.py dashboard  # View analytics")
    print("  python main.py analyze    # Run AI analysis")

async def run_dashboard():
    """Show analytics dashboard"""
    try:
        from run_analytics import run_dashboard as analytics_dashboard
        await analytics_dashboard()
    except ImportError as e:
        logger.error(f"Analytics module not available: {e}")
        print("❌ Analytics dashboard unavailable. Run: pip install -r requirements.txt")

async def run_analysis():
    """Run comprehensive AI analysis"""
    try:
        from run_analytics import run_analyze
        await run_analyze()
    except ImportError as e:
        logger.error(f"Analysis module not available: {e}")
        print("❌ AI analysis unavailable. Run: pip install -r requirements.txt")

async def run_export():
    """Export to Google Sheets"""
    try:
        from run_analytics import run_export
        await run_export()
    except ImportError as e:
        logger.error(f"Export module not available: {e}")
        print("❌ Google Sheets export unavailable. Run: pip install -r requirements.txt")

async def start_telegram_bot():
    """Start the Telegram bot interface"""
    try:
        from start_ultimate_bd_bot import main as bot_main
        print("🤖 Starting Telegram Bot Interface...")
        await bot_main()
    except ImportError as e:
        logger.error(f"Telegram bot not available: {e}")
        print("❌ Telegram bot unavailable. Run: pip install -r requirements.txt")

async def run_setup():
    """Run initial system setup"""
    try:
        from setup_telegram_bot import main as setup_main
        print("⚙️ Starting System Setup...")
        setup_main()
    except ImportError as e:
        logger.error(f"Setup module not available: {e}")
        print("❌ Setup unavailable. Please check installation.")

async def run_config():
    """Show system configuration"""
    try:
        from run_analytics import run_config
        await run_config()
    except ImportError as e:
        logger.error(f"Config module not available: {e}")
        print("❌ Configuration check unavailable.")

async def run_status():
    """Show system status"""
    try:
        from run_analytics import run_db_status
        await run_db_status()
    except ImportError as e:
        logger.error(f"Status module not available: {e}")
        print("❌ Status check unavailable.")

async def run_import():
    """Import Telegram data"""
    try:
        from run_analytics import run_db_import
        await run_db_import()
    except ImportError as e:
        logger.error(f"Import module not available: {e}")
        print("❌ Data import unavailable.")

async def run_backup():
    """Create system backup"""
    try:
        from run_analytics import run_db_backup
        await run_db_backup()
    except ImportError as e:
        logger.error(f"Backup module not available: {e}")
        print("❌ Backup unavailable.")

async def run_report():
    """Generate executive report"""
    try:
        from run_analytics import run_report
        await run_report()
    except ImportError as e:
        logger.error(f"Report module not available: {e}")
        print("❌ Report generation unavailable.")

async def run_health():
    """System health check"""
    print("🏥 System Health Check")
    print("-" * 30)
    
    # Check essential files
    checks = [
        ("📁 Core directory", Path("core").exists()),
        ("📄 Environment template", Path("env.template").exists()),
        ("📋 Requirements file", Path("requirements.txt").exists()),
        ("📂 Data directory", Path("data").exists() or "Will be created"),
        ("📝 Logs directory", Path("logs").exists()),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
    
    # Check Python modules
    print("\n🐍 Python Dependencies:")
    modules = ["sqlite3", "asyncio", "pathlib", "logging"]
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")

async def interactive_mode():
    """Interactive CLI mode"""
    print("🔄 Interactive Mode - Type 'help' for commands, 'exit' to quit")
    
    while True:
        try:
            command = input("\n📱 BD Intelligence > ").strip().lower()
            
            if command in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            elif command in ['help', 'h', '?']:
                show_main_menu()
            elif command == 'dashboard':
                await run_dashboard()
            elif command == 'analyze':
                await run_analysis()
            elif command == 'export':
                await run_export()
            elif command == 'status':
                await run_status()
            elif command == 'config':
                await run_config()
            elif command == 'health':
                await run_health()
            elif command == 'setup':
                await run_setup()
            elif command == 'bot':
                await start_telegram_bot()
            elif command == 'import':
                await run_import()
            elif command == 'backup':
                await run_backup()
            elif command == 'report':
                await run_report()
            elif command == '':
                continue
            else:
                print(f"❓ Unknown command: {command}")
                print("💡 Type 'help' for available commands")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Telegram BD Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                  # Interactive mode
  python main.py dashboard        # Show analytics dashboard  
  python main.py analyze          # Run AI analysis
  python main.py export           # Export to Google Sheets
  python main.py bot              # Start Telegram bot
  python main.py setup            # Initial setup
        """
    )
    
    parser.add_argument('command', nargs='?', default='interactive',
                       choices=['dashboard', 'analyze', 'export', 'bot', 'setup', 
                               'config', 'status', 'import', 'backup', 'report', 
                               'health', 'interactive'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        if args.command == 'interactive':
            await interactive_mode()
        elif args.command == 'dashboard':
            await run_dashboard()
        elif args.command == 'analyze':
            await run_analysis()
        elif args.command == 'export':
            await run_export()
        elif args.command == 'bot':
            await start_telegram_bot()
        elif args.command == 'setup':
            await run_setup()
        elif args.command == 'config':
            await run_config()
        elif args.command == 'status':
            await run_status()
        elif args.command == 'import':
            await run_import()
        elif args.command == 'backup':
            await run_backup()
        elif args.command == 'report':
            await run_report()
        elif args.command == 'health':
            await run_health()
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Try running: python main.py health")

if __name__ == "__main__":
    asyncio.run(main()) 