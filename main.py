import _env  # must be first — sets local cache paths
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

import torch

from config import (
    YOLO_MODEL_PATH, INPUT_DIR, OUTPUT_DIR, INPUT_EXTENSIONS,
    DETECTION_CONFIDENCE, DETECTION_IOU,
    OCR_DEVICE, INPAINT_METHOD, FONT_PATH, LAMA_MODEL_PATH,
    LANGUAGE_MAP,
)
from detect import load_detector, detect_text_regions, merge_vertical_columns
from direction import detect_direction
from ocr import load_ocr, ocr_region
from translate import translate_texts
from inpaint import inpaint_opencv, inpaint_lama
from render import render_text
from config import BASE_DIR


def merge_text_regions(regions, x_gap=30, y_overlap=0.2):
    vertical = sorted(
        [r for r in regions if r.get("direction") == "vertical"],
        key=lambda r: (-r["bbox"][0], r["bbox"][1])
    )
    others = [r for r in regions if r.get("direction") != "vertical"]
    if not vertical:
        return regions

    groups = []
    used = set()
    for i, a in enumerate(vertical):
        if i in used:
            continue
        ax1, ay1, ax2, ay2 = a["bbox"]
        ah = ay2 - ay1
        group_indices = [i]
        used.add(i)

        for j, b in enumerate(vertical):
            if j in used:
                continue
            bx1, by1, bx2, by2 = b["bbox"]
            gap = abs(ax1 - bx1)
            if gap > x_gap:
                continue
            oy1 = max(ay1, by1)
            oy2 = min(ay2, by2)
            overlap = max(0, oy2 - oy1)
            if overlap / max(ah, 1) > y_overlap or overlap > 30:
                group_indices.append(j)
                used.add(j)
                ax1 = min(ax1, bx1)
                ay1 = min(ay1, by1)
                ax2 = max(ax2, bx2)
                ay2 = max(ay2, by2)
                ah = ay2 - ay1

        groups.append(group_indices)

    merged = []
    for g in groups:
        members = [vertical[i] for i in g]
        members.sort(key=lambda r: (-r["bbox"][0], r["bbox"][1]))

        x1 = min(r["bbox"][0] for r in members)
        y1 = min(r["bbox"][1] for r in members)
        x2 = max(r["bbox"][2] for r in members)
        y2 = max(r["bbox"][3] for r in members)

        bw = x2 - x1
        pad = max(15, (120 - bw) // 2)
        x1 = max(0, x1 - pad)
        x2 = min(members[0].get("_image_w", 2000), x2 + pad)

        combined_text = " ".join(r.get("translated_text") or r.get("text", "") for r in members)
        merged.append({
            "bbox": (int(x1), y1, int(x2), y2),
            "direction": "horizontal",
            "text": members[0].get("text", ""),
            "translated_text": combined_text,
            "merged": True,
        })

    return merged + others


def translate_manga_page(image_path, output_path=None,
                         source_lang="Japanese", target_lang="English"):
    print(f"[main] Loading: {image_path}")
    source_code = LANGUAGE_MAP.get(source_lang, "ja")

    image = cv2.imread(str(image_path))
    if image is None:
        print(f"[main] ERROR: cannot read {image_path}")
        return
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print("[main] Loading YOLO detector...")
    detector = load_detector(YOLO_MODEL_PATH)

    print("[main] Detecting text regions...")
    regions = detect_text_regions(image, detector, conf=DETECTION_CONFIDENCE, iou=DETECTION_IOU)
    print(f"[main] Found {len(regions)} text regions")

    for r in regions:
        r["direction"] = detect_direction(image, r["bbox"])

    regions = merge_vertical_columns(regions, x_gap_threshold=20, y_overlap_ratio=0.25)

    regions.sort(key=lambda r: (-r["bbox"][0], r["bbox"][1]))

    print("[main] Loading OCR...")
    reader = load_ocr(lang=source_code, device=OCR_DEVICE)

    print("[main] Performing OCR...")
    for r in regions:
        text = ocr_region(image, r["bbox"], reader, lang=source_code)
        r["text"] = text
        dir_label = r.get("direction", "?")
        print(f"  [{dir_label}] ({r['bbox']}): {text[:50]}")

    texts = [r.get("text", "") for r in regions if r.get("text")]
    if not texts:
        print("[main] No text found; saving original image")
        if output_path:
            cv2.imwrite(str(output_path), image)
        return

    print("[main] Translating via LM Studio...")
    translations = translate_texts(regions, source_lang=source_lang, target_lang=target_lang)
    for r, t in zip(regions, translations):
        r["translated_text"] = t
        if r.get("text") != t:
            print(f"  {r.get('text', '')[:60]} -> {t}")

    print("[main] Inpainting...")
    if INPAINT_METHOD == "lama":
        inpainted = inpaint_lama(image, regions)
    else:
        inpainted = inpaint_opencv(image, regions)

    for r in regions:
        r["_image_w"] = image.shape[1]

    print("[main] Merging adjacent text regions...")
    render_regions = merge_text_regions(regions, x_gap=80, y_overlap=0.1)

    print("[main] Rendering translated text...")
    inpainted_rgb = cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(inpainted_rgb)
    image_pil = render_text(image_pil, render_regions, font_path=FONT_PATH)

    if output_path is None:
        stem = Path(image_path).stem
        output_path = OUTPUT_DIR / f"{stem}_translated.png"
    image_pil.save(str(output_path))
    print(f"[main] Done! Saved to: {output_path}")

    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def main():
    parser = argparse.ArgumentParser(description="Manga Translator Pipeline")
    parser.add_argument("input", nargs="?", default=None,
                        help="Path to image or input directory (default: input/)")
    parser.add_argument("-o", "--output", help="Output path (single image mode)")
    parser.add_argument("--source-lang", default="Japanese",
                        choices=list(LANGUAGE_MAP.keys()),
                        help="Source language (default: Japanese)")
    parser.add_argument("--target-lang", default="English",
                        choices=list(LANGUAGE_MAP.keys()),
                        help="Target language (default: English)")
    args = parser.parse_args()

    def process_one(path, out_path):
        translate_manga_page(path, out_path,
                             source_lang=args.source_lang,
                             target_lang=args.target_lang)

    if args.input is None:
        paths = sorted(p for p in INPUT_DIR.iterdir() if p.suffix.lower() in INPUT_EXTENSIONS)
        if not paths:
            print(f"[main] No images found in {INPUT_DIR}/")
            return
    elif Path(args.input).is_dir():
        paths = sorted(p for p in Path(args.input).iterdir() if p.suffix.lower() in INPUT_EXTENSIONS)
        if not paths:
            print(f"[main] No images found in {args.input}")
            return
    else:
        process_one(args.input, args.output)
        return

    total = len(paths)
    for i, img_path in enumerate(paths, 1):
        print(f"\n{'='*60}")
        print(f"[main] Page {i}/{total}: {img_path.name}")
        print(f"{'='*60}")
        out = OUTPUT_DIR / f"{img_path.stem}_translated.png"
        process_one(img_path, out)


if __name__ == "__main__":
    main()
