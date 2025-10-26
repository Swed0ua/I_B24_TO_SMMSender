# I_B24_TO_SMMSender - Setup and Autostart Guide

## Overview
Integration service for SmartKasa connecting Bitrix24 with AlphaSMS for sending Viber messages and SMS to contacts.

## Files
- Main entry point: `bitrix_controller.py`
- SMS/Viber sender: `sms_sender.py`
- Configuration: `.env` file
- Port: 5001 (default, configurable in `.env`)

---

## Linux/Unix Autostart Setup

### 1. Create systemd service file

```bash
sudo nano /etc/systemd/system/AC_I_B24_TO_SMMSender.service
```

### 2. Service file content

**Note**: Update paths below with your actual project directory.

```ini
[Unit]
Description=Bitrix24 to AlphaSMS Integration Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/path/to/I_B24_TO_SMMSender
Environment=PATH=/path/to/I_B24_TO_SMMSender/venv/bin
Environment=PYTHONPATH=/path/to/I_B24_TO_SMMSender
ExecStart=/path/to/I_B24_TO_SMMSender/venv/bin/python bitrix_controller.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=AC_I_B24_TO_SMMSender

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/path/to/I_B24_TO_SMMSender

[Install]
WantedBy=multi-user.target
```

### 3. Initialize and enable service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable autostart
sudo systemctl enable AC_I_B24_TO_SMMSender

# Start service
sudo systemctl start AC_I_B24_TO_SMMSender

# Check status
sudo systemctl status AC_I_B24_TO_SMMSender
```

---

## Service Management Commands

### Start service
```bash
sudo systemctl start AC_I_B24_TO_SMMSender
```

### Stop service
```bash
sudo systemctl stop AC_I_B24_TO_SMMSender
```

### Restart service
```bash
sudo systemctl restart AC_I_B24_TO_SMMSender
```

### Check status
```bash
sudo systemctl status AC_I_B24_TO_SMMSender
```

### View logs
```bash
# Follow logs in real-time
sudo journalctl -u AC_I_B24_TO_SMMSender -f

# View last 50 log entries
sudo journalctl -u AC_I_B24_TO_SMMSender -n 50

# View all logs
sudo journalctl -u AC_I_B24_TO_SMMSender
```

---

## Verification

### Check if API is responding
```bash
curl -X POST http://localhost:5001/updateLead
```

### Check if process is running
```bash
ps aux | grep "python bitrix_controller.py"
```

### Check if port is open
```bash
netstat -tulpn | grep 5001
```

### List all services
```bash
sudo systemctl list-units --type=service
```

---

## Manual Start (Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure .env file exists with proper configuration
# Copy from ENV_EXAMPLE.txt if needed

# Run the service
python bitrix_controller.py
```

---

## Environment Configuration

Create `.env` file with the following variables (see ENV_EXAMPLE.txt):

```env
# Bitrix24 Configuration
WEBHOOK_URL=https://smartkasa.bitrix24.eu/rest/YOUR_WEBHOOK_URL/
DEAL_STAGE_ID=30
LIST_ELEMENT_ID_WITH_TEMP=72

# AlphaSMS Configuration
ALPHASMS_API_KEY=your_api_key_here
SMS_SIGNATURE=SmartKasa
VIBER_SIGNATURE=СМАРТ КАСА

# Stage IDs
STAGE_ID_BOT_SALES=C30:UC_43WLCX
STAGE_ID_DISCOUNT=C30:NEW

# SMS Templates
SMS_TEXT_BOT_SALES=Your SMS text here
SMS_TEXT_DISCOUNT=Your SMS text here

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

---

