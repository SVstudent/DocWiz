# 🚀 DocWiz Quick Start Guide

Get DocWiz running in 10 minutes!

## ⚡ Super Quick Setup

### 1. Get Your API Keys (5 minutes)

**Gemini API Key**:
```
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
```

**Firebase Setup**:
```
1. Visit: https://console.firebase.google.com/
2. Click "Add project" → Name it "docwiz-hackathon"
3. Enable Firestore: Build → Firestore Database → Create database (test mode)
4. Get credentials: Project Settings → Service accounts → Generate new private key
5. Save as: backend/firebase-credentials.json
6. Copy your Project ID
```

**Freepik API Key**:
```
1. Visit: https://www.freepik.com/api
2. Sign up and get API key
3. Copy the key
```

### 2. Configure Environment (2 minutes)

**Backend (.env)**:
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```bash
# Replace these with your actual values:
FIREBASE_PROJECT_ID=docwiz-hackathon  # Your Firebase project ID
GEMINI_API_KEY=AIza...  # Your Gemini key
NANO_BANANA_API_KEY=AIza...  # Same as Gemini or separate
```

**Freepik MCP**:
Edit `.kiro/settings/mcp.json`:
```json
{
  "mcpServers": {
    "mcp-freepik": {
      "env": {
        "FREEPIK_API_KEY": "your_actual_freepik_key_here"
      }
    }
  }
}
```

### 3. Install & Run (3 minutes)

**Start Services**:
```bash
# From project root
docker-compose up -d
```

**Backend**:
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

**Frontend** (new terminal):
```bash
cd frontend
npm install
npm run dev
```

### 4. Verify (1 minute)

Open these URLs:
- ✅ Frontend: http://localhost:3000
- ✅ Backend API: http://localhost:8000/docs
- ✅ Firestore Emulator: http://localhost:8080

## 🎯 What You Get

After setup, you have:

✅ **5 Google Services** integrated and ready
✅ **Firebase/Firestore** database running
✅ **Qdrant** vector search ready
✅ **Freepik MCP** configured
✅ **Complete spec** with 33 correctness properties
✅ **All tests** ready to run

## 🏃 Next Steps

### Option 1: Start Implementing
```bash
# Open the tasks file in Kiro
# Click "Start task" on any task
open .kiro/specs/docwiz-surgical-platform/tasks.md
```

### Option 2: Run Tests
```bash
# Backend tests
cd backend
poetry run pytest

# Frontend tests
cd frontend
npm run test
```

### Option 3: Explore the API
```bash
# Visit the interactive API docs
open http://localhost:8000/docs

# Try the health check endpoint
curl http://localhost:8000/health
```

## 🆘 Troubleshooting

**"Firebase credentials not found"**:
- Make sure `firebase-credentials.json` is in `backend/` directory
- Check `FIREBASE_CREDENTIALS_PATH` in `.env`

**"Firestore emulator not connecting"**:
- Run `docker-compose ps` to check if services are running
- Set `USE_FIRESTORE_EMULATOR=true` in `.env`

**"MCP server not connecting"**:
- Check that Node.js is installed (`node --version`)
- Verify Freepik API key in `.kiro/settings/mcp.json`

**"Port already in use"**:
- Backend (8000): Change in `uvicorn` command
- Frontend (3000): Change in `package.json`
- Firestore (8080): Change in `docker-compose.yml`

## 📚 Full Documentation

For detailed setup:
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Complete overview
- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Firebase details
- **[GOOGLE_SERVICES_INTEGRATION.md](GOOGLE_SERVICES_INTEGRATION.md)** - All services

## 🎊 You're Ready!

Your DocWiz platform is now running with:
- ✅ All Google services
- ✅ Firebase/Firestore database
- ✅ Vector search capability
- ✅ Freepik integration
- ✅ Complete testing suite

**Now go build and win that hackathon! 🏆**

---

*Total setup time: ~10 minutes*
*Questions? Check SETUP_COMPLETE.md*
