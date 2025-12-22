# Novrintech Deployment Configuration

## 🔥 Backend API Setup

### 1. Deploy to Render/Railway/Heroku
- Push your code to GitHub
- Connect to your hosting platform
- Set environment variables from `.env`
- Deploy the FastAPI application

### 2. Get Your Deployed URL
After deployment, you'll get a URL like:
- Render: `https://novrintech-backend.onrender.com`
- Railway: `https://novrintech-backend.railway.app`
- Heroku: `https://novrintech-backend.herokuapp.com`

### 3. Update Desktop App Configuration
Replace `https://your-deployed-backend-url.com` with your actual URL in:
- `python_frontend_desktop/config.py`
- `python_frontend_desktop/main.py`

## 🔑 API Key Setup

### 1. Create API Key in Database
Run this command after your backend is deployed:
```bash
python create_api_key.py
```

This will create:
- **App Name**: Novrintech Desktop Client
- **API Key**: `novrintech_api_key_2024_secure`
- **Status**: Active

### 2. Desktop App Configuration
The desktop app is pre-configured with:
- **API URL**: Your deployed backend URL
- **API Key**: `novrintech_api_key_2024_secure`

## 🚀 Quick Setup Steps

1. **Deploy Backend**:
   ```bash
   # Push to GitHub, then deploy on Render/Railway
   git add .
   git commit -m "Deploy Novrintech backend"
   git push origin main
   ```

2. **Create API Key**:
   ```bash
   python create_api_key.py
   ```

3. **Update URLs**:
   - Replace `https://your-deployed-backend-url.com` with your actual deployed URL
   - Keep the API key as `novrintech_api_key_2024_secure`

4. **Run Desktop App**:
   ```bash
   cd python_frontend_desktop
   python main.py
   ```

## 🔧 Environment Variables for Deployment

Make sure these are set in your hosting platform:
```env
DATABASE_URL=postgresql://neondb_owner:npg_0N1WuhVBDLIP@ep-weathered-math-afeq5max-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
API_HOST=0.0.0.0
API_PORT=8000
KEEP_ALIVE_ENABLED=true
KEEP_ALIVE_INTERVAL=4
```

## 📱 Company Usage
- Desktop app is pre-configured for your company
- No need for users to enter API keys manually
- Ready for internal company file management
- Automatic duplicate detection and tracking

Your Novrintech Data Fall Back system is ready for production! 🔥