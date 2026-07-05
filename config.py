from pathlib import Path

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
FONTS_DIR = BASE_DIR / "fonts"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

MODELS_DIR.mkdir(exist_ok=True)
FONTS_DIR.mkdir(exist_ok=True)
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

INPUT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

LMSTUDIO_URL = "http://localhost:1234/api/v0/chat/completions"
LMSTUDIO_MODEL = "gemma-4-12b-it-qat-unquantized-uncensored-heretic-i1"
LMSTUDIO_TIMEOUT = 120

YOLO_MODEL_PATH = MODELS_DIR / "manga-text-detector.pt"
DETECTION_CONFIDENCE = 0.25
DETECTION_IOU = 0.45

OCR_DEVICE = "cuda"

INPAINT_METHOD = "opencv"
LAMA_MODEL_PATH = MODELS_DIR / "big-lama.pt"
INPAINT_RADIUS = 3

FONT_MIN_SIZE = 6
FONT_MAX_SIZE = 18
FONT_SIZE_STEP = 2
FONT_PATH = FONTS_DIR / "mangati.ttf"
FONT_FALLBACK_PATH = FONTS_DIR / "NotoSans.ttf"
TEXT_PADDING = 4

VERTICAL_ASPECT_THRESHOLD = 1.4

TRANSLATION_PROMPT = """Translate these {source} manga bubbles to {target}. Reply ONLY with:

Bubble 1: <translation>
Bubble 2: <translation>
...

Rules: add implicit subjects, keep SFX as-is, maintain speech level.
No explanations, no notes, no alternatives. Use exactly the format above.

{text}"""

LANGUAGE_MAP = {
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
}

GRADIO_PORT = 7860
GRADIO_SHARE = False
