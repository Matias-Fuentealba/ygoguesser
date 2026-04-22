import random
import requests

MONSTER_TYPES = [
    "Normal Monster",
    "Effect Monster",
    "Fusion Monster",
    "Ritual Monster",
    "Synchro Monster",
    "XYZ Monster",
    "Link Monster",
]

EXTRA_DECK_TYPES = {"Fusion", "Synchro", "XYZ", "Link"}

BASE_URL = "https://db.ygoprodeck.com/api/v7/cardinfo.php"


def fetch_random_card() -> dict | None:
    monster_type = random.choice(MONSTER_TYPES)
    try:
        resp = requests.get(
            BASE_URL,
            params={"type": monster_type, "num": 100, "offset": 0},
            timeout=5,
        )
        resp.raise_for_status()
        cards = resp.json().get("data", [])
        if not cards:
            return None
        return _normalize(random.choice(cards))
    except requests.RequestException:
        return None


def _normalize(card: dict) -> dict:
    is_link = "Link" in card["type"]
    is_xyz = "XYZ" in card["type"]
    is_extra = any(t in card["type"] for t in EXTRA_DECK_TYPES)

    level_key = "linkval" if is_link else "level"
    level_val = card.get(level_key, "N/A")

    return {
        "name": card["name"],
        "type": card["type"],
        "attribute": card.get("attribute", "N/A"),
        "level": level_val,
        "race": card.get("race", "N/A"),
        "atk": card.get("atk", "N/A"),
        "def": card.get("def", "N/A"),
        "desc": card.get("desc", ""),
        "archetype": card.get("archetype", ""),
        "is_extra": is_extra,
        "is_link": is_link,
        "is_xyz": is_xyz,
        "image_url": card["card_images"][0]["image_url"] if card.get("card_images") else "",
    }


def _atk_label(atk) -> str:
    if atk in ("N/A", None, "?"):
        return "desconocido"
    val = int(atk)
    if val >= 3000:
        return "muy alto (3000+)"
    if val >= 2500:
        return "alto (2500+)"
    if val >= 2000:
        return "medio-alto (2000+)"
    if val >= 1500:
        return "medio (1500+)"
    return "bajo (menos de 1500)"


def _level_label(card: dict) -> str:
    level = card["level"]
    if level in ("N/A", None):
        return "N/A"
    val = int(level)
    if card["is_link"]:
        return f"Link {val}"
    if card["is_xyz"]:
        label = "bajo" if val <= 4 else "medio" if val <= 6 else "alto"
        return f"Rango {label} ({val})"
    label = "bajo" if val <= 4 else "medio" if val <= 6 else "alto" if val <= 8 else "muy alto"
    return f"Nivel {label} ({val}★)"



def build_hints(card: dict) -> list[str]:
    name = card["name"]
    words = name.split()
    letter_count = len(name.replace(" ", "").replace("-", ""))

    # Pista 1 — Compuesta: filtra fuertemente desde el inicio
    if card["is_extra"]:
        card_type = card["type"].replace(" Monster", "")
        hint1 = (
            f"🃏 Es un monstruo **{card_type}**, "
            f"atributo **{card['attribute']}**, "
            f"tipo **{card['race']}**"
        )
    else:
        level_range = (
            "bajo (1–4)" if int(card["level"]) <= 4
            else "medio (5–6)" if int(card["level"]) <= 6
            else "alto (7+)"
        )
        hint1 = (
            f"🃏 Es un monstruo de atributo **{card['attribute']}**, "
            f"tipo **{card['race']}**, "
            f"nivel **{level_range}**"
        )

    # Pista 2 — Estructural: nivel exacto y ATK aproximado
    atk_label = _atk_label(card["atk"])
    level_label = _level_label(card)
    hint2 = f"⚙️ **{level_label}**, ATK **{atk_label}**"

    # Pista 3 — Temática: arquetipo o ATK/DEF exacto si no hay arquetipo
    if card["archetype"]:
        hint3 = f"🎯 Pertenece al arquetipo **{card['archetype']}**"
    else:
        atk = card["atk"] if card["atk"] not in ("N/A", None) else "?"
        def_ = card["def"] if card["def"] not in ("N/A", None) else "?"
        hint3 = f"🎯 ATK exacto: **{atk}** / DEF exacto: **{def_}**"

    # Pista 4 — Nombre: inicial, palabras y longitud
    initial = name[0].upper()
    word_str = f"**{len(words)}** {'palabra' if len(words) == 1 else 'palabras'}"
    hint4 = (
        f"🔤 El nombre empieza con **\"{initial}\"**, "
        f"tiene {word_str} y **{letter_count}** letras (sin espacios ni guiones)"
    )

    # Pista 5 — Fuerte: fragmento del nombre
    fragment = name[:max(4, len(name) // 3)] + "..."
    hint5 = f"💥 El nombre comienza con: **\"{fragment}\"**"

    return [hint1, hint2, hint3, hint4, hint5]
