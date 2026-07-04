#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=== DocumentAssistant Setup ==="
echo ""

# Download llama.cpp if not present
LLAMA_DIR="third_party/llama_cpp"
if [ ! -f "$LLAMA_DIR/llama-server" ] && [ ! -f "$LLAMA_DIR/llama-cli" ]; then
    echo "llama.cpp not found. Downloading latest release..."

    OS=$(uname -s)
    ARCH=$(uname -m)

    if [ "$OS" = "Darwin" ]; then
        if [ "$ARCH" = "arm64" ]; then
            ASSET_PATTERN="bin-macos-arm64.tar.gz"
        else
            ASSET_PATTERN="bin-macos-x64.tar.gz"
        fi
    elif [ "$OS" = "Linux" ]; then
        if [ "$ARCH" = "aarch64" ]; then
            ASSET_PATTERN="bin-ubuntu-arm64.tar.gz"
        else
            ASSET_PATTERN="bin-ubuntu-x64.tar.gz"
        fi
    else
        echo "ERROR: Unsupported OS: $OS"
        exit 1
    fi

    RELEASE_JSON=$(curl -fsSL "https://api.github.com/repos/ggml-org/llama.cpp/releases/latest")
    DOWNLOAD_URL=$(echo "$RELEASE_JSON" | python3 -c "
import sys, json
assets = json.load(sys.stdin)['assets']
pattern = '$ASSET_PATTERN'
match = next((a['browser_download_url'] for a in assets if a['name'].endswith(pattern)), None)
print(match or '')
")

    if [ -z "$DOWNLOAD_URL" ]; then
        echo "ERROR: Could not find llama.cpp asset for $OS/$ARCH"
        exit 1
    fi

    FILENAME=$(basename "$DOWNLOAD_URL")
    echo "Downloading: $FILENAME"
    curl -fsSL -o "/tmp/$FILENAME" "$DOWNLOAD_URL"

    echo "Extracting to $LLAMA_DIR..."
    mkdir -p "$LLAMA_DIR"
    tar -xzf "/tmp/$FILENAME" -C "$LLAMA_DIR" --strip-components=1
    rm "/tmp/$FILENAME"
    echo "llama.cpp ready."
else
    echo "llama.cpp already present. Skipping download."
fi
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.10+."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate
echo "Virtual environment activated"

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create required directories
echo ""
echo "Creating project directories..."
mkdir -p documents/source
mkdir -p data/chunks
mkdir -p data/embeddings
mkdir -p data/indexes
mkdir -p data/cache
mkdir -p logs

# Download model if not present
MODEL_DIR="models/gguf"
MODEL_PATH="$MODEL_DIR/Qwen_Qwen3.5-4B-Q4_K_M.gguf"
if [ ! -f "$MODEL_PATH" ]; then
    echo ""
    echo "Downloading default model (Qwen3.5-4B-Q4_K_M)..."
    mkdir -p "$MODEL_DIR"
    MODEL_URL="https://huggingface.co/Qwen/Qwen3.5-4B-GGUF/resolve/main/qwen3.5-4b-q4_k_m.gguf"
    curl -fSL -o "$MODEL_PATH" "$MODEL_URL"
    if [ $? -eq 0 ]; then
        echo "Model downloaded successfully."
    else
        echo "WARNING: Model download failed. Please download manually:"
        echo "  $MODEL_URL -> $MODEL_PATH"
    fi
else
    echo "Model already present. Skipping download."
fi

# Install ChatUI dependencies
echo ""
echo "Installing ChatUI dependencies..."
if [ -d "ChatUI" ]; then
    cd ChatUI
    if [ ! -d "node_modules" ]; then
        npm install
    else
        echo "ChatUI node_modules already present. Skipping."
    fi
    cd ..
else
    echo "WARNING: ChatUI directory not found. Skipping."
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the application:"
echo "  ./scripts/start.sh"
