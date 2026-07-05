import numpy as np
from pathlib import Path
from ultralytics import YOLO

_detector = None


def load_detector(model_path):
    global _detector
    if _detector is not None:
        return _detector
    path = Path(model_path)
    if not path.exists():
        model_id = "ogkalu/manga-text-detector-yolov8s"
        print(f"[detect] Model not found, downloading {model_id}...")
        _detector = YOLO(model_id)
    else:
        _detector = YOLO(str(path))
    return _detector


def _iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    xi1 = max(ax1, bx1)
    yi1 = max(ay1, by1)
    xi2 = min(ax2, bx2)
    yi2 = min(ay2, by2)
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter
    return inter / max(union, 1)


def _nms(regions, iou_threshold=0.5):
    regions = sorted(regions, key=lambda r: r["confidence"], reverse=True)
    kept = []
    while regions:
        best = regions.pop(0)
        kept.append(best)
        regions = [
            r for r in regions
            if _iou(best["bbox"], r["bbox"]) < iou_threshold
        ]
    return kept


def _merge_vertical_columns(regions, x_gap_threshold=15, y_overlap_ratio=0.3):
    vertical = [r for r in regions if r.get("direction") == "vertical"]
    other = [r for r in regions if r.get("direction") != "vertical"]
    if not vertical:
        return regions

    vertical.sort(key=lambda r: r["bbox"][0])
    merged = []
    used = set()
    for i, a in enumerate(vertical):
        if i in used:
            continue
        ax1, ay1, ax2, ay2 = a["bbox"]
        ah = ay2 - ay1
        group = [a]
        used.add(i)
        for j, b in enumerate(vertical):
            if j in used:
                continue
            bx1, by1, bx2, by2 = b["bbox"]
            gap = bx1 - ax2
            if gap < 0 or gap > x_gap_threshold:
                continue
            oy1 = max(ay1, by1)
            oy2 = min(ay2, by2)
            overlap = max(0, oy2 - oy1)
            if overlap / max(ah, 1) > y_overlap_ratio:
                group.append(b)
                used.add(j)
                ax2 = max(ax2, bx2)
                ay1 = min(ay1, by1)
                ay2 = max(ay2, by2)
        if group:
            conf = max(g["confidence"] for g in group)
            merged.append({
                "bbox": (ax1, ay1, ax2, ay2),
                "confidence": conf,
                "direction": "vertical",
                "merged": len(group) > 1,
            })
    return merged + other


def detect_text_regions(image, model, conf=0.15, iou=0.45):
    h, w = image.shape[:2]
    imgsz = max(640, min(max(h, w), 1280))
    results = model(image, conf=conf, iou=iou, imgsz=imgsz, verbose=False)
    regions = []
    for result in results:
        if result.boxes is None:
            print(f"[detect] WARNING: no boxes in YOLO result (conf={conf})")
            continue
        boxes = result.boxes
        print(f"[detect] YOLO raw: {len(boxes)} boxes at conf={conf}")
        for box in boxes:
            conf_val = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)
            if x2 - x1 < 10 or y2 - y1 < 10:
                continue
            regions.append({
                "bbox": (x1, y1, x2, y2),
                "confidence": conf_val,
            })
    print(f"[detect] After filtering: {len(regions)} regions")
    kept = _nms(regions, iou_threshold=0.5)
    print(f"[detect] After NMS: {len(kept)} regions")
    return kept


def merge_vertical_columns(regions, x_gap_threshold=15, y_overlap_ratio=0.3):
    vertical = [r for r in regions if r.get("direction") == "vertical"]
    other = [r for r in regions if r.get("direction") != "vertical"]
    if not vertical:
        return regions

    vertical.sort(key=lambda r: r["bbox"][0])
    merged = []
    used = set()
    for i, a in enumerate(vertical):
        if i in used:
            continue
        ax1, ay1, ax2, ay2 = a["bbox"]
        ah = ay2 - ay1
        group = [a]
        used.add(i)
        for j, b in enumerate(vertical):
            if j in used:
                continue
            bx1, by1, bx2, by2 = b["bbox"]
            gap = bx1 - ax2
            if gap < 0 or gap > x_gap_threshold:
                continue
            oy1 = max(ay1, by1)
            oy2 = min(ay2, by2)
            overlap = max(0, oy2 - oy1)
            if overlap / max(ah, 1) > y_overlap_ratio:
                group.append(b)
                used.add(j)
                ax2 = max(ax2, bx2)
                ay1 = min(ay1, by1)
                ay2 = max(ay2, by2)
        if group:
            conf = max(g["confidence"] for g in group)
            merged.append({
                "bbox": (ax1, ay1, ax2, ay2),
                "confidence": conf,
                "direction": "vertical",
                "merged": len(group) > 1,
            })
    return merged + other
