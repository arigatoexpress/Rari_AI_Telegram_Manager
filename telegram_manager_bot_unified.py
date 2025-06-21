#!/usr/bin/env python3
"""
Test script for Telegram Manager Bot setup
"""

import os
import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")

    required_packages = [
        "telethon",
        "telegram",
        "openai",
        "dotenv",
        "schedule",
        "asyncio"
    ]

    failed_imports = []

    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            failed_imports.append(package)

    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("✅ All imports successful")
    return True

def test_env_file():
    """Test if .env file exists and has required variables"""
    print("\n🔍 Testing environment configuration...")

    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Run: cp env.example .env")
        return False

    print("✅ .env file exists")

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_API_ID",
        "TELEGRAM_API_HASH",
        "OPENAI_API_KEY",
        "USER_ID"
    ]

    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            print(f"❌ {var} not configured")
            missing_vars.append(var)
        else:
            print(f"✅ {var} configured")

    if missing_vars:
        print(f"\n❌ Missing or invalid variables: {', '.join(missing_vars)}")
        print("Please edit .env file with your actual credentials")
        return False

    print("✅ All environment variables configured")
    return True

def test_data_file():
    """Test if data file can be created"""
    print("\n🔍 Testing data storage...")

    try:
        import json
        from datetime import datetime

        test_data = {
            "notes": [{"timestamp": datetime.now().isoformat(), "text": "test"}],
            "usage": []
        }

        with open("test_data.json", "w") as f:
            json.dump(test_data, f, indent=2)

        with open("test_data.json", "r") as f:
            loaded_data = json.load(f)

        os.remove("test_data.json")

        if loaded_data["notes"][0]["text"] == "test":
            print("✅ Data storage working")
            return True
        else:
            print("❌ Data storage test failed")
            return False

    except Exception as e:
        print(f"❌ Data storage test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Telegram Manager Bot Setup")
    print("=" * 50)

    tests = [
        test_imports,
        test_env_file,
        test_data_file
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("Run: python telegram_manager_bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
