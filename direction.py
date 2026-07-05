import cv2
import numpy as np
from config import VERTICAL_ASPECT_THRESHOLD


def detect_direction(image, bbox, vertical_threshold=VERTICAL_ASPECT_THRESHOLD):
    x1, y1, x2, y2 = bbox
    bw, bh = x2 - x1, y2 - y1
    aspect_ratio = bh / max(bw, 1)

    if aspect_ratio > vertical_threshold:
        return "vertical"

    if bw > bh * 1.2:
        return "horizontal"

    roi = image[y1:y2, x1:x2]
    if roi.size == 0:
        return "horizontal"

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    text_pixels = cv2.findNonZero(255 - binary)
    if text_pixels is None:
        return "horizontal"

    pixels = text_pixels.reshape(-1, 2)
    if len(pixels) < 10:
        return "horizontal"

    mean_x = np.mean(pixels[:, 0])
    mean_y = np.mean(pixels[:, 1])
    dx = pixels[:, 0] - mean_x
    dy = pixels[:, 1] - mean_y
    cov = np.cov(dx, dy)
    if np.trace(cov) == 0:
        return "horizontal"
    eigvals, eigvecs = np.linalg.eig(cov)
    major_axis = eigvecs[:, np.argmax(eigvals)]
    angle = np.degrees(np.arctan2(major_axis[1], major_axis[0]))

    if abs(angle) > 60 and aspect_ratio > 1.0:
        return "vertical"
    return "horizontal"
