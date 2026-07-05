"""Patch manga-ocr for transformers>=5.x compatibility."""
import pathlib

# Find the installed manga_ocr package
try:
    import manga_ocr
except ImportError:
    print("manga-ocr not installed, skipping patch")
    exit(0)

ocr_path = pathlib.Path(manga_ocr.__file__).parent / "ocr.py"
if not ocr_path.exists():
    print(f"Could not find {ocr_path}, skipping patch")
    exit(0)

content = ocr_path.read_text(encoding="utf-8")

if "BertJapaneseTokenizer" in content:
    print("manga-ocr already patched")
    exit(0)

content = content.replace(
    "from transformers import ViTImageProcessor, AutoTokenizer, VisionEncoderDecoderModel, GenerationMixin",
    "from transformers import ViTImageProcessor, BertJapaneseTokenizer, VisionEncoderDecoderModel, GenerationMixin",
)
content = content.replace(
    "self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path)",
    "self.tokenizer = BertJapaneseTokenizer.from_pretrained(pretrained_model_name_or_path)",
)

ocr_path.write_text(content, encoding="utf-8")
print("manga-ocr patched successfully")
