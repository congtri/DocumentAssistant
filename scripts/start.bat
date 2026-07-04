@echo off
setlocal

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%

echo === DocumentAssistant ===
echo.

:: Activate venv
if not exist "venv" (
    echo ERROR: Virtual environment not found. Run setup.bat first.
    exit /b 1
)
call venv\Scripts\activate.bat

:: Model path
set MODEL_PATH=models\gguf\Qwen_Qwen3.5-4B-Q4_K_M.gguf

if not exist "%MODEL_PATH%" (
    echo WARNING: Default model not found at %MODEL_PATH% (backend will manage llama-server)
)

:: Start DocumentAssistant API (it manages llama-server lifecycle)
echo Starting DocumentAssistant API...
start /b "" python -m backend.api.server

:: Wait for API
timeout /t 15 /nobreak >nul

:: Start ChatUI
echo Starting ChatUI...
if exist "ChatUI\node_modules" (
    cd ChatUI
    start /b "" npx vite --port 3000
    cd ..
) else (
    echo WARNING: ChatUI not installed. Run setup.bat first.
)

:: Wait and open browser
timeout /t 10 /nobreak >nul
start http://127.0.0.1:3000

echo.
echo === Services Running ===
echo   ChatUI:       http://127.0.0.1:3000
echo   API Backend:  http://127.0.0.1:8080
echo   llama.cpp:    http://127.0.0.1:8081
echo   Health:       http://127.0.0.1:8080/health
echo.
echo Press Ctrl+C to stop
pause
