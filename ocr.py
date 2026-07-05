import cv2
from PIL import Image
from manga_ocr import MangaOcr

JP_LANGS = {"ja", "jp", "japanese"}
EASY_LANGS = {
    "zh": ["ch_sim", "ch_tra"],
    "ko": ["ko"],
    "en": ["en"],
    "fr": ["fr"],
    "es": ["es"],
    "de": ["de"],
    "it": ["it"],
    "pt": ["pt"],
    "ru": ["ru"],
}

_mocr = None
_easyocr = None
_easyocr_lang = None


def _is_jp(lang_code):
    return lang_code in JP_LANGS


def load_ocr(lang="ja", device="cuda"):
    global _mocr, _easyocr, _easyocr_lang
    if _is_jp(lang):
        if _mocr is None:
            _mocr = MangaOcr()
        return _mocr
    else:
        codes = EASY_LANGS.get(lang, ["en"])
        if _easyocr is None or _easyocr_lang != lang:
            import easyocr
            _easyocr = easyocr.Reader(codes, gpu=(device == "cuda"))
            _easyocr_lang = lang
        return _easyocr


def ocr_region(image, bbox, reader, lang="ja"):
    x1, y1, x2, y2 = bbox
    roi = image[y1:y2, x1:x2]
    if roi.size == 0:
        return ""
    if _is_jp(lang):
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        roi_pil = Image.fromarray(roi_rgb)
        text = reader(roi_pil)
        return text.strip()
    else:
        results = reader.readtext(roi)
        if results:
            return results[0][1].strip()
        return ""
