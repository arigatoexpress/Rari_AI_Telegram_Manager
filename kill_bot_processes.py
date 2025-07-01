#!/usr/bin/env python3
"""
Kill Bot Processes
=================
Kills any running Telegram bot processes.
"""

import os
import subprocess
import signal
import psutil

def kill_bot_processes():
    """Kill any running bot processes"""
    print("🛑 Killing bot processes...")
    print("=" * 40)
    
    killed_processes = []
    
    # Look for Python processes that might be running bots
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('bot' in arg.lower() for arg in cmdline if arg):
                # Check if it's our bot
                if any('telegram' in arg.lower() for arg in cmdline if arg):
                    print(f"🔍 Found bot process: PID {proc.info['pid']}")
                    print(f"   Command: {' '.join(cmdline)}")
                    
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                        killed_processes.append(proc.info['pid'])
                        print(f"   ✅ Terminated PID {proc.info['pid']}")
                    except psutil.TimeoutExpired:
                        proc.kill()
                        killed_processes.append(proc.info['pid'])
                        print(f"   ⚡ Killed PID {proc.info['pid']}")
                    except Exception as e:
                        print(f"   ❌ Failed to kill PID {proc.info['pid']}: {e}")
                        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Also check for processes by name
    bot_process_names = ['python', 'python3']
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] in bot_process_names:
                cmdline = proc.cmdline()
                if any('telegram' in arg.lower() for arg in cmdline if arg):
                    if proc.info['pid'] not in killed_processes:
                        print(f"🔍 Found additional bot process: PID {proc.info['pid']}")
                        try:
                            proc.terminate()
                            proc.wait(timeout=5)
                            killed_processes.append(proc.info['pid'])
                            print(f"   ✅ Terminated PID {proc.info['pid']}")
                        except psutil.TimeoutExpired:
                            proc.kill()
                            killed_processes.append(proc.info['pid'])
                            print(f"   ⚡ Killed PID {proc.info['pid']}")
                        except Exception as e:
                            print(f"   ❌ Failed to kill PID {proc.info['pid']}: {e}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    print("\n" + "=" * 40)
    print(f"📊 Summary: Killed {len(killed_processes)} bot processes")
    
    if killed_processes:
        print("✅ All bot processes terminated")
    else:
        print("ℹ️ No bot processes found running")
    
    return killed_processes

def check_running_processes():
    """Check for any remaining bot processes"""
    print("\n🔍 Checking for remaining bot processes...")
    
    remaining = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('telegram' in arg.lower() for arg in cmdline if arg):
                remaining.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if remaining:
        print(f"⚠️ Found {len(remaining)} remaining bot processes: {remaining}")
    else:
        print("✅ No bot processes remaining")
    
    return remaining

if __name__ == "__main__":
    try:
        killed = kill_bot_processes()
        check_running_processes()
        
        print("\n🚀 Ready to start optimized bot!")
        print("Run: python start_optimized_bot.py")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}") 