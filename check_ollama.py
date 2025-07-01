#!/usr/bin/env python3
"""
Ollama Status Checker
====================
Check if Ollama is running and test AI functionality.
"""

import os
import requests
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔍 Checking Ollama Status...")
    
    # Check server
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama server is running")
        else:
            print("❌ Ollama server error")
            return False
    except:
        print("❌ Ollama server not running")
        print("Start with: ollama serve")
        return False
    
    # Check models
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        models = response.json().get('models', [])
        required_model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        model_found = any(m.get('name') == required_model for m in models)
        if model_found:
            print(f"✅ Model {required_model} available")
        else:
            print(f"⚠️  Model {required_model} not found")
            print(f"Pull with: ollama pull {required_model}")
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False
    
    print("🎉 Ollama is ready!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 