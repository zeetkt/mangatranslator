#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Auto-setup if venv missing
if [ ! -d venv ]; then
    echo "First launch — running setup..."
    bash setup.sh
fi

# Keep everything inside the project folder
export HF_HOME="$PWD/cache/huggingface"
export TORCH_HOME="$PWD/cache/torch"
export EASYOCR_MODULE_PATH="$PWD/cache/easyocr"
export TRANSFORMERS_CACHE="$PWD/cache/huggingface/transformers"
export HUGGINGFACE_HUB_CACHE="$PWD/cache/huggingface/hub"

source venv/bin/activate
python app.py "$@"
