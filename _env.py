"""Set all cache directories to project-local paths.
Must be imported before any other module."""
import os
from pathlib import Path

BASE = Path(__file__).parent.resolve()
CACHE = BASE / "cache"

os.environ.setdefault("HF_HOME", str(CACHE / "huggingface"))
os.environ.setdefault("TORCH_HOME", str(CACHE / "torch"))
os.environ.setdefault("EASYOCR_MODULE_PATH", str(CACHE / "easyocr"))
os.environ.setdefault("TRANSFORMERS_CACHE", str(CACHE / "huggingface" / "transformers"))
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(CACHE / "huggingface" / "hub"))

CACHE.mkdir(parents=True, exist_ok=True)
