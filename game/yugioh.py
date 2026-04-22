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
        card = random.choice(cards)
        return _normalize(card)
    except requests.RequestException:
        return None


def _normalize(card: dict) -> dict:
    level_key = "linkval" if card.get("linkval") else "level"
    level_label = "Link" if card.get("linkval") else "Nivel/Rango"
    return {
        "name": card["name"],
        "type": card["type"],
        "attribute": card.get("attribute", "N/A"),
        "level_label": level_label,
        "level": card.get(level_key, "N/A"),
        "race": card.get("race", "N/A"),
        "atk": card.get("atk", "N/A"),
        "def": card.get("def", "N/A"),
        "desc": card.get("desc", "Sin descripción."),
        "image_url": card["card_images"][0]["image_url"] if card.get("card_images") else "",
    }


def build_hints(card: dict) -> list[str]:
    return [
        f"🃏 Tipo de carta: **{card['type']}**",
        f"✨ Atributo: **{card['attribute']}**",
        f"⭐ {card['level_label']}: **{card['level']}**",
        f"🐉 Tipo: **{card['race']}**",
        f"⚔️ ATK: **{card['atk']}** / DEF: **{card['def']}**",
    ]
