# Novrintech Desktop Client

A Python desktop application for interacting with the Novrintech Data Fall Back API.

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
- ✅ **User-friendly Interface** - Tabbed layout for easy navigation

## Installation

1. Install Python 3.7+ if not already installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Configuration

1. **API URL**: Set your backend URL (e.g., `http://localhost:8000` or your deployed URL)
2. **API Key**: Enter your API key from the backend
3. **Test Connection**: Verify everything works

## Usage

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

### File Manager
1. Go to "File Manager" tab
2. View uploaded files (requires backend list endpoint)
3. Download or view file information

## File Tracking Features

- **Upload Count**: Tracks how many times each file name is uploaded
- **Timestamps**: Records first upload and last upload times
- **Hash Verification**: Uses MD5 to detect identical files with different names
- **Duplicate Alerts**: Warns before uploading identical content
- **Persistent History**: Saves upload history locally in `upload_history.json`

## API Integration

The desktop app integrates with all backend endpoints:
- `POST /file/upload` - File uploads
- `GET /file/read/{file_id}` - File information
- `POST /data/save` - Save data
- `GET /data/read/{key}` - Read data
- `GET /health` - Connection testing

Perfect for company internal use with your Novrintech Data Fall Back backend!