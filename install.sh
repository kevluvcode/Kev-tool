#!/usr/bin/env bash
# KevTool installer - Linux / macOS
set -e

cd "$(dirname "$0")"

echo ""
echo "  ============================================"
echo "     KevTool - KevBin Educational Suite"
echo "            Installer v1.1.0"
echo "  ============================================"
echo ""

if command -v python3 >/dev/null 2>&1; then
    PY="python3"
elif command -v python >/dev/null 2>&1; then
    PY="python"
else
    echo "  [X] Python not found. install Python 3.6+ from https://www.python.org/"
    exit 1
fi

echo "  Python found:"
"$PY" --version || true
echo ""

if ! "$PY" -c "import sys; sys.exit(0 if sys.version_info >= (3, 6) else 1)" 2>/dev/null; then
    echo "  [X] Python 3.6 or newer is required."
    exit 1
fi

if ! command -v git >/dev/null 2>&1; then
    echo "  [X] git not found. install it with your package manager (sudo apt install git)"
    exit 1
fi

echo "  installing packages from requirements.txt..."
echo ""

if "$PY" -m pip --version >/dev/null 2>&1; then
    "$PY" -m pip install --user --upgrade pip >/dev/null 2>&1 || true
    "$PY" -m pip install --user -r requirements.txt || "$PY" -m pip install -r requirements.txt
else
    echo "  [X] pip not found. try: sudo apt install python3-pip"
    exit 1
fi

echo ""
echo "  [+pip] done. all packages installed."
echo "  run kevtool with: $PY kevtool.py"
echo ""