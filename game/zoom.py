import io
import requests
from PIL import Image

# Cada nivel define qué fracción de la carta es visible (0.15 = 15% del área)
ZOOM_LEVELS = [0.15, 0.30, 0.55]
OUTPUT_SIZE = (400, 400)


def get_zoomed_image(image_url: str, zoom_level: int) -> io.BytesIO | None:
    try:
        resp = requests.get(image_url, timeout=5)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    except Exception:
        return None

    fraction = ZOOM_LEVELS[zoom_level]

    if fraction >= 1.0:
        out = io.BytesIO()
        img.resize(OUTPUT_SIZE, Image.LANCZOS).save(out, format="PNG")
        out.seek(0)
        return out

    w, h = img.size
    crop_w = int(w * fraction)
    crop_h = int(h * fraction)

    left = (w - crop_w) // 2
    top = (h - crop_h) // 2
    cropped = img.crop((left, top, left + crop_w, top + crop_h))

    zoomed = cropped.resize(OUTPUT_SIZE, Image.LANCZOS)

    out = io.BytesIO()
    zoomed.save(out, format="PNG")
    out.seek(0)
    return out


MAX_ZOOM_LEVEL = len(ZOOM_LEVELS) - 1


def zoom_score(zoom_level: int) -> int:
    scores = [100, 75, 50]
    return scores[zoom_level] if zoom_level < len(scores) else 0
