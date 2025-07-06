#!/usr/bin/env python3
"""
Bot Management Script
====================
Simple script to manage the Enhanced BD Bot
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def get_bot_pid():
    """Get the PID of the running bot"""
    try:
        result = subprocess.run(['pgrep', '-f', 'telegram_bd_bot.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            return [int(pid) for pid in pids if pid]
        return []
    except Exception:
        return []

def is_bot_running():
    """Check if the bot is running"""
    return len(get_bot_pid()) > 0

def start_bot():
    """Start the bot"""
    if is_bot_running():
        print("🤖 Bot is already running!")
        show_status()
        return
    
    print("🚀 Starting Unified Telegram Bot...")
    
    # Start the bot in background
    subprocess.Popen([
        sys.executable, 'start_bot.py'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait a moment and check if it started
    time.sleep(3)
    
    if is_bot_running():
        print("✅ Bot started successfully!")
        show_status()
    else:
        print("❌ Failed to start bot. Check logs/bd_bot.log for details")

def stop_bot():
    """Stop the bot"""
    pids = get_bot_pid()
    
    if not pids:
        print("🛑 Bot is not running")
        return
    
    print(f"🛑 Stopping bot (PID: {', '.join(map(str, pids))})")
    
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass  # Process already stopped
    
    # Wait for graceful shutdown
    time.sleep(2)
    
    # Force kill if still running
    remaining_pids = get_bot_pid()
    if remaining_pids:
        print("⚠️ Force stopping bot...")
        for pid in remaining_pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    
    # Clean up lock file
    lock_file = Path("bot.lock")
    if lock_file.exists():
        lock_file.unlink()
    
    print("✅ Bot stopped")

def restart_bot():
    """Restart the bot"""
    print("🔄 Restarting bot...")
    stop_bot()
    time.sleep(1)
    start_bot()

def show_status():
    """Show bot status"""
    pids = get_bot_pid()
    
    print("\n📊 Bot Status Report")
    print("=" * 30)
    
    if pids:
        print(f"Status: ✅ Running")
        print(f"PID(s): {', '.join(map(str, pids))}")
        
        # Check lock file
        lock_file = Path("bot.lock")
        if lock_file.exists():
            try:
                with open(lock_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        print(f"Lock PID: {lines[0].strip()}")
                        print(f"Started: {lines[1].strip()}")
            except Exception:
                pass
        
        # Check log file
        log_file = Path("logs/bot.log")
        if log_file.exists():
            try:
                # Get last few lines
                result = subprocess.run(['tail', '-3', str(log_file)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("\nRecent logs:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            print(f"  {line}")
            except Exception:
                pass
    else:
        print("Status: ❌ Not running")
        
        # Check if lock file exists (stale)
        lock_file = Path("bot.lock")
        if lock_file.exists():
            print("⚠️ Stale lock file found")
    
    print()

def show_logs():
    """Show recent logs"""
    log_file = Path("logs/bot.log")
    
    if not log_file.exists():
        print("❌ Log file not found")
        return
    
    print("📋 Recent Bot Logs:")
    print("=" * 50)
    
    try:
        result = subprocess.run(['tail', '-20', str(log_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Failed to read logs")
    except Exception as e:
        print(f"❌ Error reading logs: {e}")

def cleanup():
    """Clean up stale files"""
    print("🧹 Cleaning up...")
    
    # Remove lock file
    lock_file = Path("bot.lock")
    if lock_file.exists():
        lock_file.unlink()
        print("✅ Removed stale lock file")
    
    # Kill any remaining processes
    pids = get_bot_pid()
    if pids:
        print(f"🛑 Killing remaining processes: {', '.join(map(str, pids))}")
        for pid in pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    
    print("✅ Cleanup complete")

def show_help():
    """Show help message"""
    print("""
🤖 Unified Telegram Bot Management

Commands:
  start     - Start the bot
  stop      - Stop the bot
  restart   - Restart the bot
  status    - Show bot status
  logs      - Show recent logs
  cleanup   - Clean up stale files
  help      - Show this help

Examples:
  python3 manage_bot.py start
  python3 manage_bot.py status
  python3 manage_bot.py logs
    """)

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        start_bot()
    elif command == 'stop':
        stop_bot()
    elif command == 'restart':
        restart_bot()
    elif command == 'status':
        show_status()
    elif command == 'logs':
        show_logs()
    elif command == 'cleanup':
        cleanup()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main() 