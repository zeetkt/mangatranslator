# Manga Translator

Automatically translate manga pages — detects text, reads it, translates via a local LLM, and renders the translation back onto the cleaned page.

> ⚠️ **Disclaimer** — This project is fully **vibe-coded** by a non-developer (with AI assistance). It works on my machine with my specific setup. It might break on yours. There are almost certainly bugs, edge cases, and jank. The creator is not responsible for anything that happens as a result of using this software. You've been warned.

## Features

- **Text detection** — YOLOv8 model trained on manga, detects both horizontal and vertical text
- **OCR** — manga-ocr for Japanese, EasyOCR for Chinese/Korean/English/French/Spanish/German/Italian/Portuguese/Russian
- **Translation** — runs through LM Studio (local), page-level context for better flow
- **Inpainting** — removes original text with OpenCV Telea (LaMa also available)
- **Text rendering** — auto font sizing, white stroke for readability, respects bubble boundaries
- **GUI** — Gradio web UI with file upload, language selection, before/after gallery
- **Batch mode** — process an entire chapter at once via CLI
- **Self-contained** — all models and caches stay inside the project directory

## Requirements

- **LM Studio** running at `http://localhost:1234` with a model loaded (tested with Gemma 4 12B)
- **NVIDIA GPU** with ~4GB+ VRAM (CUDA) — CPU mode is possible but slow
- Linux, Windows, or macOS

## Quick Start

```bash
# One-command launch (auto-installs everything)
bash run.sh
```

Or step by step:

```bash
bash setup.sh     # create venv, install deps, download models
bash run.sh       # launch the Gradio UI
```

On Windows, double-click `run.bat`.

## Usage

### Web UI (recommended)

```bash
bash run.sh
```

Opens at `http://localhost:7860`. Upload a page, pick source/target languages, click Translate.

### CLI

```bash
# Single page
python main.py input/page.webp -o output/page.png

# Batch (all images in input/)
python main.py

# With language options
python main.py --source-lang Japanese --target-lang English input/page.webp
```

## Project Structure

```
mangatranslator/
├── app.py          Gradio web UI
├── main.py         Pipeline orchestrator
├── config.py       Settings
├── detect.py       YOLO text detection
├── direction.py    Text direction classifier
├── ocr.py          OCR (manga-ocr / EasyOCR)
├── translate.py    LM Studio API calls
├── inpaint.py      Text removal (OpenCV / LaMa)
├── render.py       Text rendering
├── _env.py         Local cache paths
├── setup.sh        One-click installer
├── run.sh          One-click launcher
├── input/          Drop manga pages here
├── output/         Translated pages appear here
├── cache/          Models, tokenizers, etc.
└── fonts/          Auto-downloaded fonts
```

## Supported Languages

| Source | Target |
|--------|--------|
| Japanese | English, French, Spanish, German, Italian, Portuguese, Russian, Chinese, Korean |
| Chinese  | English, French, Spanish, German, Italian, Portuguese, Russian, Japanese, Korean |
| Korean   | English, French, Spanish, German, Italian, Portuguese, Russian, Japanese, Chinese |
| English  | French, Spanish, German, Italian, Portuguese, Russian, Japanese, Chinese, Korean |
| French   | English, Spanish, German, Italian, Portuguese, Russian, Japanese, Chinese, Korean |
| Spanish  | English, French, German, Italian, Portuguese, Russian, Japanese, Chinese, Korean |
| German   | English, French, Spanish, Italian, Portuguese, Russian, Japanese, Chinese, Korean |
| Italian  | English, French, Spanish, German, Portuguese, Russian, Japanese, Chinese, Korean |
| Portuguese | English, French, Spanish, German, Italian, Russian, Japanese, Chinese, Korean |
| Russian  | English, French, Spanish, German, Italian, Portuguese, Japanese, Chinese, Korean |

## Technical Notes

- Japanese OCR uses [manga-ocr](https://github.com/kha-white/manga-ocr) (finetuned on manga)
- Non-Japanese OCR uses [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- Text detection uses [manga-text-detector](https://huggingface.co/calrinkhung/manga-text-detector) (YOLOv8)
- Inpainting uses OpenCV's Telea algorithm by default; set `INPAINT_METHOD = "lama"` in `config.py` to use LaMa
- Translation prompt includes all detected bubbles at once for context

## License

MIT
