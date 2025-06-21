# 🔐 Security Guide for Nosana Deployment

This guide will help you secure your Telegram Manager Bot on Nosana and make it accessible to your team.

## 🚀 Quick Start

1. **Create secure deployment:**
   ```bash
   python secure_nosana_deployment.py
   ```

2. **Set up team access:**
   ```bash
   python team_access_manager.py
   ```

3. **Deploy to Nosana:**
   ```bash
   # Upload files to your Nosana GPU instance
   # Run the deployment script
   ./deploy.sh
   ```

## 🔒 Security Features

### 1. **SSL/TLS Encryption**
- All communications encrypted with HTTPS
- Self-signed certificates (upgrade to Let's Encrypt for production)
- TLS 1.2+ protocols only

### 2. **API Key Authentication**
- Each team member gets unique API key
- Keys are cryptographically secure
- Automatic key rotation capability

### 3. **Role-Based Access Control**
- **Admin**: Full access to bot control and team management
- **User**: Access to bot status and basic functions
- **Viewer**: Read-only access to bot status

### 4. **Rate Limiting**
- 10 requests per second per IP
- Burst protection (20 requests)
- Automatic blocking of abusive IPs

### 5. **Access Logging**
- All access attempts logged
- IP address tracking
- Timestamp and user identification
- Failed authentication attempts flagged

### 6. **Non-Root Execution**
- Application runs as non-root user
- Minimal file permissions
- Secure file handling

## 👥 Team Access Setup

### Step 1: Add Team Members

```bash
python team_access_manager.py
# Choose option 1: Add team member
```

**Example:**
```
Name: John Doe
Email: john@company.com
Role: admin
Telegram ID: 123456789
```

### Step 2: Generate Access Instructions

```bash
python team_access_manager.py
# Choose option 4: Generate access instructions
```

This creates `team_access_instructions.txt` with:
- Individual API keys for each member
- Access URLs and endpoints
- Security guidelines
- Support information

### Step 3: Share with Team

Send each team member:
1. Their unique API key
2. Access instructions
3. Security guidelines

## 🌐 Access Methods

### 1. **Web Dashboard**
```
https://your-nosana-instance.com/admin
```
- Admin panel with full control
- Bot status monitoring
- Team management interface

### 2. **API Endpoints**
```bash
# Check bot status
curl -H "X-API-Key: YOUR_API_KEY" \
  https://your-nosana-instance.com/api/team/bot/status

# Get your profile
curl -H "X-API-Key: YOUR_API_KEY" \
  https://your-nosana-instance.com/api/team/profile

# List team members (admin only)
curl -H "X-API-Key: YOUR_API_KEY" \
  https://your-nosana-instance.com/api/team/members
```

### 3. **Telegram Bot**
- Direct access via Telegram
- Commands: `/start`, `/help`, `/status`
- Real-time notifications

## 🔧 Deployment Security

### 1. **Environment Variables**
```bash
# Required security variables
JWT_SECRET=your_jwt_secret_here
API_KEY=your_api_key_here
ADMIN_PASSWORD=your_admin_password_here
ENCRYPTION_KEY=your_encryption_key_here

# Optional security settings
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
IP_WHITELIST=192.168.1.0/24,10.0.0.0/8
```

### 2. **File Permissions**
```bash
# Secure file permissions
chmod 600 .env
chmod 600 google_service_account.json
chmod 600 team_members.json
chmod 755 deploy.sh
chmod 755 monitor.sh
```

### 3. **SSL Certificate Setup**
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /app/ssl/telegram-bot.key \
  -out /app/ssl/telegram-bot.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# For production, use Let's Encrypt
certbot --nginx -d your-domain.com
```

## 📊 Monitoring & Logs

### 1. **Access Logs**
```bash
# View access logs
tail -f /app/logs/access.log

# Monitor failed attempts
grep "FAILED" /app/logs/access.log

# Check API usage
grep "API_KEY" /app/logs/access.log | wc -l
```

### 2. **Bot Status Monitoring**
```bash
# Check if bot is running
curl -f https://your-nosana-instance.com/health

# Monitor Docker containers
docker-compose ps

# Check resource usage
docker stats
```

### 3. **Security Monitoring**
```bash
# Check for suspicious activity
grep -i "error\|failed\|denied" /app/logs/*.log

# Monitor rate limiting
grep "429" /var/log/nginx/access.log

# Check SSL certificate expiry
openssl x509 -in /app/ssl/telegram-bot.crt -text -noout | grep "Not After"
```

## 🚨 Security Best Practices

### 1. **API Key Management**
- ✅ Generate unique keys for each user
- ✅ Rotate keys regularly (every 90 days)
- ✅ Store keys securely (environment variables)
- ❌ Never commit keys to version control
- ❌ Don't share keys via email

### 2. **Access Control**
- ✅ Use role-based permissions
- ✅ Implement least privilege principle
- ✅ Regular access reviews
- ❌ Don't give admin access unnecessarily
- ❌ Avoid shared accounts

### 3. **Network Security**
- ✅ Use HTTPS for all communications
- ✅ Implement rate limiting
- ✅ Monitor for suspicious IPs
- ❌ Don't expose admin panel publicly
- ❌ Avoid HTTP (unencrypted) access

### 4. **Data Protection**
- ✅ Encrypt sensitive data at rest
- ✅ Secure file permissions
- ✅ Regular backups
- ❌ Don't store passwords in plain text
- ❌ Avoid logging sensitive information

## 🔄 Maintenance & Updates

### 1. **Regular Security Updates**
```bash
# Update system packages
apt-get update && apt-get upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Update Python dependencies
pip install --upgrade -r requirements.txt
```

### 2. **Backup Strategy**
```bash
# Backup configuration
tar -czf backup-$(date +%Y%m%d).tar.gz \
  .env team_members.json google_service_account.json

# Backup logs
tar -czf logs-$(date +%Y%m%d).tar.gz /app/logs/

# Backup data
tar -czf data-$(date +%Y%m%d).tar.gz /app/data/
```

### 3. **Monitoring Setup**
```bash
# Set up automated monitoring
nohup ./monitor.sh > /dev/null 2>&1 &

# Check monitoring status
ps aux | grep monitor.sh

# View monitoring logs
tail -f /var/log/telegram-bot-monitor.log
```

## 🆘 Incident Response

### 1. **Security Breach Response**
1. **Immediate Actions:**
   - Revoke compromised API keys
   - Block suspicious IP addresses
   - Check access logs for unauthorized activity

2. **Investigation:**
   - Review all access logs
   - Identify affected accounts
   - Determine breach scope

3. **Recovery:**
   - Generate new API keys
   - Update security configurations
   - Notify affected team members

### 2. **Bot Malfunction Response**
1. **Check Status:**
   ```bash
   curl -f https://your-nosana-instance.com/health
   docker-compose ps
   ```

2. **Restart Services:**
   ```bash
   docker-compose restart
   # or
   docker-compose down && docker-compose up -d
   ```

3. **Check Logs:**
   ```bash
   docker-compose logs -f
   tail -f /app/logs/*.log
   ```

## 📞 Support & Troubleshooting

### Common Issues:

1. **API Key Not Working**
   - Check if key is correct
   - Verify user has proper permissions
   - Check if user account is active

2. **SSL Certificate Issues**
   - Verify certificate is valid
   - Check certificate expiry
   - Ensure proper file permissions

3. **Rate Limiting**
   - Check if you're making too many requests
   - Wait for rate limit to reset
   - Contact admin if persistent

4. **Bot Not Responding**
   - Check if bot is running
   - Verify Telegram token is valid
   - Check network connectivity

### Contact Information:
- **Admin**: [Your Email]
- **Emergency**: [Emergency Contact]
- **Documentation**: [Your Documentation URL]

---

**Remember**: Security is an ongoing process. Regularly review and update your security measures to protect your Telegram Manager Bot and team access. 