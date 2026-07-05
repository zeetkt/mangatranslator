#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "========================================"
echo "  Manga Translator - Setup"
echo "========================================"

# ---- Check Python ----
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" 2>/dev/null; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.10+ required. Install it from https://python.org"
    exit 1
fi
echo " Python: $($PYTHON --version)"

# ---- Create venv ----
if [ ! -d venv ]; then
    echo " Creating virtual environment..."
    $PYTHON -m venv venv
fi

# ---- Activate & upgrade pip ----
source venv/bin/activate
pip install --upgrade pip -q

# ---- Install dependencies ----
echo " Installing dependencies (this may take a while)..."
pip install -r requirements.txt -q

# ---- Patch manga-ocr ----
echo " Patching manga-ocr for compatibility..."
$PYTHON patch_manga_ocr.py

# ---- Create dirs ----
mkdir -p input output models fonts cache

# ---- Download YOLO model ----
MODEL_URL="https://huggingface.co/ogkalu/manga-text-detector-yolov8s/resolve/main/manga-text-detector.pt"
if [ ! -f models/manga-text-detector.pt ]; then
    echo " Downloading YOLO text detector..."
    if command -v wget &>/dev/null; then
        wget -q --show-progress "$MODEL_URL" -O models/manga-text-detector.pt
    elif command -v curl &>/dev/null; then
        curl -#L "$MODEL_URL" -o models/manga-text-detector.pt
    else
        echo " WARNING: wget/curl not found. YOLO model will download on first run."
    fi
fi

# ---- Download fonts ----
FONT_URLS=(
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
)
if [ ! -f fonts/NotoSans.ttf ]; then
    echo " Downloading NotoSans font..."
    if command -v wget &>/dev/null; then
        wget -q --show-progress "${FONT_URLS[0]}" -O fonts/NotoSans.ttf
    elif command -v curl &>/dev/null; then
        curl -#L "${FONT_URLS[0]}" -o fonts/NotoSans.ttf
    fi
fi

echo ""
echo " Setup complete! Run ./run.sh to start."
echo "========================================"
