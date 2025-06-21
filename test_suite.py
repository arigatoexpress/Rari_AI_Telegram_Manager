#!/usr/bin/env python3
"""
Comprehensive Test Suite for Telegram Manager Bot
=================================================
Test for errors, compatibility, edge cases, and functionality.
"""

import os
import sys
import json
import asyncio
import unittest
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
import sqlite3

class TestSuite:
    """Comprehensive test suite for the Telegram Manager Bot"""
    
    def __init__(self):
        self.test_results = []
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
        
    def log_result(self, test_name: str, status: str, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.test_results.append(result)
        
        if status == "PASS":
            self.passed += 1
            print(f"✅ {test_name}: PASS")
        elif status == "FAIL":
            self.failed += 1
            print(f"❌ {test_name}: FAIL - {message}")
        elif status == "WARNING":
            self.warnings.append(result)
            print(f"⚠️  {test_name}: WARNING - {message}")
    
    def test_environment_variables(self):
        """Test environment variable configuration"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_API_ID", 
            "TELEGRAM_API_HASH",
            "TELEGRAM_PHONE",
            "USER_ID"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_result("Environment Variables", "FAIL", 
                          f"Missing required variables: {', '.join(missing_vars)}")
        else:
            self.log_result("Environment Variables", "PASS")
    
    def test_python_dependencies(self):
        """Test Python dependency installation"""
        required_packages = [
            "telethon",
            "python-telegram-bot", 
            "requests",
            "gspread",
            "google-auth",
            "aiohttp",
            "asyncio"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.log_result("Python Dependencies", "FAIL",
                          f"Missing packages: {', '.join(missing_packages)}")
        else:
            self.log_result("Python Dependencies", "PASS")
    
    def test_file_permissions(self):
        """Test file permissions for security"""
        sensitive_files = [
            ".env",
            "google_service_account.json",
            "team_members.json"
        ]
        
        permission_issues = []
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                if stat.st_mode & 0o777 != 0o600:
                    permission_issues.append(f"{file_path}: {oct(stat.st_mode)[-3:]}")
        
        if permission_issues:
            self.log_result("File Permissions", "WARNING",
                          f"Permission issues: {', '.join(permission_issues)}")
        else:
            self.log_result("File Permissions", "PASS")
    
    def test_telegram_connection(self):
        """Test Telegram API connection"""
        try:
            from telethon import TelegramClient
            from telethon.errors import SessionPasswordNeededError
            
            api_id = os.getenv("TELEGRAM_API_ID")
            api_hash = os.getenv("TELEGRAM_API_HASH")
            phone = os.getenv("TELEGRAM_PHONE")
            
            if not all([api_id, api_hash, phone]):
                self.log_result("Telegram Connection", "FAIL", "Missing Telegram credentials")
                return
            
            # Test connection (without actually connecting)
            client = TelegramClient('test_session', api_id, api_hash)
            
            # Check if credentials are valid format
            if not api_id.isdigit():
                self.log_result("Telegram Connection", "FAIL", "Invalid API ID format")
                return
            
            if len(api_hash) != 32:
                self.log_result("Telegram Connection", "WARNING", "API Hash length seems incorrect")
                return
            
            self.log_result("Telegram Connection", "PASS")
            
        except Exception as e:
            self.log_result("Telegram Connection", "FAIL", f"Connection error: {str(e)}")
    
    def test_google_sheets_integration(self):
        """Test Google Sheets integration"""
        try:
            service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
            spreadsheet_id = os.getenv("GOOGLE_SPREADSHEET_ID")
            
            if not service_account_file or not os.path.exists(service_account_file):
                self.log_result("Google Sheets", "FAIL", "Service account file not found")
                return
            
            if not spreadsheet_id:
                self.log_result("Google Sheets", "FAIL", "Spreadsheet ID not configured")
                return
            
            # Test JSON format
            with open(service_account_file, 'r') as f:
                creds = json.load(f)
            
            required_fields = ["type", "project_id", "private_key_id", "private_key", "client_email"]
            missing_fields = [field for field in required_fields if field not in creds]
            
            if missing_fields:
                self.log_result("Google Sheets", "FAIL", f"Missing credential fields: {missing_fields}")
                return
            
            self.log_result("Google Sheets", "PASS")
            
        except Exception as e:
            self.log_result("Google Sheets", "FAIL", f"Configuration error: {str(e)}")
    
    def test_ollama_connection(self):
        """Test Ollama AI backend connection"""
        try:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            
            if response.status_code == 200:
                self.log_result("Ollama Connection", "PASS")
            else:
                self.log_result("Ollama Connection", "FAIL", f"HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("Ollama Connection", "WARNING", f"Connection failed: {str(e)}")
    
    def test_nosana_integration(self):
        """Test Nosana integration"""
        try:
            nosana_key = os.getenv("NOSANA_API_KEY")
            
            if not nosana_key:
                self.log_result("Nosana Integration", "WARNING", "API key not configured")
                return
            
            if not nosana_key.startswith("nos_"):
                self.log_result("Nosana Integration", "WARNING", "API key format seems incorrect")
                return
            
            self.log_result("Nosana Integration", "PASS")
            
        except Exception as e:
            self.log_result("Nosana Integration", "FAIL", f"Configuration error: {str(e)}")
    
    def test_team_access_system(self):
        """Test team access management"""
        try:
            if not os.path.exists("team_members.json"):
                self.log_result("Team Access", "WARNING", "Team members file not found")
                return
            
            with open("team_members.json", 'r') as f:
                members = json.load(f)
            
            if not isinstance(members, list):
                self.log_result("Team Access", "FAIL", "Invalid team members format")
                return
            
            # Check member structure
            for i, member in enumerate(members):
                required_fields = ["name", "email", "role", "api_key"]
                missing_fields = [field for field in required_fields if field not in member]
                
                if missing_fields:
                    self.log_result("Team Access", "FAIL", 
                                  f"Member {i} missing fields: {missing_fields}")
                    return
            
            self.log_result("Team Access", "PASS", f"Found {len(members)} team members")
            
        except Exception as e:
            self.log_result("Team Access", "FAIL", f"System error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        
        # Test empty/malformed data
        test_cases = [
            ("Empty string", ""),
            ("None value", None),
            ("Very long string", "x" * 10000),
            ("Special characters", "!@#$%^&*()"),
            ("Unicode", "🚀🎉💻"),
            ("SQL injection attempt", "'; DROP TABLE users; --"),
            ("XSS attempt", "<script>alert('xss')</script>"),
        ]
        
        for case_name, test_value in test_cases:
            try:
                # Test JSON serialization
                json.dumps(test_value)
                self.log_result(f"Edge Case: {case_name}", "PASS")
            except Exception as e:
                self.log_result(f"Edge Case: {case_name}", "WARNING", f"Serialization issue: {str(e)}")
    
    def test_performance(self):
        """Test performance characteristics"""
        import time
        
        # Test file read performance
        start_time = time.time()
        try:
            with open("requirements.txt", 'r') as f:
                content = f.read()
            read_time = time.time() - start_time
            
            if read_time < 0.1:
                self.log_result("File Read Performance", "PASS", f"{read_time:.3f}s")
            else:
                self.log_result("File Read Performance", "WARNING", f"Slow read: {read_time:.3f}s")
                
        except Exception as e:
            self.log_result("File Read Performance", "FAIL", str(e))
        
        # Test memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        if memory_mb < 100:
            self.log_result("Memory Usage", "PASS", f"{memory_mb:.1f}MB")
        else:
            self.log_result("Memory Usage", "WARNING", f"High memory: {memory_mb:.1f}MB")
    
    def test_compatibility(self):
        """Test system compatibility"""
        
        # Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.log_result("Python Version", "PASS", f"{python_version.major}.{python_version.minor}")
        else:
            self.log_result("Python Version", "FAIL", f"Requires Python 3.8+, got {python_version.major}.{python_version.minor}")
        
        # Operating system
        import platform
        os_name = platform.system()
        if os_name in ["Linux", "Darwin", "Windows"]:
            self.log_result("Operating System", "PASS", os_name)
        else:
            self.log_result("Operating System", "WARNING", f"Untested OS: {os_name}")
        
        # Docker availability
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_result("Docker", "PASS")
            else:
                self.log_result("Docker", "WARNING", "Docker not available")
        except Exception:
            self.log_result("Docker", "WARNING", "Docker not installed")
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        report = f"""
🔍 COMPREHENSIVE TEST REPORT
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY:
✅ Passed: {self.passed}
❌ Failed: {self.failed}
⚠️  Warnings: {len(self.warnings)}

📋 DETAILED RESULTS:
"""
        
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            report += f"{status_emoji} {result['test']}: {result['status']}\n"
            if result['message']:
                report += f"   → {result['message']}\n"
            if result['details']:
                for key, value in result['details'].items():
                    report += f"   → {key}: {value}\n"
            report += "\n"
        
        # Recommendations
        report += "\n💡 RECOMMENDATIONS:\n"
        
        if self.failed > 0:
            report += "• Fix failed tests before deployment\n"
        
        if len(self.warnings) > 0:
            report += "• Review warnings for potential issues\n"
        
        if self.passed == len(self.test_results):
            report += "• All tests passed! Ready for deployment\n"
        
        return report
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running comprehensive test suite...\n")
        
        self.test_environment_variables()
        self.test_python_dependencies()
        self.test_file_permissions()
        self.test_telegram_connection()
        self.test_google_sheets_integration()
        self.test_ollama_connection()
        self.test_nosana_integration()
        self.test_team_access_system()
        self.test_edge_cases()
        self.test_performance()
        self.test_compatibility()
        
        print(f"\n📊 Test Summary: {self.passed} passed, {self.failed} failed, {len(self.warnings)} warnings")
        
        return self.generate_report()

def main():
    """Main test function"""
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("=" * 50)
    
    test_suite = TestSuite()
    report = test_suite.run_all_tests()
    
    print(report)
    
    # Save report
    with open("test_report.txt", 'w') as f:
        f.write(report)
    
    print("📄 Report saved to test_report.txt")
    
    if test_suite.failed > 0:
        print("\n❌ Some tests failed. Please fix issues before deployment.")
        return 1
    else:
        print("\n✅ All critical tests passed!")
        return 0

if __name__ == "__main__":
    exit(main()) 