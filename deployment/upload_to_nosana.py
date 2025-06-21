#!/usr/bin/env python3
"""
Upload Script for Nosana GPU Instance
=====================================
Helper script to upload your Telegram Manager Bot to Nosana.
"""

import os
import subprocess
import zipfile
from pathlib import Path
from typing import List

class NosanaUploader:
    """Upload files to Nosana GPU instance"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.required_files = [
            # Core application files
            "run.py",
            "telegram_manager_bot.py",
            "telegram_manager_bot_unified.py",
            "telegram_message_reader.py",
            "google_sheets_integration.py",
            "elizao_agentic_framework.py",
            "depin_solutions.py",
            "deploy_to_depin.py",
            
            # Configuration files
            "requirements.txt",
            "env.example",
            ".env",
            
            # Deployment files
            "Dockerfile",
            "docker-compose.yml",
            "deploy.sh",
            "supervisor.conf",
            "monitor.sh",
            
            # Google Sheets integration
            "google_service_account.json",
            
            # Documentation
            "README.md",
            "README_ENHANCED.md",
            "README_REDUNDANCY.md"
        ]
        
        self.optional_files = [
            # Test files
            "test_*.py",
            "setup_*.py",
            
            # Other scripts
            "*.sh",
            "*.md"
        ]
    
    def check_files(self) -> tuple[List[str], List[str]]:
        """Check which required files exist"""
        missing_files = []
        existing_files = []
        
        for file_path in self.required_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        return existing_files, missing_files
    
    def create_upload_package(self, include_optional: bool = False) -> str:
        """Create a zip package for upload"""
        package_name = "telegram-manager-bot-nosana.zip"
        
        with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add required files
            existing_files, missing_files = self.check_files()
            
            for file_path in existing_files:
                zipf.write(file_path, file_path)
                print(f"✅ Added: {file_path}")
            
            # Add optional files if requested
            if include_optional:
                for pattern in self.optional_files:
                    for file_path in self.project_dir.glob(pattern):
                        if file_path.is_file() and file_path.name not in existing_files:
                            zipf.write(file_path, file_path.name)
                            print(f"📁 Added optional: {file_path.name}")
            
            # Add missing files info
            if missing_files:
                missing_info = "\n".join([f"Missing: {f}" for f in missing_files])
                zipf.writestr("MISSING_FILES.txt", missing_info)
                print(f"⚠️  Missing files noted in package")
        
        return package_name
    
    def generate_upload_instructions(self) -> str:
        """Generate upload instructions"""
        instructions = """
🚀 UPLOAD INSTRUCTIONS FOR NOSANA GPU
=====================================

Method 1: Direct Upload (Recommended)
-------------------------------------
1. Create upload package:
   python upload_to_nosana.py

2. Upload to your Nosana instance:
   - Use Nosana dashboard file upload
   - Or use SCP/rsync if you have SSH access
   - Or use cloud storage (Google Drive, Dropbox)

3. On your Nosana instance:
   unzip telegram-manager-bot-nosana.zip
   cd telegram-manager-bot-nosana
   chmod +x deploy.sh
   ./deploy.sh

Method 2: Git Repository
------------------------
1. Push your code to GitHub/GitLab
2. On Nosana instance:
   git clone https://github.com/yourusername/tg_manager_v2.git
   cd tg_manager_v2
   chmod +x deploy.sh
   ./deploy.sh

Method 3: Manual File Transfer
-----------------------------
Upload these essential files:
- All .py files
- requirements.txt
- .env (configured)
- google_service_account.json
- Dockerfile
- docker-compose.yml
- deploy.sh

PREREQUISITES ON NOSANA INSTANCE:
================================
1. Docker and Docker Compose installed
2. NVIDIA Docker runtime (for GPU)
3. Python 3.11+
4. Git (for cloning)

ENVIRONMENT SETUP:
=================
1. Create .env file with your configuration:
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=your_phone
   USER_ID=your_user_id
   GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
   NOSANA_API_KEY=your_nosana_key

2. Upload google_service_account.json for Google Sheets

DEPLOYMENT STEPS:
================
1. Upload files to Nosana instance
2. Extract/unzip if needed
3. Run: chmod +x deploy.sh
4. Run: ./deploy.sh
5. Monitor: docker-compose logs -f
6. For 24/7 monitoring: nohup ./monitor.sh &

TROUBLESHOOTING:
===============
- Check logs: docker-compose logs
- Restart services: docker-compose restart
- Check GPU: nvidia-smi
- Check disk space: df -h
- Check memory: free -h
"""
        return instructions
    
    def create_quick_setup_script(self) -> str:
        """Create a quick setup script for Nosana"""
        script = """#!/bin/bash
# Quick Setup Script for Nosana GPU

echo "🚀 Quick Setup for Telegram Manager Bot on Nosana GPU"

# Check if running on Nosana
if [ -n "$NOSANA_API_KEY" ]; then
    echo "✅ Detected Nosana environment"
else
    echo "⚠️  NOSANA_API_KEY not found (this is okay for testing)"
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker not found. Installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is installed"
else
    echo "❌ Docker Compose not found. Installing..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Check NVIDIA Docker
if docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA Docker runtime is working"
else
    echo "⚠️  NVIDIA Docker runtime not available (GPU features may not work)"
fi

# Create necessary directories
mkdir -p logs data

# Set permissions
chmod +x deploy.sh monitor.sh

echo "🎉 Quick setup complete!"
echo "Next steps:"
echo "1. Configure your .env file"
echo "2. Run: ./deploy.sh"
echo "3. Monitor: docker-compose logs -f"
"""
        return script

def main():
    """Main upload function"""
    print("📦 NOSANA UPLOAD HELPER")
    print("=" * 50)
    
    uploader = NosanaUploader()
    
    while True:
        print("\n📋 Available Options:")
        print("1. Check required files")
        print("2. Create upload package")
        print("3. Show upload instructions")
        print("4. Create quick setup script")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            existing_files, missing_files = uploader.check_files()
            print(f"\n✅ Found {len(existing_files)} files:")
            for file_path in existing_files:
                print(f"   {file_path}")
            
            if missing_files:
                print(f"\n❌ Missing {len(missing_files)} files:")
                for file_path in missing_files:
                    print(f"   {file_path}")
        
        elif choice == "2":
            include_optional = input("Include optional files? (y/n): ").strip().lower() == 'y'
            package_name = uploader.create_upload_package(include_optional)
            print(f"\n✅ Created upload package: {package_name}")
            print(f"📁 Size: {Path(package_name).stat().st_size / 1024:.1f} KB")
        
        elif choice == "3":
            print(uploader.generate_upload_instructions())
        
        elif choice == "4":
            script_content = uploader.create_quick_setup_script()
            with open("quick_setup.sh", 'w') as f:
                f.write(script_content)
            os.chmod("quick_setup.sh", 0o755)
            print("✅ Created quick_setup.sh")
            print("Upload this script to your Nosana instance and run: ./quick_setup.sh")
        
        elif choice == "5":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main() 