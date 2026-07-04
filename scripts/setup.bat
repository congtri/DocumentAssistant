@echo off
setlocal

set PROJECT_DIR=%~dp0..
cd /d %PROJECT_DIR%

echo === DocumentAssistant Setup ===
echo.

:: Download llama.cpp if not present
set LLAMA_DIR=%PROJECT_DIR%\third_party\llama_cpp
if not exist "%LLAMA_DIR%\llama-server.exe" (
    if not exist "%LLAMA_DIR%\llama-cli.exe" (
        echo llama.cpp not found. Downloading latest release...

        :: Detect architecture
        if "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
            set ASSET_PATTERN=bin-win-cpu-arm64.zip
        ) else (
            set ASSET_PATTERN=bin-win-cpu-x64.zip
        )

        :: Use PowerShell to fetch latest release and download
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "$release = Invoke-RestMethod 'https://api.github.com/repos/ggml-org/llama.cpp/releases/latest'; " ^
            "$asset = $release.assets | Where-Object { $_.name -like '*%ASSET_PATTERN%' } | Select-Object -First 1; " ^
            "if (-not $asset) { Write-Error 'No matching asset found'; exit 1 }; " ^
            "Write-Host ('Downloading: ' + $asset.name); " ^
            "Invoke-WebRequest -Uri $asset.browser_download_url -OutFile \"$env:TEMP\llama_cpp.zip\"; " ^
            "if (-not (Test-Path '%LLAMA_DIR%')) { New-Item -ItemType Directory -Path '%LLAMA_DIR%' | Out-Null }; " ^
            "Write-Host 'Extracting...'; " ^
            "Expand-Archive -Path \"$env:TEMP\llama_cpp.zip\" -DestinationPath '%LLAMA_DIR%' -Force; " ^
            "Remove-Item \"$env:TEMP\llama_cpp.zip\"; " ^
            "Write-Host 'llama.cpp ready.'"
        if %errorlevel% neq 0 (
            echo ERROR: Failed to download llama.cpp.
            exit /b 1
        )
    )
) else (
    echo llama.cpp already present. Skipping download.
)
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.10+.
    exit /b 1
)

:: Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

:: Create required directories
echo.
echo Creating project directories...
if not exist "documents\source" mkdir "documents\source"
if not exist "data\chunks" mkdir "data\chunks"
if not exist "data\embeddings" mkdir "data\embeddings"
if not exist "data\indexes" mkdir "data\indexes"
if not exist "data\cache" mkdir "data\cache"
if not exist "logs" mkdir "logs"

:: Read model path from config/model.yaml
for /f "delims=" %%i in ('python -c "import yaml; config=yaml.safe_load(open('config/model.yaml')); print(config['model']['path'])"') do set MODEL_PATH=%%i
set MODEL_PATH=%MODEL_PATH:/=\%

if not exist "%MODEL_PATH%" (
    echo.
    echo Configured model not found at: %MODEL_PATH%
    echo Downloading Qwen3.5-4B-Q4_K_M...
    for %%F in ("%MODEL_PATH%") do if not exist "%%~dpF" mkdir "%%~dpF"
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "Invoke-WebRequest -Uri 'https://huggingface.co/Qwen/Qwen3.5-4B-GGUF/resolve/main/qwen3.5-4b-q4_k_m.gguf' -OutFile '%MODEL_PATH%'"
    if %errorlevel% neq 0 (
        echo WARNING: Model download failed. Please download manually.
    ) else (
        echo Model downloaded successfully.
    )
) else (
    echo Model already present at: %MODEL_PATH%. Skipping download.
)

:: Install ChatUI dependencies
echo.
echo Installing ChatUI dependencies...
if exist "ChatUI\package.json" (
    cd ChatUI
    if not exist "node_modules" (
        npm install
    ) else (
        echo ChatUI node_modules already present. Skipping.
    )
    cd ..
) else (
    echo WARNING: ChatUI directory not found. Skipping.
)

echo.
echo === Setup Complete ===
echo.
echo To start: scripts\start.bat
pause
