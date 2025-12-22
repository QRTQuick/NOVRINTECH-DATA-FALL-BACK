# Novrintech Desktop Client

A Python desktop application for interacting with the Novrintech Data Fall Back API.

## 🔥 Ready to Use - No Configuration Needed!

This desktop app comes pre-configured with:
- ✅ **API URL**: `https://novrintech-data-fall-back.onrender.com`
- ✅ **API Key**: Pre-embedded for instant testing
- ✅ **Keep-Alive**: Automatically pings backend every 4 seconds to prevent sleep
- ✅ **Zero Setup**: Just run and start uploading files!

## Features

### 🔥 File Management
- ✅ **File Upload** with duplicate detection
- ✅ **Upload History** tracking with timestamps
- ✅ **File Hash Verification** to prevent duplicate uploads
- ✅ **Upload Counter** - tracks how many times each file is uploaded
- ✅ **Date/Time Tracking** for first and last upload times

### 🔥 Data Operations
- ✅ **Save Data** - Store JSON data with custom keys
- ✅ **Read Data** - Retrieve data by key with fallback support
- ✅ **Real-time Results** - View API responses instantly

### 🔥 Smart Features
- ✅ **Duplicate Prevention** - MD5 hash checking before upload
- ✅ **Connection Testing** - Verify API connectivity
- ✅ **Local History** - Persistent upload tracking
- ✅ **Keep-Alive System** - Prevents backend from sleeping
- ✅ **User-friendly Interface** - Tabbed layout for easy navigation

## Quick Start

1. **Install Python 3.7+** if not already installed
2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python main.py
```

4. **Start using immediately** - No configuration needed!

## Usage

### Instant Testing
1. Launch the app - it's pre-configured!
2. Go to "Configuration" tab and click "Test Connection"
3. Start uploading files in "File Upload" tab
4. Use "Data Operations" for JSON data storage

### File Upload
1. Go to "File Upload" tab
2. Click "Browse Files" to select a file
3. Enable/disable duplicate checking
4. Click "Upload File"
5. View upload history with timestamps and counts

### Data Operations
1. Go to "Data Operations" tab
2. **Save Data**: Enter key and JSON value, click "Save Data"
3. **Read Data**: Enter key, click "Read Data" to retrieve

## Keep-Alive System

The app automatically:
- 🔄 Pings the backend every 4 seconds
- 💚 Keeps the API awake and responsive
- 📊 Shows ping status in the console
- ⚡ Ensures fast response times

## File Tracking Features

- **Upload Count**: Tracks how many times each file name is uploaded
- **Timestamps**: Records first upload and last upload times
- **Hash Verification**: Uses MD5 to detect identical files with different names
- **Duplicate Alerts**: Warns before uploading identical content
- **Persistent History**: Saves upload history locally in `upload_history.json`

Perfect for company internal use with zero configuration required! 🚀