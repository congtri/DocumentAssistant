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
    echo ERROR: Model not found at %MODEL_PATH%
    exit /b 1
)

:: Find llama-server.exe anywhere inside third_party\llama_cpp\
set LLAMA_SERVER=
for /r "third_party\llama_cpp" %%f in (llama-server.exe) do (
    if not defined LLAMA_SERVER set LLAMA_SERVER=%%f
)
if exist "%LLAMA_SERVER%" (
    echo Starting llama.cpp server...
    start /b "" %LLAMA_SERVER% --model %MODEL_PATH% --host 127.0.0.1 --port 8081 --ctx-size 8192 --n-gpu-layers 99
    timeout /t 10 /nobreak >nul
) else (
    echo WARNING: llama.cpp not found at %LLAMA_SERVER%
)

:: Start DocumentAssistant API
echo Starting DocumentAssistant API...
start /b "" python -m backend.api.server

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
