@echo off
echo ==========================================================
echo 🌳 TreeSense Imaging - Production Platform Launcher
echo ==========================================================
echo Starting FastAPI Backend on http://localhost:8000 ...
start "TreeSense Backend (FastAPI)" cmd /k "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Next.js Frontend on http://localhost:3000 ...
start "TreeSense Frontend (Next.js)" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Platform launched!
echo - Frontend: http://localhost:3000
echo - Backend API Docs: http://localhost:8000/docs
echo ==========================================================
pause
