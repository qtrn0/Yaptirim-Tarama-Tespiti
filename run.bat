@echo off
cd /d %~dp0
call venv\Scripts\activate
echo.
echo ============================================
echo   YAPTIRIM TARAMA TESPITI v2.0.0
echo ============================================
echo.
echo   Web Arayuzu:    http://127.0.0.1:8000/static/index.html
echo   Swagger API:    http://127.0.0.1:8000/docs
echo   Health Check:   http://127.0.0.1:8000/health
echo.
echo ============================================
echo.
uvicorn app.main:app --host 127.0.0.1 --port 8000 & start http://127.0.0.1:8000/static/index.html
pause