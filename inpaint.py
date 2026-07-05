import cv2
import numpy as np
import torch
from config import INPAINT_RADIUS, LAMA_MODEL_PATH


def inpaint_opencv(image, regions, radius=INPAINT_RADIUS):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for r in regions:
        x1, y1, x2, y2 = r["bbox"]
        pad = 3
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(image.shape[1], x2 + pad)
        y2 = min(image.shape[0], y2 + pad)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)

    return cv2.inpaint(image, mask, radius, cv2.INPAINT_TELEA)


def _make_mask(image, regions, pad=5):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    for r in regions:
        x1, y1, x2, y2 = r["bbox"]
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(image.shape[1], x2 + pad)
        y2 = min(image.shape[0], y2 + pad)
        cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    return mask


def _load_lama_model(device):
    if not LAMA_MODEL_PATH.exists():
        url = "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt"
        print(f"[inpaint] Downloading LaMa model from {url}...")
        import urllib.request
        urllib.request.urlretrieve(url, LAMA_MODEL_PATH)
        print("[inpaint] LaMa model downloaded")

    print("[inpaint] Loading LaMa model...")
    model = torch.jit.load(LAMA_MODEL_PATH, map_location="cpu").to(device)
    model.eval()
    return model


def inpaint_lama(image_bgr, regions):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = _load_lama_model(device)

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = image_rgb.shape[:2]
    h_8 = (8 - h % 8) % 8
    w_8 = (8 - w % 8) % 8

    img_pad = cv2.copyMakeBorder(image_rgb, 0, h_8, 0, w_8, cv2.BORDER_REFLECT)

    mask = _make_mask(image_bgr, regions)
    msk_pad = cv2.copyMakeBorder(mask, 0, h_8, 0, w_8, cv2.BORDER_CONSTANT, value=0)

    img_norm = img_pad.astype(np.float32) / 255.0
    img_norm = (img_norm - 0.5) / 0.5

    msk_norm = msk_pad.astype(np.float32) / 255.0
    msk_norm = (msk_norm > 0).astype(np.float32)

    img_t = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).float().to(device)
    msk_t = torch.from_numpy(msk_norm).unsqueeze(0).unsqueeze(0).float().to(device)

    with torch.no_grad():
        result = model(img_t, msk_t)

    result = result[0].permute(1, 2, 0).cpu().numpy()
    result = result * 0.5 + 0.5
    result = np.clip(result * 255, 0, 255).astype(np.uint8)
    result = result[:h, :w]
    result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)

    msk_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(np.float32) / 255.0
    final = (image_bgr.astype(np.float32) * (1 - msk_3ch) + result_bgr.astype(np.float32) * msk_3ch)
    return final.astype(np.uint8)
