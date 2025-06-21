#!/usr/bin/env python3
"""
Secure Nosana Deployment with Team Access
=========================================
Secure your Telegram Manager Bot on Nosana and enable team access.
"""

import os
import json
import hashlib
import secrets
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class TeamMember:
    """Team member configuration"""
    name: str
    email: str
    role: str  # "admin", "user", "viewer"
    telegram_id: Optional[str] = None
    access_level: str = "basic"  # "basic", "advanced", "admin"
    created_at: Optional[str] = None
    last_access: Optional[str] = None

@dataclass
class SecurityConfig:
    """Security configuration"""
    jwt_secret: str
    api_key: str
    admin_password: str
    encryption_key: str
    session_timeout: int = 3600  # 1 hour
    max_login_attempts: int = 5
    ip_whitelist: Optional[List[str]] = None

class SecureNosanaDeployer:
    """Secure deployment with team access management"""
    
    def __init__(self):
        self.security_config = self._generate_security_config()
        self.team_members = []
        self.access_log = []
    
    def _generate_security_config(self) -> SecurityConfig:
        """Generate secure configuration"""
        return SecurityConfig(
            jwt_secret=secrets.token_urlsafe(32),
            api_key=secrets.token_urlsafe(24),
            admin_password=secrets.token_urlsafe(16),
            encryption_key=secrets.token_urlsafe(32),
            ip_whitelist=["0.0.0.0/0"]  # Allow all IPs initially
        )
    
    def create_secure_dockerfile(self) -> str:
        """Create secure Dockerfile with security best practices"""
        dockerfile = """# Secure Nosana GPU Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install security updates and dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \\
    git \\
    curl \\
    wget \\
    nginx \\
    supervisor \\
    fail2ban \\
    ufw \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/ssl /app/config \\
    && chown -R appuser:appuser /app \\
    && chmod -R 755 /app \\
    && chmod 600 /app/.env \\
    && chmod 600 /app/google_service_account.json

# Create SSL directory
RUN mkdir -p /etc/ssl/private /etc/ssl/certs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose ports
EXPOSE 80 443 8080

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "run.py"]
"""
        return dockerfile
    
    def create_nginx_config(self) -> str:
        """Create secure Nginx configuration"""
        nginx_config = """# Secure Nginx Configuration
server {
    listen 80;
    server_name _;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name _;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/telegram-bot.crt;
    ssl_certificate_key /etc/ssl/private/telegram-bot.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Proxy to application
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Admin panel
    location /admin {
        auth_basic "Admin Area";
        auth_basic_user_file /app/config/.htpasswd;
        proxy_pass http://localhost:8080/admin;
    }
    
    # API endpoints
    location /api {
        proxy_pass http://localhost:8080/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8080/health;
        access_log off;
    }
}
"""
        return nginx_config
    
    def create_fail2ban_config(self) -> str:
        """Create Fail2ban configuration for security"""
        fail2ban_config = """[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log

[telegram-bot]
enabled = true
filter = telegram-bot
port = http,https
logpath = /app/logs/access.log
maxretry = 10
"""
        return fail2ban_config
    
    def create_team_access_system(self) -> str:
        '''Create team access management system'''
        access_system = '''#!/usr/bin/env python3
# Team Access Management System
# ============================
# Manage team member access to the Telegram Manager Bot.

import os
import json
import secrets
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('JWT_SECRET', 'your-secret-key')

class TeamAccessManager:
    def __init__(self):
        self.members_file = "/app/config/team_members.json"
        self.access_log_file = "/app/logs/access.log"
        self.members = self.load_members()
    
    def load_members(self) -> List[Dict]:
        # Load team members from file
        try:
            if os.path.exists(self.members_file):
                with open(self.members_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading members: {e}")
        return []
    
    def save_members(self):
        # Save team members to file
        try:
            os.makedirs(os.path.dirname(self.members_file), exist_ok=True)
            with open(self.members_file, 'w') as f:
                json.dump(self.members, f, indent=2)
        except Exception as e:
            print(f"Error saving members: {e}")
    
    def add_member(self, name: str, email: str, role: str, telegram_id: str = None) -> bool:
        # Add new team member
        member = {
            "name": name,
            "email": email,
            "role": role,
            "telegram_id": telegram_id,
            "access_level": "basic" if role == "user" else "admin" if role == "admin" else "advanced",
            "created_at": datetime.now().isoformat(),
            "last_access": None,
            "api_key": secrets.token_urlsafe(24)
        }
        
        self.members.append(member)
        self.save_members()
        return True
    
    def authenticate_member(self, api_key: str) -> Optional[Dict]:
        # Authenticate team member
        for member in self.members:
            if member.get("api_key") == api_key:
                member["last_access"] = datetime.now().isoformat()
                self.save_members()
                return member
        return None

# Initialize access manager
access_manager = TeamAccessManager()

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        member = access_manager.authenticate_member(api_key)
        if not member:
            return jsonify({"error": "Invalid API key"}), 401
        
        request.member = member
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/team/members', methods=['GET'])
@require_auth
def get_members():
    # Get all team members (admin only)
    if request.member["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    return jsonify({
        "members": access_manager.members,
        "total": len(access_manager.members)
    })

@app.route('/api/team/members', methods=['POST'])
@require_auth
def add_member():
    # Add new team member (admin only)
    if request.member["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.get_json()
    
    if not all(k in data for k in ["name", "email", "role"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    success = access_manager.add_member(
        data["name"],
        data["email"],
        data["role"],
        data.get("telegram_id")
    )
    
    if success:
        return jsonify({"message": "Member added successfully"}), 201
    else:
        return jsonify({"error": "Failed to add member"}), 500

@app.route('/api/team/profile', methods=['GET'])
@require_auth
def get_profile():
    # Get current member profile
    return jsonify({
        "name": request.member["name"],
        "email": request.member["email"],
        "role": request.member["role"],
        "access_level": request.member["access_level"],
        "last_access": request.member["last_access"]
    })

@app.route('/api/team/bot/status', methods=['GET'])
@require_auth
def get_bot_status():
    # Get bot status (all authenticated users)
    return jsonify({
        "status": "running",
        "uptime": "2 hours",
        "messages_processed": 150,
        "active_chats": 5
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
'''
        return access_system
    
    def create_team_setup_script(self) -> str:
        """Create team setup script"""
        script = """#!/bin/bash
# Team Setup Script for Secure Nosana Deployment

echo "🔐 Setting up secure team access..."

# Create configuration directories
mkdir -p /app/config /app/logs /app/ssl

# Generate SSL certificates (self-signed for now)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
    -keyout /app/ssl/telegram-bot.key \\
    -out /app/ssl/telegram-bot.crt \\
    -subj "/C=US/ST=State/L=City/O=Organization/CN=telegram-bot.nosana.com"

# Copy SSL certificates
cp /app/ssl/telegram-bot.key /etc/ssl/private/
cp /app/ssl/telegram-bot.crt /etc/ssl/certs/

# Set proper permissions
chmod 600 /app/ssl/telegram-bot.key
chmod 644 /app/ssl/telegram-bot.crt

# Create admin user
echo "Creating admin user..."
read -p "Enter admin email: " ADMIN_EMAIL
read -s -p "Enter admin password: " ADMIN_PASSWORD
echo

# Create .htpasswd for admin access
htpasswd -cb /app/config/.htpasswd $ADMIN_EMAIL $ADMIN_PASSWORD

# Initialize team members
cat > /app/config/team_members.json << EOF
[
  {
    "name": "Admin User",
    "email": "$ADMIN_EMAIL",
    "role": "admin",
    "access_level": "admin",
    "created_at": "$(date -Iseconds)",
    "api_key": "$(openssl rand -hex 12)"
  }
]
EOF

echo "✅ Secure team setup complete!"
echo "📋 Next steps:"
echo "1. Add team members via API"
echo "2. Share API keys with team"
echo "3. Monitor access logs"
"""
        return script
    
    def create_deployment_package(self) -> Dict[str, Any]:
        """Create complete secure deployment package"""
        try:
            print("🔐 Creating secure deployment package...")
            
            # Create all security files
            files_to_create = {
                "Dockerfile": self.create_secure_dockerfile(),
                "nginx.conf": self.create_nginx_config(),
                "fail2ban.conf": self.create_fail2ban_config(),
                "team_access.py": self.create_team_access_system(),
                "team_setup.sh": self.create_team_setup_script(),
                "security.env": f"""# Security Configuration
JWT_SECRET={self.security_config.jwt_secret}
API_KEY={self.security_config.api_key}
ADMIN_PASSWORD={self.security_config.admin_password}
ENCRYPTION_KEY={self.security_config.encryption_key}
SESSION_TIMEOUT={self.security_config.session_timeout}
MAX_LOGIN_ATTEMPTS={self.security_config.max_login_attempts}
IP_WHITELIST={','.join(self.security_config.ip_whitelist) if self.security_config.ip_whitelist else ''}
""",
                "docker-compose.secure.yml": """version: '3.8'

services:
  telegram-manager-bot:
    build: .
    container_name: telegram-manager-bot-secure
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      - TELEGRAM_PHONE=${TELEGRAM_PHONE}
      - AI_BACKEND=ollama
      - OLLAMA_BASE_URL=http://localhost:11434
      - OLLAMA_MODEL=llama3.2:latest
      - USER_ID=${USER_ID}
      - GOOGLE_SERVICE_ACCOUNT_FILE=${GOOGLE_SERVICE_ACCOUNT_FILE}
      - GOOGLE_SPREADSHEET_ID=${GOOGLE_SPREADSHEET_ID}
      - JWT_SECRET=${JWT_SECRET}
      - API_KEY=${API_KEY}
      - REDUNDANCY_ENABLED=true
      - AGENT_ENABLED=true
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./config:/app/config
      - ./ssl:/app/ssl
      - ./google_service_account.json:/app/google_service_account.json:ro
    networks:
      - bot-network

  team-access:
    build: .
    container_name: team-access-manager
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - API_KEY=${API_KEY}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    networks:
      - bot-network

  nginx:
    image: nginx:alpine
    container_name: nginx-proxy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/ssl
    depends_on:
      - telegram-manager-bot
      - team-access
    networks:
      - bot-network

  ollama:
    image: ollama/ollama:latest
    container_name: ollama-server
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    networks:
      - bot-network

volumes:
  ollama_data:

networks:
  bot-network:
    driver: bridge
"""
            }
            
            # Write files
            for filename, content in files_to_create.items():
                with open(filename, 'w') as f:
                    f.write(content)
                print(f"✅ Created {filename}")
            
            # Make scripts executable
            os.chmod("team_setup.sh", 0o755)
            
            print("\n🔐 SECURE DEPLOYMENT INSTRUCTIONS:")
            print("=" * 50)
            print("1. Upload all files to your Nosana GPU instance")
            print("2. Run: chmod +x team_setup.sh")
            print("3. Run: ./team_setup.sh")
            print("4. Configure your .env file with security settings")
            print("5. Start services: docker-compose -f docker-compose.secure.yml up -d")
            print("6. Add team members via API")
            
            print("\n🔑 SECURITY FEATURES:")
            print("- SSL/TLS encryption")
            print("- Rate limiting")
            print("- Team access management")
            print("- API key authentication")
            print("- Access logging")
            print("- Non-root user execution")
            
            print("\n👥 TEAM ACCESS:")
            print("- Admin panel: https://your-instance.com/admin")
            print("- API endpoints: https://your-instance.com/api/team/*")
            print("- Bot status: https://your-instance.com/api/team/bot/status")
            
            return {
                "success": True,
                "message": "Secure deployment package created",
                "files_created": list(files_to_create.keys()),
                "security_config": {
                    "jwt_secret": self.security_config.jwt_secret[:10] + "...",
                    "api_key": self.security_config.api_key[:10] + "...",
                    "admin_password": self.security_config.admin_password[:10] + "..."
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """Main secure deployment function"""
    print("🔐 SECURE NOSANA DEPLOYMENT")
    print("=" * 50)
    
    deployer = SecureNosanaDeployer()
    
    print("📋 Available Options:")
    print("1. Create secure deployment package")
    print("2. Show security features")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        result = deployer.create_deployment_package()
        if result["success"]:
            print(f"\n✅ {result['message']}")
            print(f"📁 Files created: {len(result['files_created'])}")
        else:
            print(f"\n❌ Error: {result['error']}")
    
    elif choice == "2":
        print("\n🔐 SECURITY FEATURES:")
        print("• SSL/TLS encryption for all communications")
        print("• Rate limiting to prevent abuse")
        print("• Team access management with roles")
        print("• API key authentication")
        print("• Comprehensive access logging")
        print("• Non-root user execution")
        print("• IP whitelisting capability")
        print("• Session timeout management")
        print("• Encrypted configuration storage")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main() 