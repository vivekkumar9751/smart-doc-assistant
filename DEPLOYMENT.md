# 🚀 Smart Document Assistant - Server Deployment Guide

This guide will help you deploy the Smart Document Assistant on any server (Linux, cloud instances, etc.) to ensure it works properly.

## 🔧 Prerequisites

1. **Python 3.8+** installed on your server
2. **Valid OpenAI API Key** with available credits/billing configured
3. **Internet connection** for API calls
4. **Sufficient storage** for document uploads

## 📋 Quick Deployment Steps

### 1. Clone and Setup

```bash
# Clone your repository (or upload files to server)
cd /path/to/your/server/directory

# Ensure all files are present
ls -la
# Should show: backend/, frontend/, requirements.txt, deploy.sh, start.sh, etc.
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.template .env

# Edit the .env file with your actual API key
nano .env  # or use vim, emacs, etc.
```

**Important**: In the `.env` file, replace `YOUR_ACTUAL_API_KEY_HERE` with your real OpenAI API key:

```bash
# ❌ WRONG (what causes the quota error)
OPENAI_API_KEY=sk-proj-VRfOmjMhcGkDrJxHTO0mv0EKqXs_rEJEfTsJ5CVycpBKX37VGjdk2MWEGTu3Wkp2paqMEbx7O1T3BlbkFJTb
u4uAxkEqziGHD30EvQ9Yk-CLeW-QliIPtimQaYvWV0DdOl6jb_NQ8fOh6P5L5KBSCUlXVLQA

# ✅ CORRECT (single line, complete key)
OPENAI_API_KEY=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
```

### 3. Run Deployment Validation

```bash
# Make deployment script executable (if not already)
chmod +x deploy.sh

# Run the deployment validation
./deploy.sh
```

This script will:
- ✅ Validate your `.env` configuration
- ✅ Check API key format
- ✅ Install Python dependencies
- ✅ Test OpenAI API connectivity
- ✅ Verify billing/quota status

### 4. Start the Application

```bash
# Make start script executable (if not already)
chmod +x start.sh 

# Start both backend and frontend
./start.sh
```

**Or start services manually:**

```bash
# Terminal 1 - Backend API
uvicorn backend.api:app --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend (in a new terminal)
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

## 🌐 Accessing Your Application

Once deployed, your application will be available at:

- **Frontend (Main App)**: `http://YOUR_SERVER_IP:8501`
- **Backend API**: `http://YOUR_SERVER_IP:8000`
- **API Health Check**: `http://YOUR_SERVER_IP:8000/health`
- **OpenAI Health Check**: `http://YOUR_SERVER_IP:8000/health/openai`

## 🔍 Troubleshooting Common Server Issues

### ❌ "Quota Exceeded" Error

**Cause**: OpenAI API key has no credits or billing issues

**Solutions**:
1. Check your billing at https://platform.openai.com/usage
2. Add a payment method to your OpenAI account
3. Verify your usage limits haven't been exceeded
4. Generate a new API key if the current one is invalid

### ❌ "Invalid API Key" Error

**Cause**: API key is malformed, split across lines, or invalid

**Solutions**:
1. Ensure API key is on a **single line** in `.env`
2. No spaces or line breaks in the key
3. Key should start with `sk-proj-` or `sk-`
4. Generate a new key at https://platform.openai.com/api-keys

### ❌ Connection/Timeout Issues

**Cause**: Network connectivity or server configuration

**Solutions**:
1. Check if ports 8000 and 8501 are open
2. Verify internet connectivity: `curl https://api.openai.com`
3. Check firewall settings
4. Ensure server has sufficient resources (memory/CPU)

### ❌ "Backend Unhealthy" Error

**Cause**: Backend service failed to start

**Solutions**:
1. Check backend logs: `uvicorn backend.api:app --log-level debug`
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Test API key with: `curl http://localhost:8000/health/openai`

## 🔐 Security Considerations for Production

### Environment Variables
```bash
# Set production environment
export ENVIRONMENT=production

# Use secure secret key
export SECRET_KEY=your-random-secret-key-here
```

### Firewall Configuration
```bash
# Only allow necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 8000  # Backend API
sudo ufw allow 8501  # Frontend
sudo ufw enable
```

### HTTPS Setup (Recommended)
Use a reverse proxy like Nginx with SSL certificates for production.

## 📊 Monitoring and Logs

### Check Service Status
```bash
# Check if services are running
ps aux | grep uvicorn
ps aux | grep streamlit

# Check port usage
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501
```

### View Logs
```bash
# Backend logs
tail -f /var/log/smart-doc-assistant/backend.log

# Or run with verbose logging
uvicorn backend.api:app --log-level debug
```

### Health Monitoring
```bash
# Automated health check
curl -f http://localhost:8000/health || echo "Backend is down"
curl -f http://localhost:8000/health/openai || echo "OpenAI API issues"
```

## 🔄 Process Management with systemd (Linux)

Create service files for automatic startup:

### Backend Service
```bash
sudo nano /etc/systemd/system/smart-doc-backend.service
```

```ini
[Unit]
Description=Smart Document Assistant Backend
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/smart-doc-assistant
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/uvicorn backend.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Frontend Service
```bash
sudo nano /etc/systemd/system/smart-doc-frontend.service
```

```ini
[Unit]
Description=Smart Document Assistant Frontend
After=network.target smart-doc-backend.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/smart-doc-assistant
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

### Enable Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable smart-doc-backend
sudo systemctl enable smart-doc-frontend
sudo systemctl start smart-doc-backend
sudo systemctl start smart-doc-frontend
```

## 🚨 Common Deployment Pitfalls

1. **API Key in Git**: Never commit `.env` files to version control
2. **Line Breaks in Keys**: Ensure API keys are single-line
3. **Port Conflicts**: Check if ports 8000/8501 are available
4. **File Permissions**: Ensure scripts are executable (`chmod +x`)
5. **Dependencies**: Always run `pip install -r requirements.txt`
6. **OpenAI Billing**: Verify your account has active billing/credits

## 📞 Getting Help

If deployment fails:

1. Run the diagnostic endpoints:
   - `curl http://localhost:8000/health/env`
   - `curl http://localhost:8000/health/openai`

2. Check the application logs for specific error messages

3. Verify your OpenAI account status at https://platform.openai.com/usage

4. Ensure your server meets the minimum requirements

---

**🎉 Success!** Your Smart Document Assistant should now be running smoothly on your server! 