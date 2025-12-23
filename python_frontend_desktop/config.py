"""
Configuration settings for Novrintech Desktop Client
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Embedded API Configuration - Ready to use!
DEFAULT_API_URL = "https://novrintech-data-fall-back.onrender.com"
DEFAULT_API_KEY = "novrintech_api_key_2024_secure"

# File Upload Settings
MAX_FILE_SIZE_MB = 100  # Maximum file size in MB
ALLOWED_FILE_TYPES = [
    ".txt", ".pdf", ".doc", ".docx", ".xls", ".xlsx", 
    ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".avi",
    ".zip", ".rar", ".json", ".xml", ".csv",".html"
]

# UI Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
THEME = "default"  # Can be "default", "dark", etc.

# Local Storage
HISTORY_FILE = "upload_history.json"
CONFIG_FILE = "app_config.json"

# API Endpoints
ENDPOINTS = {
    "health": "/health",
    "file_upload": "/file/upload",
    "file_read": "/file/read",
    "data_save": "/data/save",
    "data_read": "/data/read",
    "data_update": "/data/update",
    "data_delete": "/data/delete"
}

# Duplicate Detection
ENABLE_HASH_CHECK = True
HASH_ALGORITHM = "md5"  # md5, sha1, sha256

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "app.log"