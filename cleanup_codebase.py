#!/usr/bin/env python3
"""
Codebase Cleanup Script
=======================
Identifies and removes unnecessary files from the codebase.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set

def get_unnecessary_files() -> Set[str]:
    """Get list of files that can be safely removed"""
    unnecessary_files = {
        # Old bot versions
        'simple_bot.py',
        'telegram_manager_bot.py',
        'telegram_bot_consolidated.py',
        'start_async_bot.py',
        'start_enhanced_bot.py',
        'start_consolidated_bot.py',
        
        # Old analyzers
        'enhanced_chat_analyzer.py',
        'enhanced_ai_analyzer.py',
        'automated_chat_analyzer.py',
        'automated_intelligence_system.py',
        
        # Old managers
        'enhanced_startup_manager.py',
        'automated_update_manager.py',
        'ai_performance_optimizer.py',
        
        # Old integrations
        'google_sheets_database.py',
        'google_sheets_integration.py',
        'chat_history_manager.py',
        'auto_sync_manager.py',
        
        # Old clients
        'nosana_client.py',
        'atoma_client.py',
        
        # Old monitors
        'sui_monitor.py',
        
        # Old READMEs
        'README_ENHANCED_BOT.md',
        'README_CONSOLIDATED.md',
        'README_UNIFIED.md',
        'README_AUTOMATED_SYSTEM.md',
        'README_OPTIMIZED.md',
        'README_COMPLETE.md',
        
        # Old logs
        'simple_bot.log',
        'bot_consolidated.log',
        'enhanced_startup.log',
        'ai_optimizer.log',
        'update_manager.log',
        'bot.log',
        
        # Old startup scripts
        'telegram_message_reader.py',
        'telethon_data_fetcher.py',
        'team_access_manager.py',
        'whitelist_manager.py',
    }
    
    return unnecessary_files

def get_unnecessary_directories() -> Set[str]:
    """Get list of directories that can be safely removed"""
    unnecessary_dirs = {
        'ai_cache',
        'cache',
        'temp_updates',
        'whitelist_backups',
        'backups',
    }
    
    return unnecessary_dirs

def cleanup_codebase():
    """Clean up the codebase by removing unnecessary files"""
    print("🧹 Starting codebase cleanup...")
    print("=" * 50)
    
    # Get lists of unnecessary files and directories
    unnecessary_files = get_unnecessary_files()
    unnecessary_dirs = get_unnecessary_directories()
    
    # Track what we're removing
    removed_files = []
    removed_dirs = []
    failed_removals = []
    
    # Remove unnecessary files
    print("\n📁 Removing unnecessary files:")
    for filename in unnecessary_files:
        filepath = Path(filename)
        if filepath.exists():
            try:
                filepath.unlink()
                removed_files.append(filename)
                print(f"  ✅ Removed: {filename}")
            except Exception as e:
                failed_removals.append((filename, str(e)))
                print(f"  ❌ Failed to remove {filename}: {e}")
        else:
            print(f"  ⚠️ Not found: {filename}")
    
    # Remove unnecessary directories
    print("\n📂 Removing unnecessary directories:")
    for dirname in unnecessary_dirs:
        dirpath = Path(dirname)
        if dirpath.exists() and dirpath.is_dir():
            try:
                shutil.rmtree(dirpath)
                removed_dirs.append(dirname)
                print(f"  ✅ Removed: {dirname}")
            except Exception as e:
                failed_removals.append((dirname, str(e)))
                print(f"  ❌ Failed to remove {dirname}: {e}")
        else:
            print(f"  ⚠️ Not found: {dirname}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Cleanup Summary:")
    print(f"  Files removed: {len(removed_files)}")
    print(f"  Directories removed: {len(removed_dirs)}")
    print(f"  Failed removals: {len(failed_removals)}")
    
    if removed_files:
        print("\n🗑️ Removed files:")
        for filename in removed_files:
            print(f"  • {filename}")
    
    if removed_dirs:
        print("\n🗂️ Removed directories:")
        for dirname in removed_dirs:
            print(f"  • {dirname}")
    
    if failed_removals:
        print("\n❌ Failed removals:")
        for item, error in failed_removals:
            print(f"  • {item}: {error}")
    
    print("\n✅ Cleanup completed!")
    print("\n📋 Remaining essential files:")
    essential_files = [
        'telegram_bot_optimized.py',
        'start_optimized_bot.py',
        'core/data_manager.py',
        'core/ai_analyzer.py',
        'core/__init__.py',
        'ollama_client.py',
        'requirements.txt',
        'env.template',
        'README.md',
        'LICENSE',
        '.gitignore'
    ]
    
    for filename in essential_files:
        if Path(filename).exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ Missing: {filename}")

if __name__ == "__main__":
    cleanup_codebase() 