# Novrintech Data Fall Back - Backend API

A universal backend API service for data storage and retrieval with dual-database architecture.

## Features
- ✅ Secure API Key authentication
- ✅ PostgreSQL primary storage (Render)
- ✅ Firebase Realtime Database fallback
- ✅ RESTful CRUD operations
- ✅ File upload/download support
- ✅ Automatic data synchronization
- ✅ Frontend-agnostic (works with any client)

## Tech Stack
- **Backend**: FastAPI (Python)
- **Primary DB**: PostgreSQL
- **Secondary DB**: Firebase Realtime Database
- **Auth**: API Key based

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Add Firebase credentials:
- Download `firebase-credentials.json` from Firebase Console
- Place in project root

4. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Data Operations
- `POST /data/save` - Save data
- `GET /data/read/{data_key}` - Read data
- `PUT /data/update/{data_key}` - Update data
- `DELETE /data/delete/{data_key}` - Delete data

### File Operations
- `POST /file/upload` - Upload file
- `GET /file/read/{file_id}` - Read file info

### Health Check
- `GET /health` - API health status

## Authentication
Include API key in request headers:
```
X-API-KEY: your_api_key_here
```

## Deployment
Deploy to Render or any platform supporting Python/FastAPI.
