import random
import requests
from game.strings import t

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


def fetch_card_for_price(exclude_names: set = None, _retries: int = 5) -> dict | None:
    for _ in range(_retries):
        result = _fetch_card_for_price_once(exclude_names)
        if result:
            return result
    return None


def _fetch_card_for_price_once(exclude_names: set = None) -> dict | None:
    try:
        offset = random.randint(0, 10000)
        resp = requests.get(
            BASE_URL,
            params={"num": 20, "offset": offset},
            timeout=5,
        )
        resp.raise_for_status()
        cards = resp.json().get("data", [])

        valid = []
        for card in cards:
            if exclude_names and card["name"] in exclude_names:
                continue
            sets_with_price = [
                s for s in card.get("card_sets", [])
                if float(s.get("set_price") or 0) > 0
            ]
            if not sets_with_price:
                continue
            set_info = random.choice(sets_with_price)
            price = float(set_info["set_price"])
            valid.append((card, price, set_info))

        if not valid:
            return None

        card, price, set_info = random.choice(valid)
        return {
            "name": card["name"],
            "image_url": card["card_images"][0]["image_url"] if card.get("card_images") else "",
            "price": price,
            "set_name": set_info.get("set_name", "Set desconocido"),
            "set_rarity": set_info.get("set_rarity", ""),
        }
    except Exception:
        return None





def fetch_random_card(retries: int = 5) -> dict | None:
    for _ in range(retries):
        result = _fetch_random_card_once()
        if result:
            return result
    return None


def _fetch_random_card_once() -> dict | None:
    monster_type = random.choice(MONSTER_TYPES)
    try:
        offset = random.randint(0, 400)
        resp = requests.get(
            BASE_URL,
            params={"type": monster_type, "num": 100, "offset": offset},
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


def _atk_label(atk, lang: str = "en") -> str:
    if atk in ("N/A", None, "?"):
        return t("atk_unknown", lang)
    val = int(atk)
    if val >= 3000:
        return t("atk_very_high", lang)
    if val >= 2500:
        return t("atk_high", lang)
    if val >= 2000:
        return t("atk_mid_high", lang)
    if val >= 1500:
        return t("atk_mid", lang)
    return t("atk_low", lang)


def _level_label(card: dict, lang: str = "en") -> str:
    level = card["level"]
    if level in ("N/A", None):
        return "N/A"
    val = int(level)
    if card["is_link"]:
        return t("level_link", lang, val=val)
    if card["is_xyz"]:
        key = "level_rank_low" if val <= 4 else "level_rank_mid" if val <= 6 else "level_rank_high"
        return t(key, lang, val=val)
    key = "level_low" if val <= 4 else "level_mid" if val <= 6 else "level_high" if val <= 8 else "level_very_high"
    return t(key, lang, val=val)


def build_hints(card: dict, lang: str = "en") -> list[str]:
    name = card["name"]
    words = name.split()
    letter_count = len(name.replace(" ", "").replace("-", ""))

    if card["is_extra"]:
        card_type = card["type"].replace(" Monster", "")
        hint1 = t("hint1_extra", lang, type=card_type, attr=card["attribute"], race=card["race"])
    else:
        level_val = int(card["level"])
        lr_key = "level_range_low" if level_val <= 4 else "level_range_mid" if level_val <= 6 else "level_range_high"
        hint1 = t("hint1_normal", lang, attr=card["attribute"], race=card["race"], level_range=t(lr_key, lang))

    atk_lbl = _atk_label(card["atk"], lang)
    level_lbl = _level_label(card, lang)
    hint2 = t("hint2", lang, level_label=level_lbl, atk_label=atk_lbl)

    if card["archetype"]:
        hint3 = t("hint3_archetype", lang, archetype=card["archetype"])
    else:
        atk = card["atk"] if card["atk"] not in ("N/A", None) else "?"
        def_ = card["def"] if card["def"] not in ("N/A", None) else "?"
        hint3 = t("hint3_stats", lang, atk=atk, def_=def_)

    n_words = len(words)
    word_str = t("word_singular" if n_words == 1 else "word_plural", lang, n=n_words)
    archetype = card.get("archetype", "")
    arch_in_name = archetype and archetype.lower() in name.lower()

    if arch_in_name:
        arch_idx = name.lower().find(archetype.lower())
        suffix = name[arch_idx + len(archetype):].strip(" -").strip()
        if suffix:
            hint4 = t("hint4_unique", lang, word_str=word_str, letters=letter_count, char=suffix[0].upper())
            frag = suffix[:max(3, len(suffix) // 2)] + "..."
            hint5 = t("hint5_unique", lang, frag=frag)
        else:
            hint4 = t("hint4_full", lang, char=name[0].upper(), word_str=word_str, letters=letter_count)
            hint5 = t("hint5_full", lang, frag=name[:max(4, len(name) // 3)] + "...")
    else:
        hint4 = t("hint4_full", lang, char=name[0].upper(), word_str=word_str, letters=letter_count)
        hint5 = t("hint5_full", lang, frag=name[:max(4, len(name) // 3)] + "...")

    return [hint1, hint2, hint3, hint4, hint5]
