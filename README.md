# Manga Translator

Automatically translate manga pages — detects text, reads it, translates via a local LLM, and renders the translation back onto the cleaned page.

> ⚠️ **Disclaimer** — This project is fully **vibe-coded** by a non-developer (with AI assistance). It works on my machine with my specific setup. It might break on yours. There are almost certainly bugs, edge cases, and jank. The creator is not responsible for anything that happens as a result of using this software. You've been warned.

> ⚠️ **Prerequisite** — **LM Studio** must be installed, launched, and serving a model on `http://localhost:1234` before running. See [Requirements](#requirements) below.

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

- **LM Studio** — required. Download from [lmstudio.ai](https://lmstudio.ai/), launch it, and go to the **Server** tab → **Start Server**. The app expects it at `http://localhost:1234`.
  - Recommended model: **Gemma 4 12B** (good quality/speed balance for translation).
  - Load the model in LM Studio before running the translator.
- **GPU (optional)** — An NVIDIA GPU with ~4GB+ VRAM accelerates YOLO detection and OCR. The app works on CPU too (slower but functional).
- Linux, Windows, or macOS

## Quick Start

```bash
# One-command launch (auto-installs everything)
bash run.sh
```

Or step by step:

```bash
bash setup.sh     # prompts for GPU/CPU, creates venv, installs deps, downloads models
bash run.sh       # launch the Gradio UI
```

> **Note:** `setup.sh` will ask whether you have an NVIDIA GPU. Choose **Yes** for CUDA acceleration or **No** for CPU-only (slower).

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

All 10 languages can be translated to and from each other in any combination:

- English
- French
- Spanish
- German
- Italian
- Portuguese
- Russian
- Japanese
- Chinese
- Korean

> **Note:** OCR for Japanese uses manga-ocr (specialized for manga). All other languages use EasyOCR.

## Technical Notes

- Japanese OCR uses [manga-ocr](https://github.com/kha-white/manga-ocr) (finetuned on manga)
- Non-Japanese OCR uses [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- Text detection uses [manga-text-detector](https://huggingface.co/calrinkhung/manga-text-detector) (YOLOv8)
- Inpainting uses OpenCV's Telea algorithm by default; set `INPAINT_METHOD = "lama"` in `config.py` to use LaMa
- Translation prompt includes all detected bubbles at once for context

## License

MIT
