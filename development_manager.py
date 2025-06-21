#!/usr/bin/env python3
"""
Development Manager for Telegram Manager Bot v2.0.0
==================================================
Manage development workflow with the consolidated codebase structure.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class DevelopmentManager:
    """Manage development workflow for the consolidated codebase"""
    
    def __init__(self):
        self.root_dir = Path.cwd()
        self.config = {
            "version": "2.0.0",
            "project_name": "Telegram Manager Bot",
            "main_bot_file": "telegram_manager_bot_unified.py",
            "test_suite": "test_suite.py",
            "deployment_script": "deploy_to_nosana.py",
            "requirements_file": "requirements.txt",
            "env_template": "env.example"
        }
        
        # Development commands
        self.commands = {
            "start": "Start the bot in development mode",
            "test": "Run comprehensive test suite",
            "deploy": "Deploy to Nosana GPU",
            "status": "Check bot and system status",
            "setup": "Setup development environment",
            "clean": "Clean temporary files",
            "docs": "Generate documentation",
            "monitor": "Monitor bot performance",
            "backup": "Create backup of configuration",
            "restore": "Restore from backup"
        }
    
    def print_banner(self):
        """Print development manager banner"""
        print("🚀 Telegram Manager Bot v2.0.0 - Development Manager")
        print("=" * 60)
        print(f"📁 Project: {self.config['project_name']}")
        print(f"🔧 Version: {self.config['version']}")
        print(f"📂 Root: {self.root_dir}")
        print("=" * 60)
    
    def check_structure(self) -> bool:
        """Check if the consolidated structure is intact"""
        print("🔍 Checking project structure...")
        
        required_dirs = [
            "deployment",
            "testing", 
            "docs",
            "config",
            "scripts",
            "deployment_package"
        ]
        
        required_files = [
            "telegram_manager_bot_unified.py",
            "requirements.txt",
            "env.example",
            "test_suite.py",
            "deploy_to_nosana.py"
        ]
        
        missing_dirs = []
        missing_files = []
        
        for dir_name in required_dirs:
            if not (self.root_dir / dir_name).exists():
                missing_dirs.append(dir_name)
        
        for file_name in required_files:
            if not (self.root_dir / file_name).exists():
                missing_files.append(file_name)
        
        if missing_dirs or missing_files:
            print("❌ Structure issues found:")
            if missing_dirs:
                print(f"   Missing directories: {', '.join(missing_dirs)}")
            if missing_files:
                print(f"   Missing files: {', '.join(missing_files)}")
            return False
        
        print("✅ Project structure is intact")
        return True
    
    def start_development(self):
        """Start the bot in development mode"""
        print("🚀 Starting bot in development mode...")
        
        # Check if .env exists
        env_file = self.root_dir / ".env"
        if not env_file.exists():
            print("⚠️  .env file not found. Creating from template...")
            self.setup_environment()
        
        # Start the bot
        try:
            print("🤖 Starting Telegram Manager Bot...")
            subprocess.run([sys.executable, self.config["main_bot_file"]], check=True)
        except KeyboardInterrupt:
            print("\n⏹️  Bot stopped by user")
        except Exception as e:
            print(f"❌ Error starting bot: {e}")
    
    def run_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Running comprehensive test suite...")
        
        test_files = [
            "test_suite.py",
            "test_bot_status.py"
        ]
        
        for test_file in test_files:
            test_path = self.root_dir / test_file
            if test_path.exists():
                print(f"📋 Running {test_file}...")
                try:
                    result = subprocess.run([sys.executable, str(test_path)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {test_file} passed")
                    else:
                        print(f"❌ {test_file} failed")
                        print(result.stderr)
                except Exception as e:
                    print(f"❌ Error running {test_file}: {e}")
            else:
                print(f"⚠️  {test_file} not found")
        
        # Run tests in testing directory
        testing_dir = self.root_dir / "testing"
        if testing_dir.exists():
            print("📁 Running tests from testing/ directory...")
            for test_file in testing_dir.glob("test_*.py"):
                print(f"📋 Running {test_file.name}...")
                try:
                    result = subprocess.run([sys.executable, str(test_file)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {test_file.name} passed")
                    else:
                        print(f"❌ {test_file.name} failed")
                except Exception as e:
                    print(f"❌ Error running {test_file.name}: {e}")
    
    def deploy_to_nosana(self):
        """Deploy to Nosana GPU"""
        print("🚀 Deploying to Nosana GPU...")
        
        deploy_script = self.root_dir / self.config["deployment_script"]
        if not deploy_script.exists():
            print(f"❌ Deployment script not found: {deploy_script}")
            return
        
        try:
            print("📦 Starting Nosana deployment...")
            subprocess.run([sys.executable, str(deploy_script)], check=True)
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
    
    def check_status(self):
        """Check bot and system status"""
        print("📊 Checking system status...")
        
        # Check bot status
        status_script = self.root_dir / "test_bot_status.py"
        if status_script.exists():
            print("🤖 Checking bot status...")
            try:
                result = subprocess.run([sys.executable, str(status_script)], 
                                      capture_output=True, text=True)
                print(result.stdout)
            except Exception as e:
                print(f"❌ Error checking bot status: {e}")
        
        # Check directory structure
        print("\n📁 Directory structure:")
        for item in self.root_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                file_count = len(list(item.glob('*')))
                print(f"   {item.name}/ ({file_count} items)")
        
        # Check environment
        print("\n🔧 Environment check:")
        env_file = self.root_dir / ".env"
        if env_file.exists():
            print("   ✅ .env file exists")
        else:
            print("   ❌ .env file missing")
        
        requirements_file = self.root_dir / self.config["requirements_file"]
        if requirements_file.exists():
            print("   ✅ requirements.txt exists")
        else:
            print("   ❌ requirements.txt missing")
    
    def setup_environment(self):
        """Setup development environment"""
        print("🔧 Setting up development environment...")
        
        # Copy env template
        env_template = self.root_dir / self.config["env_template"]
        env_file = self.root_dir / ".env"
        
        if env_template.exists() and not env_file.exists():
            import shutil
            shutil.copy2(env_template, env_file)
            print("✅ Created .env from template")
            print("⚠️  Please edit .env with your credentials")
        elif env_file.exists():
            print("✅ .env file already exists")
        else:
            print("❌ env.example template not found")
        
        # Install requirements
        requirements_file = self.root_dir / self.config["requirements_file"]
        if requirements_file.exists():
            print("📦 Installing requirements...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                              check=True)
                print("✅ Requirements installed")
            except Exception as e:
                print(f"❌ Error installing requirements: {e}")
        else:
            print("❌ requirements.txt not found")
    
    def clean_temporary_files(self):
        """Clean temporary files"""
        print("🧹 Cleaning temporary files...")
        
        # Remove Python cache
        for cache_dir in self.root_dir.rglob("__pycache__"):
            import shutil
            shutil.rmtree(cache_dir)
            print(f"🗑️  Removed {cache_dir}")
        
        # Remove .pyc files
        for pyc_file in self.root_dir.rglob("*.pyc"):
            pyc_file.unlink()
            print(f"🗑️  Removed {pyc_file}")
        
        # Clean logs directory
        logs_dir = self.root_dir / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                log_file.unlink()
                print(f"🗑️  Removed {log_file}")
        
        print("✅ Cleanup complete")
    
    def generate_documentation(self):
        """Generate documentation"""
        print("📚 Generating documentation...")
        
        # Create development guide
        dev_guide = """# Development Guide v2.0.0

## 🚀 Quick Development Commands

```bash
# Start development
python development_manager.py start

# Run tests
python development_manager.py test

# Deploy to Nosana
python development_manager.py deploy

# Check status
python development_manager.py status
```

## 📁 Development Structure

- **Root Directory**: Core application files
- **deployment/**: Deployment and setup scripts
- **testing/**: Test files and demos
- **docs/**: Documentation files
- **config/**: Configuration files
- **scripts/**: Utility scripts
- **deployment_package/**: Clean deployment package

## 🔧 Development Workflow

1. **Setup**: `python development_manager.py setup`
2. **Develop**: Edit core files in root directory
3. **Test**: `python development_manager.py test`
4. **Deploy**: `python development_manager.py deploy`
5. **Monitor**: `python development_manager.py status`

## 📊 Monitoring

- Check bot status: `python test_bot_status.py`
- Run test suite: `python test_suite.py`
- Monitor logs: Check `logs/` directory
- Check configuration: Review `config/` directory

## 🚀 Deployment

### Local Development
```bash
python telegram_manager_bot_unified.py
```

### Nosana GPU
```bash
python deploy_to_nosana.py
```

### Docker
```bash
cd deployment_package/
docker-compose up -d
```

## 🔒 Security

- Keep `.env` file secure
- Use team access management
- Monitor API usage
- Regular backups

## 📞 Support

- Check `docs/` for detailed documentation
- Run tests for diagnostics
- Use development manager for workflow
"""
        
        with open(self.root_dir / "DEVELOPMENT_GUIDE.md", 'w') as f:
            f.write(dev_guide)
        
        print("✅ Documentation generated: DEVELOPMENT_GUIDE.md")
    
    def monitor_performance(self):
        """Monitor bot performance"""
        print("📊 Monitoring bot performance...")
        
        # Check if bot is running
        try:
            import psutil
            bot_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'])
                        if 'telegram_manager_bot' in cmdline:
                            bot_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if bot_processes:
                print("🤖 Bot processes running:")
                for proc in bot_processes:
                    print(f"   PID {proc['pid']}: {proc['cmdline']}")
            else:
                print("🤖 No bot processes running")
        except ImportError:
            print("⚠️  psutil not installed. Install with: pip install psutil")
        
        # Check log files
        logs_dir = self.root_dir / "logs"
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                print(f"📋 Log files found: {len(log_files)}")
                for log_file in log_files:
                    size = log_file.stat().st_size
                    print(f"   {log_file.name}: {size} bytes")
            else:
                print("📋 No log files found")
    
    def create_backup(self):
        """Create backup of configuration"""
        print("💾 Creating backup...")
        
        backup_dir = self.root_dir / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup config files
        config_dir = self.root_dir / "config"
        if config_dir.exists():
            import shutil
            backup_config = backup_dir / "config_backup"
            if backup_config.exists():
                shutil.rmtree(backup_config)
            shutil.copytree(config_dir, backup_config)
            print("✅ Configuration backed up")
        
        # Backup .env
        env_file = self.root_dir / ".env"
        if env_file.exists():
            import shutil
            shutil.copy2(env_file, backup_dir / ".env.backup")
            print("✅ .env backed up")
        
        print(f"💾 Backup created in: {backup_dir}")
    
    def restore_backup(self):
        """Restore from backup"""
        print("🔄 Restoring from backup...")
        
        backup_dir = self.root_dir / "backup"
        if not backup_dir.exists():
            print("❌ No backup found")
            return
        
        # Restore config
        backup_config = backup_dir / "config_backup"
        if backup_config.exists():
            import shutil
            config_dir = self.root_dir / "config"
            if config_dir.exists():
                shutil.rmtree(config_dir)
            shutil.copytree(backup_config, config_dir)
            print("✅ Configuration restored")
        
        # Restore .env
        backup_env = backup_dir / ".env.backup"
        if backup_env.exists():
            import shutil
            shutil.copy2(backup_env, self.root_dir / ".env")
            print("✅ .env restored")
        
        print("✅ Restore complete")
    
    def show_help(self):
        """Show help information"""
        print("\n📋 Available Commands:")
        for command, description in self.commands.items():
            print(f"   {command:10} - {description}")
        
        print("\n💡 Examples:")
        print("   python development_manager.py start")
        print("   python development_manager.py test")
        print("   python development_manager.py deploy")
        print("   python development_manager.py status")
    
    def run(self, command: str):
        """Run development command"""
        self.print_banner()
        
        if not self.check_structure():
            print("❌ Project structure issues detected. Please fix before continuing.")
            return
        
        if command == "start":
            self.start_development()
        elif command == "test":
            self.run_tests()
        elif command == "deploy":
            self.deploy_to_nosana()
        elif command == "status":
            self.check_status()
        elif command == "setup":
            self.setup_environment()
        elif command == "clean":
            self.clean_temporary_files()
        elif command == "docs":
            self.generate_documentation()
        elif command == "monitor":
            self.monitor_performance()
        elif command == "backup":
            self.create_backup()
        elif command == "restore":
            self.restore_backup()
        elif command == "help":
            self.show_help()
        else:
            print(f"❌ Unknown command: {command}")
            self.show_help()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Development Manager for Telegram Manager Bot v2.0.0")
    parser.add_argument("command", nargs="?", default="help", 
                       choices=["start", "test", "deploy", "status", "setup", "clean", "docs", "monitor", "backup", "restore", "help"],
                       help="Development command to run")
    
    args = parser.parse_args()
    
    manager = DevelopmentManager()
    manager.run(args.command)

if __name__ == "__main__":
    main() 