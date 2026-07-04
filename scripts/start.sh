#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=== DocumentAssistant ==="
echo ""

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "ERROR: Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Find llama-server binary anywhere inside third_party/llama_cpp/
LLAMA_SERVER=$(find third_party/llama_cpp -name "llama-server" -type f 2>/dev/null | head -1)

# Model path from config
MODEL_PATH="models/gguf/Qwen_Qwen3.5-4B-Q4_K_M.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "WARNING: Default model not found at $MODEL_PATH (backend will manage llama-server)"
fi

# Start DocumentAssistant API (it manages llama-server lifecycle)
echo "Starting DocumentAssistant API..."
python -m backend.api.server &
API_PID=$!
echo "API started (PID: $API_PID)"

# Wait for API to be ready
echo "Waiting for API..."
for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
        echo "API is ready!"
        break
    fi
    sleep 1
done

# Start ChatUI
echo "Starting ChatUI..."
if [ -d "ChatUI" ] && [ -d "ChatUI/node_modules" ]; then
    cd ChatUI
    npx vite --port 3000 &
    CHATUI_PID=$!
    cd ..
    echo "ChatUI started (PID: $CHATUI_PID)"
else
    echo "WARNING: ChatUI not installed. Run setup.sh first."
fi

# Wait for ChatUI and open browser
echo "Waiting for ChatUI to start..."
for i in $(seq 1 30); do
    if curl -s -o /dev/null http://localhost:3000 2>/dev/null; then
        echo "ChatUI is ready!"
        # Open default browser (cross-platform)
        if command -v xdg-open > /dev/null 2>&1; then
            xdg-open http://localhost:3000
        elif command -v open > /dev/null 2>&1; then
            open http://localhost:3000
        fi
        break
    fi
    sleep 1
done

echo ""
echo "=== Services Running ==="
echo "  ChatUI:       http://localhost:3000"
echo "  API Backend:  http://127.0.0.1:8080"
echo "  llama.cpp:    http://127.0.0.1:8081"
echo "  Health:       http://127.0.0.1:8080/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle shutdown
cleanup() {
    echo ""
    echo "Shutting down..."
    [ -n "$CHATUI_PID" ] && kill $CHATUI_PID 2>/dev/null
    [ -n "$API_PID" ] && kill $API_PID 2>/dev/null
    echo "Done."
    exit 0
}
trap cleanup SIGINT SIGTERM

wait
