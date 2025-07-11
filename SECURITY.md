# 🔒 Security & Privacy Guide

This document outlines the security measures, privacy protections, and best practices implemented in the Telegram BD Intelligence System.

---

## 🛡️ Security Features

### **1. Data Protection**
- **Local Storage Only** - All sensitive data stored locally in SQLite databases
- **No Cloud Dependencies** - Core functionality works completely offline
- **Encrypted Communications** - All API calls use industry-standard TLS encryption
- **Privacy by Design** - Minimal data collection, maximum local control

### **2. Environment Security**
- **Environment File Exclusion** - All `.env*` files automatically excluded from git
- **Template System** - Safe configuration templates with placeholder values
- **No Hardcoded Secrets** - All sensitive data configurable via environment variables
- **Secure Defaults** - Security-first configuration out of the box

### **3. Git Repository Protection**
The repository is configured with comprehensive `.gitignore` protection for:

```
# Sensitive Data Directories
exports/           # Contains actual user conversations and contact data
data/             # Contains all databases with personal information
backups/          # Contains backup data
cache/            # Contains cached sensitive data
logs/             # Contains application logs with potential data

# Configuration Files
.env*             # Environment files with API keys
config.env*       # Configuration files
*.env*            # Any environment variations

# Database Files
*.db              # SQLite database files
*.sqlite          # SQLite variations
*.sqlite3         # Additional SQLite formats

# Personal Data Files
*.csv             # Export files with contact data
*.xlsx            # Excel exports
*.json            # JSON exports with data
extraction_summary_*.txt  # Telegram extraction summaries

# Session Files
*.session*        # Telegram session files
*.auth            # Authentication files
auth_*            # Auth-related files
session_*         # Session-related files

# Scripts with Secrets (removed)
quick_env_fix.py  # Had hardcoded API keys (deleted)
fix_phone_number.py  # Had hardcoded phone numbers (deleted)
fix_env.py        # Had sensitive configuration (deleted)
```

---

## 🔐 API Key Security

### **OpenAI API Keys**
- **Environment Storage** - Keys stored only in `.env` files (excluded from git)
- **No Hardcoding** - All references use `os.getenv()` with safe defaults
- **Placeholder System** - Templates use obvious placeholders like `sk-proj-your-key-here`
- **Rotation Ready** - Easy to rotate keys by updating `.env` file

### **Telegram API Credentials**
- **Separate Storage** - API ID, hash, and phone stored separately
- **No Session Commits** - Telegram session files excluded from git
- **Safe Defaults** - All code uses environment variables with safe fallbacks

### **Google Service Account**
- **Email Configuration** - Service account email configurable via environment
- **No Credential Files** - JSON credential files excluded from git
- **Placeholder System** - Generic placeholder emails in templates

---

## 🚫 Data That Will NEVER Be Committed

### **Automatically Excluded**
The `.gitignore` file ensures these are never committed:

1. **Personal Conversations** - All Telegram chat history and messages
2. **Contact Information** - Names, phone numbers, usernames, emails
3. **Business Data** - Lead information, deal data, analytics
4. **API Credentials** - All API keys, tokens, and authentication data
5. **Database Files** - SQLite databases containing user data
6. **Export Files** - CSV, Excel, JSON files with personal information
7. **Cache Data** - Temporary files that might contain sensitive information
8. **Log Files** - Application logs that might contain personal data

### **Manually Removed**
We've removed files that contained hardcoded sensitive data:

1. **`quick_env_fix.py`** - Contained real OpenAI API key (DELETED)
2. **`fix_phone_number.py`** - Contained real phone number (DELETED)  
3. **`fix_env.py`** - Contained sensitive configuration (DELETED)

---

## 🔍 Security Verification

### **Pre-Commit Checks**
Before each commit, verify:

```bash
# 1. Check git status for sensitive files
git status

# 2. Scan for API keys (should return no results)
grep -r "sk-proj-[a-zA-Z0-9\-_]{48,}" *.py core/*.py

# 3. Scan for bot tokens (should return no results)
grep -r "[0-9]{10}:[a-zA-Z0-9\-_]{35}" *.py core/*.py

# 4. Scan for real phone numbers (only +1234567890 examples should appear)
grep -r "\+[0-9]{10,15}" *.py core/*.py

# 5. Check for hardcoded emails (should only show placeholder examples)
grep -r "@.*\.com" *.py core/*.py | grep -v "example\|placeholder\|your_"
```

### **Repository Security Audit**
✅ **No real API keys** - All API keys replaced with placeholders
✅ **No real phone numbers** - Only example phone numbers (+1234567890)
✅ **No real emails** - Only placeholder service account emails
✅ **No personal data** - All user data directories excluded
✅ **No session files** - Telegram sessions excluded from git
✅ **No database files** - All `.db` files excluded
✅ **No export files** - All export directories excluded

---

## 🛠️ Security Best Practices

### **For Users**

#### **Environment File Management**
```bash
# 1. Always copy from template
cp env.template .env

# 2. Verify .env is not tracked
git status | grep -v ".env"

# 3. Use strong, unique API keys
# - Generate new OpenAI API key for each project
# - Use dedicated Telegram app for this project
# - Rotate keys regularly
```

#### **Database Security**
```bash
# 1. Regular backups (stored locally only)
python main.py backup

# 2. Secure file permissions
chmod 600 .env
chmod 700 data/

# 3. Clean sensitive logs periodically
find logs/ -name "*.log" -mtime +30 -delete
```

#### **Network Security**
- **VPN Usage** - Consider VPN for API calls in sensitive environments
- **Firewall Rules** - Ensure outbound HTTPS is allowed for API access
- **Network Monitoring** - Monitor for unusual API access patterns

### **For Developers**

#### **Code Security**
```python
# ✅ GOOD: Use environment variables
api_key = os.getenv('OPENAI_API_KEY', 'placeholder-key')

# ❌ BAD: Hardcoded secrets
api_key = "sk-proj-real-key-here"  # NEVER DO THIS

# ✅ GOOD: Safe fallbacks
service_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL', 
                         'your_service_account@your_project.iam.gserviceaccount.com')

# ❌ BAD: Real hardcoded emails
service_email = "real_account@real_project.iam.gserviceaccount.com"  # NEVER
```

#### **Git Practices**
```bash
# 1. Always check status before commit
git status

# 2. Use git hooks for security scanning
# Create .git/hooks/pre-commit with security checks

# 3. Review diff before push
git diff --cached

# 4. Use .gitignore early and often
git add .gitignore
git commit -m "Add comprehensive .gitignore for security"
```

---

## 🚨 Incident Response

### **If Secrets Are Accidentally Committed**

#### **Immediate Response**
1. **Rotate Compromised Keys** - Immediately regenerate all exposed API keys
2. **Remove from History** - Use `git filter-branch` or `BFG Repo-Cleaner`
3. **Force Push** - Rewrite repository history: `git push --force-with-lease`
4. **Notify Team** - Alert all collaborators to update their local repos

#### **Key Rotation Process**
```bash
# 1. OpenAI API Key
# - Go to https://platform.openai.com/api-keys
# - Delete compromised key
# - Generate new key
# - Update .env file

# 2. Telegram API
# - Go to https://my.telegram.org/apps
# - Delete application (if severely compromised)
# - Create new application
# - Update .env file

# 3. Google Service Account
# - Go to Google Cloud Console
# - Delete compromised service account
# - Create new service account
# - Update .env file and re-share Google Sheets
```

### **Prevention Measures**
- **Pre-commit Hooks** - Implement automated security scanning
- **Branch Protection** - Require review for sensitive changes
- **Access Control** - Limit repository access to necessary personnel
- **Regular Audits** - Periodic security reviews of code and configuration

---

## 📋 Security Checklist

### **Pre-GitHub Push Checklist**
- [ ] `.env` file is not in git status
- [ ] No real API keys in any Python files
- [ ] No real phone numbers in code (only +1234567890 examples)
- [ ] No real email addresses in code (only placeholders)
- [ ] `data/`, `exports/`, `backups/` directories excluded
- [ ] All database files (`.db`, `.sqlite`) excluded
- [ ] All session files excluded
- [ ] Environment template (`env.template`) is clean
- [ ] README and SETUP guides don't contain real credentials
- [ ] Security scan passes: `grep -r "sk-proj-" *.py` returns no results

### **Repository Security Standards**
- [ ] Comprehensive `.gitignore` for all sensitive data types
- [ ] Environment template with placeholder values only
- [ ] No hardcoded secrets in any source files
- [ ] Documentation uses placeholder examples
- [ ] Security guide provided (this document)
- [ ] Setup instructions emphasize security practices

---

## 🔗 Additional Resources

### **Security Tools**
- **git-secrets** - Prevents committing secrets to git
- **truffleHog** - Searches for secrets in git repositories
- **Gitleaks** - SAST tool for detecting secrets in code

### **Best Practices References**
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/best-practices-for-securing-your-repository)
- [API Key Security Guidelines](https://cloud.google.com/docs/authentication/api-keys)

---

**🔒 Security is everyone's responsibility. When in doubt, err on the side of caution.** 