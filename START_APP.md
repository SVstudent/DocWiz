# Quick Start Guide - Launch DocWiz Application

## Prerequisites Check
Make sure you have:
- ✅ Backend `.env` file configured (check `backend/.env`)
- ✅ Frontend `.env.local` file configured (check `frontend/.env.local`)
- ✅ Firebase credentials in place
- ✅ All API keys set (Gemini, Freepik, etc.)

## Step 1: Start the Backend Server

Open a terminal and run:

```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Backend will be available at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

## Step 2: Start the Frontend Server

Open a NEW terminal and run:

```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Ready in X.Xs
```

Frontend will be available at: **http://localhost:3000**

## Step 3: Access the Application

Open your browser and go to:
👉 **http://localhost:3000**

## Quick Test Flow

1. **Register/Login** - Create an account at `/register`
2. **Create Profile** - Go to `/profile` and fill in your information
3. **Browse Procedures** - Check out available procedures
4. **Upload Image** - Upload a photo for visualization
5. **Generate Preview** - See AI-generated surgical preview
6. **View Costs** - Get detailed cost estimates
7. **Compare Options** - Compare multiple procedures
8. **Generate Claim** - Create insurance documentation

## Troubleshooting

### Backend won't start?
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify Firebase credentials are in place
- Check `.env` file has all required variables

### Frontend won't start?
- Check if port 3000 is already in use: `lsof -i :3000`
- Run `npm install` if dependencies are missing
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`

### Can't connect to backend?
- Make sure backend is running on port 8000
- Check CORS settings in `backend/app/config.py`
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local`

## Stopping the Servers

- Backend: Press `CTRL+C` in the backend terminal
- Frontend: Press `CTRL+C` in the frontend terminal

## Optional: Start with Docker Compose

If you prefer Docker:

```bash
docker-compose up
```

This will start:
- Backend on port 8000
- Frontend on port 3000
- PostgreSQL on port 5432
- Qdrant on port 6333
- Redis on port 6379

---

**Ready to test!** 🚀
