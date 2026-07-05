import re
import requests
from config import LMSTUDIO_URL, LMSTUDIO_MODEL, LMSTUDIO_TIMEOUT, TRANSLATION_PROMPT


def translate_texts(bubbles, source_lang="Japanese", target_lang="English",
                    url=LMSTUDIO_URL, model=LMSTUDIO_MODEL):
    numbered = "\n".join(
        f"Bubble {i+1}: {b['text']}" for i, b in enumerate(bubbles)
    )
    prompt = TRANSLATION_PROMPT.format(
        source=source_lang, target=target_lang, text=numbered
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a manga translator."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 8192,
        "stream": False,
    }

    try:
        resp = requests.post(url, json=payload, timeout=LMSTUDIO_TIMEOUT)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[translate] API error: {e}")
        return [b["text"] for b in bubbles]

    translations = {}
    pattern = re.compile(r"Bubble\s+(\d+)\s*:\s*(.*?)(?=\n\s*Bubble\s+\d+\s*:|\n*$)", re.DOTALL)
    matches = list(pattern.finditer(content))
    if not matches:
        print(f"[translate] WARNING: no matches found in LLM response")
        return [b["text"] for b in bubbles]
    for match in matches:
        idx = int(match.group(1)) - 1
        text = match.group(2).strip()
        translations[idx] = text

    result = []
    for i, b in enumerate(bubbles):
        if i in translations and translations[i]:
            result.append(translations[i])
        else:
            result.append(b["text"])
    return result
